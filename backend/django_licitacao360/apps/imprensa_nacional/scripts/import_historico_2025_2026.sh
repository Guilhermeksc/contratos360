#!/bin/bash

# Script para importar dados históricos do INLABS
# Período: 2025-10-09 até 2026-02-07
# 
# Uso:
#   ./import_historico_2025_2026.sh
#   OU
#   bash import_historico_2025_2026.sh
#   OU (do diretório raiz do projeto):
#   docker compose exec backend python manage.py import_inlabs_batch \
#       --start-date 2025-10-09 --end-date 2026-02-07 \
#       --continue-on-error --delay 3

# Encontrar o diretório raiz do projeto (onde está docker-compose.yml)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"

# Verificar se estamos no diretório correto
if [ ! -f "$PROJECT_ROOT/docker-compose.yml" ]; then
    echo "Erro: docker-compose.yml não encontrado."
    echo "Execute este script do diretório raiz do projeto ou de qualquer subdiretório."
    exit 1
fi

echo "=========================================="
echo "Importação Histórica INLABS"
echo "Período: 2025-10-09 até 2026-02-07"
echo "=========================================="
echo ""
echo "Diretório do projeto: $PROJECT_ROOT"
echo ""

cd "$PROJECT_ROOT" || exit 1

docker compose exec backend python manage.py import_inlabs_batch \
    --start-date 2025-10-09 \
    --end-date 2026-02-07 \
    --continue-on-error \
    --delay 3 \
    --skip-existing

echo ""
echo "=========================================="
echo "Importação histórica concluída!"
echo "=========================================="
