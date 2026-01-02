# Script para iniciar servidor de mídias local

# Configuração
$MEDIA_PATH = "C:\Users\guilh\projeto\www\midias"
$PORT = 8089

# Banner
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "   SERVIDOR DE MÍDIAS LOCAL    " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se o diretório existe
if (-not (Test-Path $MEDIA_PATH)) {
    Write-Host "❌ Diretório não encontrado: $MEDIA_PATH" -ForegroundColor Red
    Write-Host "   Crie o diretório ou atualize a variável MEDIA_PATH" -ForegroundColor Yellow
    exit 1
}

# Verificar se http-server está instalado
Write-Host "🔍 Verificando http-server..." -ForegroundColor Yellow
$httpServerInstalled = Get-Command http-server -ErrorAction SilentlyContinue

if (-not $httpServerInstalled) {
    Write-Host "❌ http-server não encontrado" -ForegroundColor Red
    Write-Host "📦 Instalando http-server globalmente..." -ForegroundColor Yellow
    npm install -g http-server
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao instalar http-server" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ http-server instalado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "✅ http-server encontrado" -ForegroundColor Green
}

# Ir para o diretório de mídias
Set-Location $MEDIA_PATH

# Exibir informações
Write-Host ""
Write-Host "📁 Diretório: $MEDIA_PATH" -ForegroundColor Cyan
Write-Host "🌐 URL: http://localhost:$PORT" -ForegroundColor Green
Write-Host "🔓 CORS: Habilitado" -ForegroundColor Green
Write-Host "⏹️  Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""
Write-Host "Exemplos de URLs:" -ForegroundColor Cyan
Write-Host "  http://localhost:$PORT/geopolitica/vinganca-geografia/video/capX.mp4" -ForegroundColor Gray
Write-Host "  http://localhost:$PORT/geopolitica/vinganca-geografia/audio/podcast_capX.mp3" -ForegroundColor Gray
Write-Host ""

# Iniciar servidor
http-server -p $PORT --cors -c-1 -o

