# AWS EC2 Deployment Guide for Expense Tracker Backend

Complete guide to deploy your FastAPI backend to AWS EC2 with PostgreSQL, SSL/HTTPS, and production-grade security.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [EC2 Instance Setup](#ec2-instance-setup)
3. [Security Groups & Network](#security-groups--network)
4. [System Dependencies](#system-dependencies)
5. [Application Deployment](#application-deployment)
6. [Database Setup](#database-setup)
7. [SSL/HTTPS with Let's Encrypt](#sslhttps-with-lets-encrypt)
8. [Process Management with Systemd](#process-management-with-systemd)
9. [Nginx Reverse Proxy](#nginx-reverse-proxy)
10. [Monitoring & Logs](#monitoring--logs)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### AWS Account Requirements
- ✅ AWS account with billing enabled
- ✅ EC2 key pair created (`.pem` file)
- ✅ Estimated cost: **$5-15/month** for small-medium traffic
- ✅ Free tier eligible (if within 12 months of account creation)

### Local Prerequisites
- ✅ SSH client
- ✅ GitHub repository access (for code deployment)

### Application Requirements
- ✅ Python 3.10+ compatible
- ✅ PostgreSQL compatible database models
- ✅ Dependencies listed in `requirements.txt`

---

## EC2 Instance Setup

### Step 1: Launch EC2 Instance

1. **Go to AWS Console**
   - Visit https://console.aws.amazon.com
   - Navigate to EC2 Dashboard

2. **Click "Launch Instances"**

3. **Choose AMI (Amazon Machine Image)**
   - Select: **Ubuntu Server 24.04 LTS (Eligible for free tier)**
   - Architecture: 64-bit (x86)

4. **Instance Type**
   - **Development/Testing**: `t3.micro` (Free tier eligible)
   - **Small Production**: `t3.small` ($0.0208/hour)
   - **Medium Production**: `t3.medium` ($0.0416/hour)

5. **Configure Instance Details**
   - VPC: Default VPC (fine for most cases)
   - Subnet: Any subnet in your region
   - Auto-assign Public IP: **Enable**
   - IAM Role: None (unless using AWS services)

6. **Add Storage**
   - Size: **20 GB** (minimum for development)
   - Size: **30+ GB** (for production)
   - Volume Type: **gp3** (General Purpose SSD)
   - Delete on Termination: **Yes**

7. **Add Tags** (Optional but recommended)
   ```
   Key: Name
   Value: expense-tracker-backend
   
   Key: Environment
   Value: production
   
   Key: Project
   Value: spend-book
   ```

8. **Configure Security Group**
   - Create new security group
   - Name: `expense-tracker-sg`
   - Description: "Security group for Expense Tracker API"
   
   Keep default for now (we'll configure in next section)

9. **Review & Launch**
   - Select your key pair (or create new one)
   - Download `.pem` file if creating new key pair
   - Click "Launch Instances"

10. **Wait for Instance to Start**
    - Status check: Running
    - Status checks: 2/2 passed

### Step 2: Get Your Instance Details

1. **Find Public IP Address**
   - Go to EC2 Dashboard → Instances
   - Click your instance
   - Note the "Public IPv4 address" (e.g., `54.123.45.67`)

2. **Set Permissions on Key Pair** (Local machine)
   ```bash
   chmod 400 ~/Downloads/your-key.pem
   ```

3. **SSH Into Instance**
   ```bash
   ssh -i ~/Downloads/your-key.pem ubuntu@54.123.45.67
   ```
   
   You should see: `ubuntu@ip-172-31-XX-XX:~$`

---

## Security Groups & Network

### Configure Inbound Rules

1. **Go to EC2 Dashboard → Security Groups**
2. **Select your security group** (`expense-tracker-sg`)
3. **Click "Inbound rules" tab**
4. **Click "Edit inbound rules"**

### Required Rules

| Type | Protocol | Port Range | Source | Purpose |
|------|----------|-----------|--------|---------|
| SSH | TCP | 22 | 0.0.0.0/0 | SSH access (restrict this in production!) |
| HTTP | TCP | 80 | 0.0.0.0/0 | HTTP traffic (for Let's Encrypt) |
| HTTPS | TCP | 443 | 0.0.0.0/0 | HTTPS traffic (encrypted) |

**Add these rules:**

```
Rule 1:
  Type: SSH
  Protocol: TCP
  Port: 22
  Source: 0.0.0.0/0  (WARNING: Open to world! Restrict to your IP in production)

Rule 2:
  Type: HTTP
  Protocol: TCP
  Port: 80
  Source: 0.0.0.0/0

Rule 3:
  Type: HTTPS
  Protocol: TCP
  Port: 443
  Source: 0.0.0.0/0

Rule 4 (If using RDS):
  Type: Custom TCP
  Protocol: TCP
  Port: 5432 (PostgreSQL)
  Source: <RDS security group>
```

### Outbound Rules

- Keep default (allow all traffic out)

---

## System Dependencies

### Step 1: Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 2: Install Python & Build Tools

```bash
sudo apt install -y \
  python3.10 \
  python3.10-venv \
  python3-pip \
  build-essential \
  libpq-dev \
  git \
  curl \
  wget \
  nano
```

### Step 3: Install PostgreSQL Client (If using RDS)

```bash
sudo apt install -y postgresql-client-15
```

### Step 4: Install Nginx

```bash
sudo apt install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### Step 5: Install Certbot (For SSL)

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Step 6: Install Supervisor (Optional, for process management)

```bash
sudo apt install -y supervisor
```

---

## Application Deployment

### Step 1: Clone Repository

```bash
cd /var/www
sudo git clone https://github.com/vjvishal8386/expense_be.git
cd expense_be
sudo chown -R ubuntu:ubuntu .
```

### Step 2: Create Virtual Environment

```bash
python3.10 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Step 4: Create .env File

```bash
nano .env
```

**Paste this template** (update with your values):

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/expense_tracker

# JWT Configuration
SECRET_KEY=$(openssl rand -base64 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-digit-app-password
FROM_EMAIL=your-email@gmail.com

# Frontend URL
FRONTEND_URL=https://your-frontend-domain.com

# Environment
ENVIRONMENT=production
```

**To generate SECRET_KEY:**
```bash
openssl rand -base64 32
```

### Step 5: Test Application Locally

```bash
source venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Visit: `http://54.123.45.67:8000/docs` (replace with your public IP)

If you see Swagger UI, the app is working! Press `Ctrl+C` to stop.

---

## Database Setup

### Option A: AWS RDS (Recommended for Production)

#### Step 1: Create RDS Instance

1. **Go to AWS Console → RDS Dashboard**
2. **Click "Create database"**
3. **Select PostgreSQL**
4. **Choose Free tier or small instance**
5. **DB Instance Identifier**: `expense-tracker-db`
6. **Master Username**: `dbadmin`
7. **Master Password**: Generate strong password (save it!)
8. **Storage**: 20 GB
9. **Public accessibility**: Yes
10. **Create security group**: Name it `rds-sg`
11. **Click "Create database"**

#### Step 2: Get Connection Details

Wait 5-10 minutes for RDS to start, then:

1. **Go to RDS Dashboard → Databases**
2. **Click your database**
3. **Note the "Endpoint"** (e.g., `expense-tracker-db.xxxxx.us-east-1.rds.amazonaws.com`)
4. **Update .env with DATABASE_URL**

#### Step 3: Configure RDS Security Group

1. **Go to EC2 → Security Groups → rds-sg**
2. **Inbound rule:**
   - Type: PostgreSQL
   - Port: 5432
   - Source: `expense-tracker-sg` (your EC2 security group)

#### Step 4: Test Database Connection

```bash
psql -h expense-tracker-db.xxxxx.us-east-1.rds.amazonaws.com \
     -U dbadmin \
     -d expense_tracker \
     -c "SELECT version();"
```

#### Step 5: Run Database Migrations

```bash
source venv/bin/activate
alembic upgrade head
```

### Option B: Local PostgreSQL on EC2 (Not Recommended)

```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database
sudo -u postgres psql
  CREATE DATABASE expense_tracker;
  CREATE USER dbadmin WITH PASSWORD 'your-password';
  ALTER ROLE dbadmin SET client_encoding TO 'utf8';
  ALTER ROLE dbadmin SET default_transaction_isolation TO 'read committed';
  ALTER ROLE dbadmin SET default_transaction_deferrable TO on;
  ALTER ROLE dbadmin SET default_transaction_level TO 'read committed';
  GRANT ALL PRIVILEGES ON DATABASE expense_tracker TO dbadmin;
  \q

# Update .env
DATABASE_URL=postgresql://dbadmin:your-password@localhost:5432/expense_tracker
```

---

## SSL/HTTPS with Let's Encrypt

### Prerequisites
- Domain name (required)
- Domain pointing to your EC2 public IP

### Step 1: Point Domain to EC2

1. **Get your EC2 public IP**
2. **Update DNS records** in your domain registrar:
   ```
   A Record: api.yourdomain.com → 54.123.45.67
   ```
3. **Wait for DNS propagation** (up to 24 hours, usually 5 min)
4. **Verify DNS:**
   ```bash
   nslookup api.yourdomain.com
   ```

### Step 2: Create Certificate with Let's Encrypt

```bash
sudo certbot certonly --standalone \
  -d api.yourdomain.com \
  -d www.api.yourdomain.com \
  --agree-tos \
  -m your-email@gmail.com \
  -n
```

**Certificate location:**
```
/etc/letsencrypt/live/api.yourdomain.com/
```

### Step 3: Auto-Renewal

```bash
# Enable auto-renewal
sudo systemctl enable certbot.timer

# Test renewal (dry run)
sudo certbot renew --dry-run
```

---

## Process Management with Systemd

### Step 1: Create Systemd Service File

```bash
sudo nano /etc/systemd/system/expense-tracker.service
```

**Paste this:**

```ini
[Unit]
Description=Expense Tracker Backend API
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/var/www/expense_be
ExecStart=/var/www/expense_be/venv/bin/uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --timeout-keep-alive 5
Restart=on-failure
RestartSec=10s
StandardOutput=journal
StandardError=journal

# Environment variables
EnvironmentFile=/var/www/expense_be/.env

[Install]
WantedBy=multi-user.target
```

### Step 2: Enable & Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable expense-tracker.service
sudo systemctl start expense-tracker.service
```

### Step 3: Check Service Status

```bash
sudo systemctl status expense-tracker.service
sudo journalctl -u expense-tracker.service -f  # View logs
```

### Step 4: Service Management

```bash
# Stop service
sudo systemctl stop expense-tracker.service

# Restart service
sudo systemctl restart expense-tracker.service

# View logs (last 50 lines)
sudo journalctl -u expense-tracker.service -n 50

# View logs (real-time)
sudo journalctl -u expense-tracker.service -f
```

---

## Nginx Reverse Proxy

### Step 1: Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/expense-tracker
```

**Paste this:**

```nginx
upstream uvicorn {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Certificate
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # CORS Headers
    add_header Access-Control-Allow-Origin "https://your-frontend-domain.com" always;
    add_header Access-Control-Allow-Credentials "true" always;

    # Proxy Settings
    location / {
        proxy_pass http://uvicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "upgrade";
        proxy_set_header Upgrade $http_upgrade;
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_http_version 1.1;
    }

    # Health Check Endpoint
    location /health {
        proxy_pass http://uvicorn;
        access_log off;
    }

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    # Logging
    access_log /var/log/nginx/expense-tracker-access.log;
    error_log /var/log/nginx/expense-tracker-error.log;
}
```

### Step 2: Enable Nginx Configuration

```bash
sudo ln -s /etc/nginx/sites-available/expense-tracker /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remove default config
```

### Step 3: Test Nginx Configuration

```bash
sudo nginx -t
```

Should output: `nginx: configuration file test is successful`

### Step 4: Restart Nginx

```bash
sudo systemctl restart nginx
```

### Step 5: Verify HTTPS

Visit: `https://api.yourdomain.com/docs`

You should see Swagger UI with a valid SSL certificate! 🎉

---

## Monitoring & Logs

### View Application Logs

```bash
# Real-time logs
sudo journalctl -u expense-tracker.service -f

# Last 100 lines
sudo journalctl -u expense-tracker.service -n 100

# Today's logs
sudo journalctl -u expense-tracker.service --since today

# Specific error
sudo journalctl -u expense-tracker.service | grep ERROR
```

### View Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/expense-tracker-access.log

# Error logs
sudo tail -f /var/log/nginx/expense-tracker-error.log
```

### Monitor System Resources

```bash
# Install htop
sudo apt install htop

# View resource usage
htop

# Check disk space
df -h

# Check memory
free -h
```

### Health Check Endpoint

Add this to your FastAPI app (`app/main.py`):

```python
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT"),
        "version": "1.0.0"
    }
```

Test it:
```bash
curl https://api.yourdomain.com/health
```

---

## Troubleshooting

### Issue: "Permission denied" when accessing files

**Solution:**
```bash
sudo chown -R ubuntu:ubuntu /var/www/expense_be
```

### Issue: "Database connection refused"

**Solution:**
1. Check RDS security group allows traffic from EC2 security group
2. Verify .env DATABASE_URL is correct
3. Test connection:
   ```bash
   psql -h your-rds-endpoint -U dbadmin -d expense_tracker -c "SELECT 1;"
   ```

### Issue: "Certificate not found"

**Solution:**
```bash
# Verify certificate exists
ls -la /etc/letsencrypt/live/api.yourdomain.com/

# Re-create if missing
sudo certbot certonly --standalone -d api.yourdomain.com -m your-email@gmail.com
```

### Issue: Nginx shows 502 Bad Gateway

**Solution:**
1. Check if uvicorn service is running:
   ```bash
   sudo systemctl status expense-tracker.service
   ```
2. Check uvicorn logs:
   ```bash
   sudo journalctl -u expense-tracker.service -f
   ```
3. Verify Nginx configuration:
   ```bash
   sudo nginx -t
   ```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>

# Restart service
sudo systemctl restart expense-tracker.service
```

### Issue: Application won't start

**Solution:**
```bash
# Test locally
cd /var/www/expense_be
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Check for errors in output
# Common issues: Missing dependencies, database connection, missing .env
```

### Issue: "Email not sending"

**Solution:**
1. Verify SMTP credentials in .env
2. Check Gmail 2-Step Verification is enabled
3. Verify App Password is correct (16 digits)
4. Test SMTP connection:
   ```bash
   python -c "import smtplib; smtplib.SMTP('smtp.gmail.com', 587).starttls()"
   ```

### Issue: CORS errors on frontend

**Solution:**
Update Nginx configuration CORS headers:
```nginx
add_header Access-Control-Allow-Origin "https://your-frontend-domain.com" always;
add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
```

Then restart Nginx:
```bash
sudo systemctl restart nginx
```

---

## Deployment Checklist

- [ ] EC2 instance launched and running
- [ ] Security groups configured (SSH, HTTP, HTTPS)
- [ ] Domain name pointing to EC2 public IP
- [ ] System dependencies installed
- [ ] Application cloned to `/var/www/expense_be`
- [ ] Virtual environment created
- [ ] Requirements installed
- [ ] `.env` file configured with all variables
- [ ] Database migrations run (`alembic upgrade head`)
- [ ] SSL certificate generated with Let's Encrypt
- [ ] Nginx reverse proxy configured
- [ ] Systemd service created and running
- [ ] Application accessible at `https://api.yourdomain.com`
- [ ] Swagger docs working at `https://api.yourdomain.com/docs`
- [ ] Health check endpoint responding
- [ ] Logs being generated and accessible

---

## Performance Tuning

### Uvicorn Workers

```bash
# Current: 4 workers
# For more concurrent connections, increase:

ExecStart=/var/www/expense_be/venv/bin/uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 8  # Increase for more CPU cores
```

### Database Connection Pooling

Add to your `app/database.py`:

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Nginx Caching

Add to Nginx config:

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

---

## Cost Estimation

| Component | Instance | Cost/Month |
|-----------|----------|-----------|
| EC2 | t3.small | $7.50 |
| RDS | db.t3.micro | $9.00 |
| Bandwidth | 100 GB | $0.00-5.00 |
| **Total** | | **$16.50-21.50** |

*Costs vary by region. Check AWS pricing calculator.*

---

## Summary

Your FastAPI backend is now:
- ✅ Running on AWS EC2
- ✅ Using PostgreSQL RDS database
- ✅ Secured with SSL/HTTPS
- ✅ Behind Nginx reverse proxy
- ✅ Managed with systemd service
- ✅ Auto-scaling with Uvicorn workers
- ✅ Monitored with systemd logs
- ✅ Production-ready! 🚀

For questions, check the [Troubleshooting](#troubleshooting) section or AWS documentation.
