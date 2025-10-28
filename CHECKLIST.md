# Expense Tracker Backend - Setup Checklist

Use this checklist to ensure everything is configured correctly.

## ☑️ Initial Setup

- [ ] Python 3.9+ installed (`python3 --version`)
- [ ] PostgreSQL installed and running (`sudo systemctl status postgresql`)
- [ ] Git installed (optional)
- [ ] Virtual environment support (`python3 -m venv --help`)

## ☑️ Project Setup

- [ ] Downloaded/cloned the project
- [ ] Navigated to project directory (`cd temp_BE`)
- [ ] Run setup script (`./setup.sh`)
- [ ] Virtual environment created (`venv/` directory exists)
- [ ] Dependencies installed (check `pip list`)

## ☑️ Database Configuration

- [ ] PostgreSQL database created (`createdb expense_tracker`)
- [ ] Database connection verified (`psql -d expense_tracker -c "\dt"`)
- [ ] `.env` file created from `.env.example`
- [ ] `DATABASE_URL` updated with correct credentials
- [ ] `SECRET_KEY` generated and set (run `python -c "import secrets; print(secrets.token_urlsafe(32))"`)

## ☑️ Database Migrations

- [ ] Alembic configured (`alembic.ini` exists)
- [ ] Initial migration created (`./migrate.sh`)
- [ ] Migrations applied successfully
- [ ] Tables created in database (verify with `psql -d expense_tracker -c "\dt"`)
  - [ ] `users` table exists
  - [ ] `friends` table exists
  - [ ] `expenses` table exists

## ☑️ Server Testing

- [ ] Server starts without errors (`./run_server.sh`)
- [ ] Health endpoint works (`curl http://127.0.0.1:8000/health`)
- [ ] Swagger UI accessible (`http://127.0.0.1:8000/docs`)
- [ ] ReDoc accessible (`http://127.0.0.1:8000/redoc`)

## ☑️ API Testing

### Authentication
- [ ] User registration works (`POST /auth/register`)
- [ ] User login works (`POST /auth/login`)
- [ ] Get current user works (`GET /auth/me`)
- [ ] JWT token received and valid

### Friends
- [ ] Get friends list works (`GET /friends`)
- [ ] Add friend works (`POST /friends`)
- [ ] Bidirectional friendship verified (both users see each other)

### Expenses
- [ ] Create expense works (`POST /expenses`)
- [ ] Get expenses with friend works (`GET /expenses/{friend_id}`)
- [ ] Get balance works (`GET /expenses/{friend_id}/balance`)
- [ ] Balance calculation is correct
- [ ] Expenses visible to both users

## ☑️ Security Verification

- [ ] Passwords are hashed (check database - no plain text passwords)
- [ ] JWT tokens expire correctly (check token payload)
- [ ] Protected endpoints require authentication
- [ ] Unauthorized requests return 401
- [ ] CORS configured for frontend origin

## ☑️ Frontend Integration

- [ ] Frontend can connect to `http://127.0.0.1:8000`
- [ ] CORS headers allow frontend requests
- [ ] Registration from frontend works
- [ ] Login from frontend works
- [ ] Protected API calls from frontend work
- [ ] Token stored in frontend (localStorage/sessionStorage)

## ☑️ Production Readiness (Optional)

- [ ] Environment variables secured
- [ ] Database backups configured
- [ ] Logging configured
- [ ] Error tracking setup (e.g., Sentry)
- [ ] HTTPS configured
- [ ] Rate limiting implemented
- [ ] Server monitoring setup
- [ ] Database connection pooling optimized

## 🧪 Test Scenarios

### Scenario 1: Two Users, One Expense
- [ ] User A registers
- [ ] User B registers
- [ ] User A adds User B as friend
- [ ] User A creates expense (User A paid)
- [ ] User B sees the expense
- [ ] Balance shows: User B owes User A

### Scenario 2: Balanced Expenses
- [ ] User A creates expense for ₹500 (A paid)
- [ ] User B creates expense for ₹500 (B paid)
- [ ] Balance shows: 0 (settled)

### Scenario 3: Multiple Expenses
- [ ] Create 5 expenses with varying amounts
- [ ] Verify all expenses appear for both users
- [ ] Verify balance calculation is accurate
- [ ] Verify expenses sorted by date (newest first)

### Scenario 4: Edge Cases
- [ ] Cannot add self as friend
- [ ] Cannot create expense with non-friend
- [ ] Cannot create expense with negative amount
- [ ] Cannot create expense with empty description
- [ ] Cannot access endpoints without token
- [ ] Invalid token returns 401

## 🔍 Verification Commands

### Check Python Version
```bash
python3 --version
# Should be 3.9 or higher
```

### Check PostgreSQL Status
```bash
sudo systemctl status postgresql
# Should show "active (running)"
```

### Check Database Tables
```bash
psql -d expense_tracker -c "\dt"
# Should list: users, friends, expenses, alembic_version
```

### Check Server Health
```bash
curl http://127.0.0.1:8000/health
# Should return: {"status":"healthy"}
```

### Run All API Tests
```bash
python test_api.py
# Should complete without errors
```

### Check Virtual Environment
```bash
source venv/bin/activate
which python
# Should point to venv/bin/python
```

### Verify Dependencies
```bash
pip list | grep -E "fastapi|sqlalchemy|uvicorn|jose|passlib"
# All should be installed
```

## 📋 Environment Variables Checklist

Check your `.env` file has all required variables:

```bash
# Required
✓ DATABASE_URL=postgresql://...
✓ SECRET_KEY=...
✓ ALGORITHM=HS256
✓ ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

## 🐛 Troubleshooting Checklist

If something isn't working, check:

- [ ] Virtual environment is activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] PostgreSQL is running
- [ ] Database exists
- [ ] `.env` file exists with correct values
- [ ] Migrations have been run
- [ ] No firewall blocking port 8000
- [ ] No other service using port 8000
- [ ] Python version is 3.9+

## ✅ Ready to Go!

Once all items are checked:

1. ✅ **Development**: Server running, API tested, ready for frontend integration
2. ✅ **Documentation**: README, QUICKSTART, API_EXAMPLES available
3. ✅ **Testing**: test_api.py script available, Swagger UI accessible
4. ✅ **Production**: Ready for deployment (after production checklist)

## 📞 Quick Reference

- **Start Server**: `./run_server.sh`
- **Run Migrations**: `./migrate.sh`
- **Run Tests**: `python test_api.py`
- **API Docs**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

---

**Status**: All checked? You're ready to build an amazing expense tracker! 🚀

