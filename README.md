# Expense Tracker Backend API

FastAPI backend for a React + TypeScript expense tracker application. This app allows users to manage shared expenses with friends in a one-on-one format.

## Features

- 🔐 JWT-based Authentication
- 👥 Friend Management (bidirectional relationships)
- 💰 Expense Tracking between two users
- 📊 Real-time Balance Calculation
- 🔄 Shared Data (expenses visible to both users)

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Authentication:** JWT tokens with bcrypt password hashing
- **Validation:** Pydantic models

## Setup Instructions

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Create PostgreSQL database
createdb expense_tracker

# Or using psql:
psql -U postgres
CREATE DATABASE expense_tracker;
\q
```

### 3. Environment Configuration

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your database credentials and secret key
nano .env
```

Generate a secure SECRET_KEY:
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Database Migration

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Run migrations
alembic upgrade head
```

### 5. Run the Server

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at: `http://127.0.0.1:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## API Endpoints

### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user info

### Friends

- `GET /friends` - Get all friends
- `POST /friends` - Add a new friend

### Expenses

- `GET /expenses/{friend_id}` - Get all expenses with a friend
- `POST /expenses` - Create new expense
- `GET /expenses/{friend_id}/balance` - Get balance with a friend

## Database Schema

### Users
- id (UUID)
- email (unique)
- password_hash
- name (optional)
- created_at

### Friends (Junction table)
- id (UUID)
- user_id → users.id
- friend_id → users.id
- created_at

### Expenses
- id (UUID)
- user_a_id → users.id
- user_b_id → users.id
- amount (decimal)
- description
- paid_by_user_id → users.id
- expense_date
- created_at
- updated_at

## Example Usage

### 1. Register User
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "vishal@gmail.com", "password": "password123"}'
```

### 2. Login
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "vishal@gmail.com", "password": "password123"}'
```

### 3. Add Friend
```bash
curl -X POST http://127.0.0.1:8000/friends \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "tushar@example.com", "name": "Tushar"}'
```

### 4. Add Expense
```bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "friend_id": "friend-uuid",
    "amount": 500,
    "description": "Lunch",
    "paid_by_user_id": "your-uuid",
    "expense_date": "2025-10-28"
  }'
```

### 5. Get Balance
```bash
curl -X GET http://127.0.0.1:8000/expenses/{friend_id}/balance \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app initialization
│   ├── database.py          # Database connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User model
│   │   ├── friend.py        # Friend model
│   │   └── expense.py       # Expense model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py          # Auth schemas
│   │   ├── friend.py        # Friend schemas
│   │   └── expense.py       # Expense schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          # Auth endpoints
│   │   ├── friends.py       # Friends endpoints
│   │   └── expenses.py      # Expenses endpoints
│   ├── dependencies.py      # Dependency injection
│   └── security.py          # JWT & password utilities
├── alembic/                 # Database migrations
├── requirements.txt
├── .env.example
└── README.md
```

## CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:3000` (React development server)

To modify CORS settings, edit `app/main.py`.

## Security Notes

- Passwords are hashed using bcrypt
- JWT tokens expire after 7 days
- All endpoints (except register/login) require authentication
- SECRET_KEY should be kept secret and never committed to version control

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Check database exists: `psql -l`
- Verify credentials in `.env` file

### Migration Issues
- Delete alembic/versions/* and regenerate: `alembic revision --autogenerate -m "Initial"`
- Check database connection string in `alembic.ini`

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## License

MIT License

