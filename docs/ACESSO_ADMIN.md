# Como Acessar o Admin do Django

## ⚠️ Problema Identificado e Resolvido

O app `gestao_contratos` não estava no `INSTALLED_APPS` do `settings.py`. Isso foi corrigido.

## 🔧 Como Acessar o Admin

### ❌ ERRADO (não funciona)
```
http://127.0.0.1:8000/admin
```
**Motivo:** A porta 8000 é interna do Docker. O Django não está exposto diretamente na porta 8000 do host.

### ✅ CORRETO (use uma dessas opções)

#### Opção 1: Via Nginx (porta 80)
```
http://localhost/admin
ou
http://127.0.0.1/admin
```

#### Opção 2: Via Nginx (porta 8088)
```
http://localhost:8088/admin
ou
http://127.0.0.1:8088/admin
```

## 🔍 Verificação

Para verificar se está funcionando:

```bash
# Verificar se o nginx está respondendo
curl -I http://localhost/admin/

# Deve retornar HTTP 302 (redirecionamento para login)
```

## 📝 Credenciais do Admin

As credenciais padrão são:
- **Usuário:** `admin`
- **Senha:** `@cemos2028`

(Definidas no docker-compose.yml)

## 🐛 Troubleshooting

### Se ainda não funcionar:

1. **Verificar se os containers estão rodando:**
   ```bash
   docker compose ps
   ```

2. **Ver logs do backend:**
   ```bash
   docker compose logs backend --tail 50
   ```

3. **Ver logs do nginx:**
   ```bash
   docker compose logs nginx --tail 50
   ```

4. **Reiniciar todos os serviços:**
   ```bash
   docker compose restart
   ```

5. **Verificar se o app está instalado:**
   ```bash
   docker compose exec backend python manage.py shell
   >>> from django.apps import apps
   >>> 'gestao_contratos' in [app.name for app in apps.get_app_configs()]
   True
   ```

## 📚 Arquitetura

```
Cliente (navegador)
    ↓
Nginx (porta 80 ou 8088) ← Acesse aqui!
    ↓
Django Backend (porta 8000 interna) ← Não acesse diretamente
    ↓
PostgreSQL (porta 5432 interna)
```

O nginx atua como **proxy reverso**, então você sempre deve acessar através dele, não diretamente no backend.

