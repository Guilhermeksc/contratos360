#!/bin/bash
# Script para criar arquivo .env baseado no env.example

if [ -f .env ]; then
    echo "⚠️  Arquivo .env já existe. Fazendo backup..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
fi

# Gerar SECRET_KEY
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")

# Copiar template e substituir SECRET_KEY
cp env.example .env
sed -i "s|sua-chave-secreta-super-segura-aqui-gerada-aleatoriamente|${SECRET_KEY}|g" .env

echo "✅ Arquivo .env criado com sucesso!"
echo "📝 Por favor, revise o arquivo .env e ajuste as configurações conforme necessário:"
echo "   - POSTGRES_PASSWORD"
echo "   - FLOWER_PASSWORD"
echo "   - DJANGO_SUPERUSER_PASSWORD"
echo "   - ALLOWED_HOSTS"

