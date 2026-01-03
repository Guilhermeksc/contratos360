# Script para rebuild do frontend Angular
Write-Host "🔨 Fazendo build do Angular para DESENVOLVIMENTO..." -ForegroundColor Cyan

# Navega para o diretório do frontend
Set-Location -Path ".\frontend"

# Executa o build em modo desenvolvimento (usa localhost:8088)
npm run build:dev

# Verifica se o build foi bem-sucedido
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build concluído com sucesso!" -ForegroundColor Green
    
    # Retorna ao diretório raiz
    Set-Location -Path ".."
    
    # Reinicia o Nginx
    Write-Host "🔄 Reiniciando Nginx..." -ForegroundColor Cyan
    docker compose restart nginx
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Nginx reiniciado com sucesso!" -ForegroundColor Green
        Write-Host "" 
        Write-Host "🌐 Acesse a aplicação em:" -ForegroundColor Yellow
        Write-Host "   http://localhost:8088" -ForegroundColor White
        Write-Host "   http://localhost:8088/admin" -ForegroundColor White
    } else {
        Write-Host "❌ Erro ao reiniciar o Nginx" -ForegroundColor Red
        Set-Location -Path ".."
    }
} else {
    Write-Host "❌ Erro no build do Angular" -ForegroundColor Red
    Set-Location -Path ".."
}
