# SmartFit Automated Setup Script for Windows (PowerShell)
$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting SmartFit Full System Setup..." -ForegroundColor Cyan

# PostgreSQL credentials
$env:PGUSER = if ($env:PGUSER) { $env:PGUSER } else { "postgres" }

# 1. Database Setup
Write-Host "`n🐘 Checking & Creating PostgreSQL Databases..." -ForegroundColor Yellow
try {
    psql -U $env:PGUSER -c 'CREATE DATABASE "SmartFit_db";' 2>$null
    Write-Host "  ✅ Database SmartFit_db ready." -ForegroundColor Green
} catch {
    Write-Host "  ℹ️ SmartFit_db ready or postgres CLI bypassed." -ForegroundColor Gray
}

try {
    psql -U $env:PGUSER -c 'CREATE DATABASE "SmartFit_Test_db";' 2>$null
    Write-Host "  ✅ Database SmartFit_Test_db ready." -ForegroundColor Green
} catch {
    Write-Host "  ℹ️ SmartFit_Test_db ready or postgres CLI bypassed." -ForegroundColor Gray
}

# 2. Backend Setup
Write-Host "`n⚙️ Setting up Backend..." -ForegroundColor Yellow
Set-Location backend

if (-not (Test-Path ".venv")) {
    Write-Host "  📦 Creating Python virtual environment (.venv)..." -ForegroundColor Blue
    python -m venv .venv
}

Write-Host "  🔌 Activating virtual environment..." -ForegroundColor Blue
& .\.venv\Scripts\Activate.ps1

Write-Host "  📥 Installing Python dependencies..." -ForegroundColor Blue
pip install -r requirements.txt --quiet

if (-not (Test-Path ".env")) {
    Write-Host "  📄 Copying .env.example to .env..." -ForegroundColor Blue
    Copy-Item .env.example .env
}

Write-Host "  🗄️ Initializing database tables..." -ForegroundColor Blue
python -m app.db.init_db

Write-Host "  🧪 Executing automated backend test suite..." -ForegroundColor Blue
pytest -v

Set-Location ..

# 3. Frontend Setup
Write-Host "`n💻 Setting up Frontend..." -ForegroundColor Yellow
Set-Location frontend

if (-not (Test-Path ".env")) {
    Write-Host "  📄 Copying .env.example to .env..." -ForegroundColor Blue
    Copy-Item .env.example .env
}

Write-Host "  📥 Installing npm packages (Three.js, R3F, React 19)..." -ForegroundColor Blue
npm install

Set-Location ..

Write-Host "`n🎉 Setup complete! You are ready to start development." -ForegroundColor Green