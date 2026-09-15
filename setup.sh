#!/usr/bin/env bash
set -e

echo "🚀 Starting SmartFit Full System Setup..."

PGUSER=${PGUSER:-postgres}

# 1. Database Setup
echo "
🐘 Checking & Creating PostgreSQL Databases..."
psql -U "$PGUSER" -c 'CREATE DATABASE "SmartFit_db";' 2>/dev/null || echo "  ℹ️ SmartFit_db ready or already exists."
psql -U "$PGUSER" -c 'CREATE DATABASE "SmartFit_Test_db";' 2>/dev/null || echo "  ℹ️ SmartFit_Test_db ready or already exists."

# 2. Backend Setup
echo "
⚙️ Setting up Backend..."
cd backend

if [ ! -d ".venv" ]; then
    echo "  📦 Creating Python virtual environment (.venv)..."
    python3 -m venv .venv
fi

echo "  🔌 Activating virtual environment..."
source .venv/bin/activate

echo "  📥 Installing Python dependencies..."
pip install -r requirements.txt --quiet

if [ ! -f ".env" ]; then
    echo "  📄 Copying .env.example to .env..."
    cp .env.example .env
fi

echo "  🗄️ Initializing database tables..."
python -m app.db.init_db

echo "  🧪 Executing automated backend test suite..."
pytest -v

cd ..

# 3. Frontend Setup
echo "
💻 Setting up Frontend..."
cd frontend

if [ ! -f ".env" ]; then
    echo "  📄 Copying .env.example to .env..."
    cp .env.example .env
fi

echo "  📥 Installing npm packages..."
npm install

cd ..

echo "
🎉 Setup complete! You are ready to start development."