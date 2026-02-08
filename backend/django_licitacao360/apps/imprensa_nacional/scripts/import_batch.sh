#!/bin/bash

# Script para importar múltiplas datas do INLABS
# Uso: ./import_batch.sh START_DATE END_DATE [DELAY]

set -e

START_DATE="${1:-2025-10-09}"
END_DATE="${2:-2026-02-07}"
DELAY="${3:-2}"

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Uso: $0 START_DATE END_DATE [DELAY]"
    echo "Exemplo: $0 2025-10-09 2026-02-07 2"
    exit 1
fi

echo "=========================================="
echo "Importação em lote do INLABS"
echo "=========================================="
echo "Data inicial: $START_DATE"
echo "Data final: $END_DATE"
echo "Delay entre importações: ${DELAY}s"
echo "=========================================="
echo ""

# Converter datas para timestamp para calcular diferença
START_TS=$(date -d "$START_DATE" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$START_DATE" +%s 2>/dev/null)
END_TS=$(date -d "$END_DATE" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$END_DATE" +%s 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "Erro: Formato de data inválido. Use YYYY-MM-DD"
    exit 1
fi

CURRENT_DATE="$START_DATE"
SUCCESS=0
ERRORS=0
SKIPPED=0

while [ "$(date -d "$CURRENT_DATE" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$CURRENT_DATE" +%s 2>/dev/null)" -le "$END_TS" ]; do
    echo "[$(date +%H:%M:%S)] Processando $CURRENT_DATE..."
    
    if docker compose exec -T backend python manage.py import_inlabs --date "$CURRENT_DATE" 2>&1; then
        echo "✅ $CURRENT_DATE: Sucesso"
        SUCCESS=$((SUCCESS + 1))
    else
        EXIT_CODE=$?
        if [ $EXIT_CODE -eq 1 ]; then
            # Verificar se é erro de arquivo não disponível
            if docker compose exec -T backend python manage.py import_inlabs --date "$CURRENT_DATE" 2>&1 | grep -q "Nenhum arquivo disponível\|HTTP 404"; then
                echo "⚠️  $CURRENT_DATE: Arquivo não disponível (pulando)"
                SKIPPED=$((SKIPPED + 1))
            else
                echo "❌ $CURRENT_DATE: Erro"
                ERRORS=$((ERRORS + 1))
            fi
        else
            echo "❌ $CURRENT_DATE: Erro (código: $EXIT_CODE)"
            ERRORS=$((ERRORS + 1))
        fi
    fi
    
    # Avançar para próxima data
    CURRENT_DATE=$(date -d "$CURRENT_DATE + 1 day" +%Y-%m-%d 2>/dev/null || date -j -v+1d -f "%Y-%m-%d" "$CURRENT_DATE" +%Y-%m-%d 2>/dev/null)
    
    # Delay entre importações
    if [ "$DELAY" -gt 0 ]; then
        sleep "$DELAY"
    fi
done

echo ""
echo "=========================================="
echo "RESUMO"
echo "=========================================="
echo "✅ Sucessos: $SUCCESS"
echo "⚠️  Puladas: $SKIPPED"
echo "❌ Erros: $ERRORS"
echo "=========================================="
