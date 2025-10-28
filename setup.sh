#!/bin/bash

# Setup script for Expense Tracker Backend

echo "================================"
echo "Expense Tracker Backend Setup"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file from .env.example..."
    cp .env.example .env
    
    # Generate a random secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Update SECRET_KEY in .env file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|SECRET_KEY=your-secret-key-here-generate-a-random-string|SECRET_KEY=$SECRET_KEY|" .env
    else
        # Linux
        sed -i "s|SECRET_KEY=your-secret-key-here-generate-a-random-string|SECRET_KEY=$SECRET_KEY|" .env
    fi
    
    echo ""
    echo "⚠️  IMPORTANT: Please update the DATABASE_URL in .env file with your PostgreSQL credentials!"
    echo "   Example: DATABASE_URL=postgresql://username:password@localhost:5432/expense_tracker"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Update DATABASE_URL in .env file with your PostgreSQL credentials"
echo "2. Create PostgreSQL database: createdb expense_tracker"
echo "3. Run database migrations: alembic upgrade head"
echo "4. Start the server: uvicorn app.main:app --reload --port 8000"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
