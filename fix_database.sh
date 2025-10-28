#!/bin/bash

# Fix database configuration script

echo "🔧 Database Configuration Fix"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    
    # Generate SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s|SECRET_KEY=your-secret-key-here-generate-a-random-string|SECRET_KEY=$SECRET_KEY|" .env
fi

echo "Current .env DATABASE_URL:"
grep "^DATABASE_URL=" .env

echo ""
echo "You need to update the DATABASE_URL with your PostgreSQL credentials."
echo ""
echo "Options:"
echo "1. Use peer authentication (no password needed)"
echo "2. Use password authentication"
echo ""
echo "Choose option 1 (peer) or 2 (password): "
read -r choice

case $choice in
    1)
        # Try to get current system user
        USERNAME=$(whoami)
        echo ""
        echo "Checking if you can access PostgreSQL..."
        if psql -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
            echo "✅ Can connect to PostgreSQL as $USERNAME"
            NEW_URL="postgresql://$USERNAME@localhost:5432/expense_tracker"
        elif sudo -u postgres psql -c "SELECT 1;" > /dev/null 2>&1; then
            echo "✅ Can connect to PostgreSQL as postgres"
            NEW_URL="postgresql://postgres@localhost:5432/expense_tracker"
            USERNAME="postgres"
        else
            echo "❌ Cannot connect to PostgreSQL"
            exit 1
        fi
        
        echo ""
        echo "Creating database: expense_tracker"
        
        # Try with different users
        if psql -d postgres -c "CREATE DATABASE expense_tracker;" > /dev/null 2>&1; then
            echo "✅ Database created successfully"
        elif sudo -u postgres psql -c "CREATE DATABASE expense_tracker;" > /dev/null 2>&1; then
            echo "✅ Database created successfully"
        else
            echo "⚠️  Could not create database automatically"
            echo "Please run: createdb expense_tracker"
        fi
        
        # Update .env
        sed -i "s|^DATABASE_URL=.*|DATABASE_URL=$NEW_URL|" .env
        echo ""
        echo "✅ Updated DATABASE_URL to: $NEW_URL"
        ;;
    2)
        echo ""
        echo "Enter PostgreSQL username (default: postgres): "
        read -r pg_user
        pg_user=${pg_user:-postgres}
        
        echo "Enter PostgreSQL password: "
        read -rs pg_pass
        
        echo "Enter database name (default: expense_tracker): "
        read -r db_name
        db_name=${db_name:-expense_tracker}
        
        NEW_URL="postgresql://$pg_user:$pg_pass@localhost:5432/$db_name"
        sed -i "s|^DATABASE_URL=.*|DATABASE_URL=$NEW_URL|" .env
        
        echo ""
        echo "✅ Updated DATABASE_URL to: $NEW_URL"
        
        echo ""
        echo "Attempting to create database: $db_name"
        PGPASSWORD=$pg_pass psql -U $pg_user -h localhost -c "CREATE DATABASE $db_name;" 2>/dev/null
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "✅ Database configuration updated!"
echo ""
echo "New DATABASE_URL:"
grep "^DATABASE_URL=" .env
echo ""
echo "Next steps:"
echo "1. Run migrations: ./migrate.sh"
echo "2. Start server: ./run_server.sh"
echo "========================================="

