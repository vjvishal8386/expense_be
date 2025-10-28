# Quick Start Guide

Get your Expense Tracker API up and running in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- PostgreSQL database
- Git (optional)

## Setup Steps

### 1. Automated Setup (Recommended)

```bash
# Make setup script executable (if not already)
chmod +x setup.sh

# Run setup script
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Generate a secure SECRET_KEY
- Create a `.env` file

### 2. Configure Database

Edit the `.env` file and update the `DATABASE_URL`:

```bash
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/expense_tracker
```

### 3. Create Database

```bash
# Using createdb command
createdb expense_tracker

# OR using psql
psql -U postgres
CREATE DATABASE expense_tracker;
\q
```

### 4. Run Database Migrations

```bash
# Make migrate script executable (if not already)
chmod +x migrate.sh

# Run migrations
./migrate.sh
```

### 5. Start the Server

```bash
# Make run script executable (if not already)
chmod +x run_server.sh

# Start the server
./run_server.sh
```

The API will be available at: **http://127.0.0.1:8000**

## Test the API

### Option 1: Using Swagger UI (Recommended)

Open your browser and go to: **http://127.0.0.1:8000/docs**

You can test all endpoints interactively!

### Option 2: Using the Test Script

```bash
# Make test script executable (if not already)
chmod +x test_api.py

# Run tests
python test_api.py
```

### Option 3: Using cURL

```bash
# Health check
curl http://127.0.0.1:8000/health

# Register a user
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123", "name": "John Doe"}'

# Login
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

## Manual Setup (Alternative)

If you prefer manual setup:

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy .env.example to .env
cp .env.example .env

# 5. Edit .env and update DATABASE_URL and SECRET_KEY
nano .env

# 6. Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 7. Create database
createdb expense_tracker

# 8. Run migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# 9. Start server
uvicorn app.main:app --reload --port 8000
```

## Project Structure

```
temp_BE/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # Database configuration
│   ├── security.py          # JWT & password hashing
│   ├── dependencies.py      # Dependency injection
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── friend.py
│   │   └── expense.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── auth.py
│   │   ├── friend.py
│   │   └── expense.py
│   └── routers/             # API endpoints
│       ├── auth.py
│       ├── friends.py
│       └── expenses.py
├── alembic/                 # Database migrations
├── setup.sh                 # Automated setup script
├── run_server.sh           # Server start script
├── migrate.sh              # Database migration script
├── test_api.py             # API testing script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create from .env.example)
└── README.md               # Detailed documentation
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user info

### Friends
- `GET /friends` - Get all friends
- `POST /friends` - Add a friend

### Expenses
- `GET /expenses/{friend_id}` - Get expenses with a friend
- `POST /expenses` - Create new expense
- `GET /expenses/{friend_id}/balance` - Get balance with friend

## Common Issues

### Database Connection Error
- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Check database exists: `psql -l`
- Verify DATABASE_URL in `.env` is correct

### Import Errors
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Port Already in Use
- Change port in `run_server.sh` or run: `uvicorn app.main:app --reload --port 8001`

### Alembic Migration Issues
- Delete all files in `alembic/versions/`
- Run: `alembic revision --autogenerate -m "Initial migration"`
- Run: `alembic upgrade head`

## Next Steps

1. **Connect your React frontend** to `http://127.0.0.1:8000`
2. **Explore API docs** at `http://127.0.0.1:8000/docs`
3. **Review README.md** for detailed documentation
4. **Test all endpoints** using the test script or Swagger UI

## Support

For issues or questions:
1. Check the main `README.md` for detailed information
2. Review the API documentation at `/docs`
3. Check the troubleshooting section in `README.md`

Happy coding! 🚀

