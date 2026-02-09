#!/bin/bash

echo "🔍 Testando acesso ao Django Admin..."
echo ""

echo "1️⃣ Testando redirecionamento /admin → /admin/"
echo "----------------------------------------"
curl -I http://localhost/admin 2>&1 | grep -E "(HTTP|Location)"
echo ""

echo "2️⃣ Testando acesso /admin/"
echo "----------------------------------------"
curl -I http://localhost/admin/ 2>&1 | grep -E "(HTTP|Location|Content-Type)"
echo ""

echo "3️⃣ Testando página de login"
echo "----------------------------------------"
LOGIN_RESPONSE=$(curl -s http://localhost/admin/login/ 2>&1)
if echo "$LOGIN_RESPONSE" | grep -q "login"; then
    echo "✅ Página de login encontrada"
else
    echo "❌ Página de login NÃO encontrada"
fi
echo ""

echo "4️⃣ Testando arquivos estáticos CSS"
echo "----------------------------------------"
STATIC_TEST=$(curl -I http://localhost/static/admin/css/base.css 2>&1 | grep -E "HTTP")
if echo "$STATIC_TEST" | grep -q "200"; then
    echo "✅ Arquivos estáticos acessíveis"
else
    echo "❌ Arquivos estáticos NÃO acessíveis"
    echo "$STATIC_TEST"
fi
echo ""

echo "5️⃣ Verificando containers"
echo "----------------------------------------"
docker compose ps | grep -E "(nginx|backend)" | grep -E "Up"
echo ""

echo "6️⃣ Testando conectividade backend → nginx"
echo "----------------------------------------"
docker compose exec backend curl -I http://backend:8000/admin/ 2>&1 | grep -E "(HTTP|Location)" | head -3
echo ""

echo "✅ Testes concluídos!"
echo ""
echo "📝 Se todos os testes passaram mas ainda não funciona no navegador:"
echo "   1. Limpe o cache do navegador (Ctrl+Shift+R)"
echo "   2. Abra o DevTools (F12) e verifique erros no Console"
echo "   3. Verifique a aba Network para ver se algum recurso está falhando"
echo "   4. Tente em uma janela anônima/privada"
