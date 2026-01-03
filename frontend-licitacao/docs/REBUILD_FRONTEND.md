# 🔄 Como Atualizar o Build do Frontend

## ⚠️ IMPORTANTE: Ambiente de Desenvolvimento vs Produção

O Angular tem **dois ambientes de build**:

- **Development** (`npm run build:dev`): Usa `http://localhost:8088/api` para chamadas de API
- **Production** (`npm run build:prod`): Usa `https://cemos2028.com/api` para chamadas de API

**Para desenvolvimento local, SEMPRE use `build:dev`!**

## Problema
Quando você faz alterações no código Angular, o Nginx não reflete as mudanças automaticamente porque ele serve os arquivos da pasta `dist` que foi gerada anteriormente.

## Solução Rápida

### Opção 1: Usar o Script PowerShell (Recomendado para DEV)
Execute o script que faz tudo automaticamente em modo desenvolvimento:

```powershell
.\rebuild-frontend.ps1
```

Para build de produção:
```powershell
.\rebuild-frontend-prod.ps1
```

### Opção 2: Manual - Build de Desenvolvimento
Execute os comandos manualmente:

```powershell
# 1. Entre na pasta do frontend
cd frontend

# 2. Faça o build em modo DESENVOLVIMENTO (usa localhost:8088)
npm run build:dev

# 3. Volte para a raiz
cd ..

# 4. Reinicie o Nginx
docker compose restart nginx
```

### Opção 3: Manual - Build de Produção
```powershell
cd frontend
npm run build:prod  # Usa cemos2028.com
cd ..
docker compose restart nginx
```

## Como Funciona

1. **Build Local**: O Angular é compilado localmente no Windows usando `npm run build`
2. **Saída**: Os arquivos são gerados em `frontend/dist/frontend/browser/`
3. **Docker Volume**: O Nginx acessa esses arquivos via volume mount
4. **Restart**: O Nginx precisa ser reiniciado para recarregar os arquivos

## Desenvolvimento com Hot Reload

Para desenvolvimento ativo, recomendo rodar o Angular localmente:

```powershell
cd frontend
npm start
```

Isso abrirá em `http://localhost:4200` com hot reload automático.

## Verificar Build Atual

Para ver a data da última modificação dos arquivos do build:

```powershell
Get-ChildItem .\frontend\dist\frontend\browser\ | Select-Object Name, LastWriteTime
```

## Troubleshooting

### O Nginx não está carregando os novos arquivos
```powershell
# Pare e inicie novamente o Nginx
docker compose stop nginx
docker compose start nginx
```

### Limpar cache do build
```powershell
cd frontend
Remove-Item -Recurse -Force dist, .angular
npm run build
cd ..
docker compose restart nginx
```

### Verificar logs do Nginx
```powershell
docker compose logs nginx --tail=50
```
