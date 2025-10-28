#!/bin/bash

# Database migration script

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it from .env.example"
    exit 1
fi

echo "🗄️  Running database migrations..."
echo ""

# Check if this is the first migration
if [ -z "$(ls -A alembic/versions 2>/dev/null)" ] || [ ! -d "alembic/versions" ]; then
    echo "📝 Creating initial migration..."
    alembic revision --autogenerate -m "Initial migration"
fi

echo "⬆️  Applying migrations..."
alembic upgrade head

echo ""
echo "✅ Database migrations completed!"

