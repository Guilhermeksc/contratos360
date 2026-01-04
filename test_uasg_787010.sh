#!/bin/bash
# Script para testar a sincronização da UASG 787010 no Docker

echo "=========================================="
echo "Teste de Integração - UASG 787010"
echo "=========================================="
echo ""

# Verifica se os containers estão rodando
echo "1. Verificando se os containers estão rodando..."
if ! docker compose ps | grep -q "licitacao360_backend.*Up"; then
    echo "❌ Container backend não está rodando!"
    echo "Execute: docker compose up -d"
    exit 1
fi
echo "✅ Containers estão rodando"
echo ""

# Executa o teste de integração
echo "2. Executando teste de integração..."
echo ""
docker compose exec backend python manage.py test gestao_contratos.tests_integration.ComprasNetIntegrationTest.test_sync_uasg_787010_and_verify_all_fields --verbosity=2

echo ""
echo "=========================================="
echo "3. Verificando contratos salvos no banco..."
echo "=========================================="
docker compose exec backend python manage.py shell << 'EOF'
from gestao_contratos.models import Contrato, Uasg

uasg_code = '787010'
contratos = Contrato.objects.filter(uasg__uasg_code=uasg_code)

print(f"\nTotal de contratos para UASG {uasg_code}: {contratos.count()}\n")

# Estatísticas
com_valor_global = contratos.exclude(valor_global__isnull=True).count()
sem_valor_global = contratos.filter(valor_global__isnull=True).count()

print(f"Contratos COM valor_global: {com_valor_global}")
print(f"Contratos SEM valor_global: {sem_valor_global}")

if com_valor_global > 0:
    print("\nExemplos de contratos COM valor_global:")
    for c in contratos.exclude(valor_global__isnull=True)[:5]:
        print(f"  - {c.numero or c.id}: R$ {c.valor_global:,.2f}")

if sem_valor_global > 0:
    print("\nExemplos de contratos SEM valor_global:")
    for c in contratos.filter(valor_global__isnull=True)[:5]:
        raw_valor = c.raw_json.get('valor_global') if c.raw_json else None
        print(f"  - {c.numero or c.id}: raw_json.valor_global = {raw_valor}")
EOF

echo ""
echo "=========================================="
echo "Teste concluído!"
echo "=========================================="


