# Free Deployment Guide for FastAPI Backend

Complete guide to deploy your Expense Tracker backend for **FREE** with PostgreSQL database.

## 📋 Table of Contents
1. [Best Free Options](#best-free-options)
2. [Option 1: Render (Recommended)](#option-1-render-recommended)
3. [Option 2: Railway](#option-2-railway)
4. [Option 3: Fly.io](#option-3-flyio)
5. [Free PostgreSQL Database Options](#free-postgresql-database-options)
6. [Environment Variables Setup](#environment-variables-setup)
7. [CORS Configuration for Production](#cors-configuration)
8. [Testing Your Deployment](#testing-your-deployment)

---

## Note on bcrypt / passlib compatibility

We pin `bcrypt==3.2.2` in `requirements.txt` because some newer `bcrypt` releases changed how version metadata is exposed which caused `passlib.handlers.bcrypt` to fail when trying to read the bcrypt version at runtime. If you upgrade `bcrypt` or `passlib` in future, verify the registration/password hashing flows locally and in CI.


## 🎯 Best Free Options (Comparison)

| Platform | Backend | Database | Auto-Deploy | Sleep Time | Best For |
|----------|---------|----------|-------------|------------|----------|
| **Render** | ✅ Free | ✅ Free PostgreSQL | ✅ GitHub | 15min inactive | **Recommended** |
| **Railway** | ✅ $5 credit/mo | ✅ Included | ✅ GitHub | None | Simple setup |
| **Fly.io** | ✅ Free | ❌ Extra setup | ✅ GitHub | None | Advanced users |
| **Supabase** | ❌ No backend | ✅ Free PostgreSQL | N/A | None | Database only |
| **Neon** | ❌ No backend | ✅ Free PostgreSQL | N/A | None | Database only |

**Recommendation**: Use **Render** - easiest setup with both backend and database free!

---

## Option 1: Render (Recommended) ⭐

**Free Tier:**
- FastAPI backend hosting
- PostgreSQL database (512MB)
- Auto-deploy from GitHub
- HTTPS included
- Custom domain support

### Step 1: Prepare Your Code

Create `render.yaml` in project root:

```yaml
# render.yaml
services:
  - type: web
    name: expense-tracker-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: expense-tracker-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: ALGORITHM
        value: HS256
      - key: ACCESS_TOKEN_EXPIRE_MINUTES
        value: "10080"

databases:
  - name: expense-tracker-db
    databaseName: expense_tracker
    user: expense_tracker_user
```

### Step 2: Create `runtime.txt`

```txt
python-3.12.0
```

### Step 3: Update CORS in `app/main.py`

```python
# Add your Render URL after deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend.vercel.app",  # Add your frontend URL
        "*"  # For testing only - remove in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 4: Deploy to Render

1. **Create account**: Go to https://render.com and sign up (free)
2. **Connect GitHub**: Link your GitHub account
3. **Create new Web Service**:
   - Click "New +" → "Web Service"
   - Connect your repository
   - Name: `expense-tracker-api`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   
4. **Create PostgreSQL Database**:
   - Click "New +" → "PostgreSQL"
   - Name: `expense-tracker-db`
   - Database: `expense_tracker`
   - Click "Create Database"

5. **Add Environment Variables**:
   - Go to Web Service → Environment
   - Add:
     ```
     DATABASE_URL = [Copy from PostgreSQL dashboard]
     SECRET_KEY = [Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"]
     ALGORITHM = HS256
     ACCESS_TOKEN_EXPIRE_MINUTES = 10080
     ```

6. **Deploy**: Click "Create Web Service"

### Step 5: Run Database Migrations

After deployment, go to Shell tab and run:
```bash
alembic upgrade head
```

**Your API URL**: `https://your-app-name.onrender.com`

---

## Option 2: Railway 🚂

**Free Tier:**
- $5 credit per month (enough for small apps)
- PostgreSQL included
- Auto-deploy from GitHub
- No sleep time

### Step 1: Create `Procfile`

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Step 2: Deploy to Railway

1. **Sign up**: https://railway.app (use GitHub login)
2. **New Project**: 
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   
3. **Add PostgreSQL**:
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway auto-creates DATABASE_URL

4. **Add Environment Variables**:
   - Click on your service → Variables
   - Add:
     ```
     SECRET_KEY = [generate random string]
     ALGORITHM = HS256
     ACCESS_TOKEN_EXPIRE_MINUTES = 10080
     ```

5. **Generate Domain**:
   - Settings → Generate Domain
   - Your API: `https://your-app.up.railway.app`

6. **Run Migrations**:
   - Go to service → Shell
   - Run: `alembic upgrade head`

---

## Option 3: Fly.io 🪰

**Free Tier:**
- 3 shared VMs
- 3GB storage
- 160GB bandwidth/month

### Step 1: Install Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
```

### Step 2: Create `fly.toml`

```toml
app = "expense-tracker-api"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"
  ALGORITHM = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES = "10080"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

### Step 3: Deploy

```bash
# Login
fly auth login

# Launch app
fly launch

# Set secrets
fly secrets set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
fly secrets set DATABASE_URL="your_postgresql_url"

# Deploy
fly deploy
```

**Your API URL**: `https://expense-tracker-api.fly.dev`

---

## Free PostgreSQL Database Options

### Option A: Render PostgreSQL (Recommended)
- **Free Tier**: 512MB storage, 90 days inactive deletion
- **Setup**: Automatic with Render web service
- **URL**: Provided in Render dashboard
- **Best for**: Using Render for backend

### Option B: Supabase
- **Free Tier**: 500MB database, 2GB bandwidth
- **Setup**: 
  1. Go to https://supabase.com
  2. Create new project
  3. Copy connection string from Settings → Database
- **Connection String**: 
  ```
  postgresql://postgres:[password]@[host]:5432/postgres
  ```

### Option C: Neon (Serverless Postgres)
- **Free Tier**: 512MB storage, 1 project
- **Setup**:
  1. Go to https://neon.tech
  2. Create project
  3. Copy connection string
- **Features**: Auto-scaling, branching
- **Best for**: Modern serverless apps

### Option D: ElephantSQL
- **Free Tier**: 20MB storage (Tiny Turtle plan)
- **Setup**:
  1. Go to https://www.elephantsql.com
  2. Create new instance
  3. Copy URL
- **Limitation**: Very small storage

### Option E: Aiven
- **Free Tier**: 30-day trial, then paid
- **Not recommended** for permanent free hosting

---

## Environment Variables Setup

### Required Variables

```bash
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### For Render

Add in Dashboard → Environment:
```
DATABASE_URL = [from PostgreSQL service]
SECRET_KEY = [generated value]
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 10080
```

### For Railway

Variables are auto-added when you connect PostgreSQL. Just add:
```
SECRET_KEY = [generated value]
```

---

## CORS Configuration for Production

Update `app/main.py`:

```python
# For production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://your-frontend-domain.vercel.app",  # Production frontend
        "https://your-frontend-domain.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Important**: Don't use `"*"` in production! Add specific frontend URLs.

---

## Database Migrations on Deployment

After deploying, run migrations:

### On Render
```bash
# In Shell tab
alembic upgrade head
```

### On Railway
```bash
# In service Shell
alembic upgrade head
```

### On Fly.io
```bash
fly ssh console
alembic upgrade head
```

---

## Testing Your Deployment

### 1. Check Health Endpoint

```bash
curl https://your-api-url.onrender.com/health
# Should return: {"status":"healthy"}
```

### 2. Test Registration

```bash
curl -X POST https://your-api-url.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### 3. Check API Documentation

Visit: `https://your-api-url.onrender.com/docs`

### 4. Test from Frontend

Update your frontend `.env`:
```
REACT_APP_API_BASE_URL=https://your-api-url.onrender.com
```

---

## Deployment Checklist

Before deploying:

- [ ] All code committed to GitHub
- [ ] `requirements.txt` is up to date
- [ ] Environment variables prepared
- [ ] CORS origins updated with production URLs
- [ ] Database connection string ready
- [ ] Migrations tested locally
- [ ] API endpoints tested locally

After deploying:

- [ ] Health endpoint returns 200
- [ ] Database migrations run successfully
- [ ] Registration endpoint works
- [ ] Login endpoint works
- [ ] Protected endpoints require auth
- [ ] Frontend can connect to backend
- [ ] CORS headers working correctly

---

## 🎯 Recommended Setup

### For Simplest Deployment:
1. **Backend + Database**: Use **Render** (both free)
2. **Frontend**: Deploy on **Vercel** or **Netlify** (free)

### Setup Steps:
1. Push code to GitHub
2. Create Render account
3. Deploy Web Service (FastAPI backend)
4. Create PostgreSQL database on Render
5. Connect database to web service
6. Run migrations
7. Update frontend with production API URL
8. Test all endpoints

**Total Time**: 15-20 minutes  
**Total Cost**: $0 (completely free!)

---

## Alternative: All-in-One Solutions

### Option: PythonAnywhere (Simple but Limited)
- **Free Tier**: 1 web app, 512MB storage
- **Limitation**: No outbound HTTPS, older Python versions
- **Best for**: Learning, not production

### Option: Heroku (No longer free)
- Heroku removed free tier in 2022
- Paid plans start at $7/month
- Not recommended for free hosting

---

## Cost Comparison

| Platform | Monthly Cost | Storage | Uptime | Auto-Deploy |
|----------|--------------|---------|--------|-------------|
| Render (Free) | $0 | 512MB | ~99% | ✅ |
| Railway | $0 ($5 credit) | 1GB | 99.9% | ✅ |
| Fly.io | $0 | 3GB | 99.9% | ✅ |
| Heroku | $7+ | 512MB | 99.95% | ✅ |

---

## Troubleshooting Deployment

### Database Connection Failed
```bash
# Check DATABASE_URL format
postgresql://username:password@host:port/database

# Test connection
psql "postgresql://user:pass@host:port/dbname"
```

### Migrations Failed
```bash
# Ensure alembic is in requirements.txt
# Run migrations manually via shell
alembic upgrade head
```

### CORS Error
```python
# Update allow_origins with your frontend URL
allow_origins=["https://your-frontend.vercel.app"]
```

### App Crashed
```bash
# Check logs in platform dashboard
# Verify all environment variables are set
# Check Python version compatibility
```

---

## 🚀 Quick Start (Render)

```bash
# 1. Push to GitHub
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Go to render.com
# 3. New Web Service → Connect GitHub repo
# 4. Add environment variables
# 5. Click "Create Web Service"
# 6. Go to Shell and run:
alembic upgrade head

# 7. Visit: https://your-app.onrender.com/docs
```

**Done!** Your API is live! 🎉

---

## Next Steps After Deployment

1. Update frontend with production API URL
2. Test all endpoints with production data
3. Set up monitoring (Render/Railway dashboards)
4. Configure custom domain (optional)
5. Set up backup strategy for database
6. Monitor usage and costs
7. Plan for scaling if needed

---

## Support & Resources

- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app
- **Fly.io Docs**: https://fly.io/docs
- **Supabase**: https://supabase.com/docs
- **Neon**: https://neon.tech/docs

Happy deploying! 🚀

