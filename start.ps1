# AI-Driven Customer Feedback Analyzer
# Quick Start Script for Windows

Write-Host "🚀 Starting AI Feedback Analyzer Setup..." -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found or not running!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop and make sure it's running." -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created!" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Please edit .env file and add your API keys:" -ForegroundColor Yellow
    Write-Host "   - OPENAI_API_KEY (required for AI features)" -ForegroundColor Yellow
    Write-Host "   - SECRET_KEY (generate a random string)" -ForegroundColor Yellow
    Write-Host "   - JWT_SECRET_KEY (generate a random string)" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Press Enter to open .env file in notepad, or type 'skip' to continue"
    if ($continue -ne "skip") {
        notepad .env
        Write-Host ""
        Read-Host "Press Enter when you are done editing .env"
    }
}

Write-Host ""
Write-Host "🐳 Starting Docker containers..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check container status
Write-Host ""
Write-Host "📊 Container Status:" -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access your application:" -ForegroundColor Cyan
Write-Host "   Frontend Dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API:        http://localhost:8000" -ForegroundColor White
Write-Host "   API Documentation:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "📚 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host "   2. Register a new account via API docs (http://localhost:8000/docs)" -ForegroundColor White
Write-Host "   3. Login and start analyzing feedback!" -ForegroundColor White
Write-Host ""
Write-Host "🛠️  Useful Commands:" -ForegroundColor Cyan
Write-Host "   View logs:      docker-compose logs -f" -ForegroundColor White
Write-Host "   Stop services:  docker-compose down" -ForegroundColor White
Write-Host "   Restart:        docker-compose restart" -ForegroundColor White
Write-Host ""
Write-Host "📖 For detailed setup guide, see SETUP_GUIDE.md" -ForegroundColor Yellow
Write-Host ""
