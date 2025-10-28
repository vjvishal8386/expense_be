# Quick Setup Guide - Run Server Now!

## The Problem
Your `.env` file has placeholder database credentials that don't match your PostgreSQL setup.

## The Solution - 3 Simple Steps

### Step 1: Create PostgreSQL User & Database

Run these commands in your terminal:

```bash
# Create PostgreSQL user 'vishal' (if needed)
sudo -u postgres createuser -s vishal

# Create the database
sudo -u postgres createdb -O vishal expense_tracker
```

**OR if you prefer to use the default postgres user:**

```bash
# Create database as postgres user
sudo -u postgres createdb expense_tracker
```

---

### Step 2: Update .env File

Edit the `.env` file and replace the DATABASE_URL line:

**Option A: Using your username 'vishal' (recommended)**
```bash
nano .env
```

Change this line:
```
DATABASE_URL=postgresql://user:password@localhost:5432/expense_tracker
```

To this:
```
DATABASE_URL=postgresql://vishal@localhost:5432/expense_tracker
```

**Option B: Using postgres user**
```
DATABASE_URL=postgresql://postgres@localhost:5432/expense_tracker
```

Also generate a secure SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and replace `your-secret-key-here-generate-a-random-string` in `.env`

---

### Step 3: Run Migrations & Start Server

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run database migrations
./migrate.sh

# Start the server
./run_server.sh
```

---

## ⚡ FASTEST WAY - Copy & Paste These Commands:

### If you want to use 'vishal' as database user:

```bash
# 1. Setup database
sudo -u postgres createuser -s vishal 2>/dev/null || echo "User already exists"
sudo -u postgres createdb -O vishal expense_tracker 2>/dev/null || echo "Database already exists"

# 2. Update .env
cd /home/vishal/Downloads/temp_BE
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
cat > .env << EOF
DATABASE_URL=postgresql://vishal@localhost:5432/expense_tracker
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
EOF

# 3. Run migrations
source venv/bin/activate
./migrate.sh

# 4. Start server
./run_server.sh
```

### If you prefer using 'postgres' user:

```bash
# 1. Setup database
sudo -u postgres createdb expense_tracker 2>/dev/null || echo "Database already exists"

# 2. Update .env
cd /home/vishal/Downloads/temp_BE
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
cat > .env << EOF
DATABASE_URL=postgresql://postgres@localhost:5432/expense_tracker
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
EOF

# 3. Run migrations
source venv/bin/activate
./migrate.sh

# 4. Start server
./run_server.sh
```

---

## What You'll See When It Works:

```
🚀 Starting Expense Tracker API server...
📍 API will be available at: http://127.0.0.1:8000
📚 API Documentation: http://127.0.0.1:8000/docs

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Then visit: **http://127.0.0.1:8000/docs** 🎉

---

## Troubleshooting

### "Role vishal does not exist"
Run: `sudo -u postgres createuser -s vishal`

### "Database already exists"
That's fine! Continue with step 2.

### "Permission denied on .env"
Run: `chmod 644 .env`

### "Module not found"
Make sure venv is activated: `source venv/bin/activate`

### Still having issues?
Check: `sudo systemctl status postgresql` (should be running)

---

## After Server Starts

1. Visit **http://127.0.0.1:8000/docs** for Swagger UI
2. Test registration endpoint
3. Connect your React frontend

🚀 You're ready to go!

