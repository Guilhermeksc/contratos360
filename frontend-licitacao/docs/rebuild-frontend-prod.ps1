# Script para rebuild do frontend Angular para PRODUÇÃO
Write-Host "🔨 Fazendo build do Angular para PRODUÇÃO..." -ForegroundColor Cyan
Write-Host "⚠️  Este build usará cemos2028.com como API URL" -ForegroundColor Yellow

# Navega para o diretório do frontend
Set-Location -Path ".\frontend"

# Executa o build em modo produção (usa cemos2028.com)
npm run build:prod

# Verifica se o build foi bem-sucedido
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build de produção concluído com sucesso!" -ForegroundColor Green
    
    # Retorna ao diretório raiz
    Set-Location -Path ".."
    
    # Reinicia o Nginx
    Write-Host "🔄 Reiniciando Nginx..." -ForegroundColor Cyan
    docker compose restart nginx
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Nginx reiniciado com sucesso!" -ForegroundColor Green
        Write-Host "" 
        Write-Host "🌐 Build de produção pronto para deploy!" -ForegroundColor Yellow
        Write-Host "   Certifique-se de que o domínio cemos2028.com está configurado" -ForegroundColor White
    } else {
        Write-Host "❌ Erro ao reiniciar o Nginx" -ForegroundColor Red
        Set-Location -Path ".."
    }
} else {
    Write-Host "❌ Erro no build do Angular" -ForegroundColor Red
    Set-Location -Path ".."
}
