#!/bin/bash

# AWS EC2 Deployment Script for Expense Tracker Backend
# Run this script on a fresh Ubuntu 24.04 EC2 instance
# Usage: curl -fsSL https://your-raw-script-url | bash

set -e

echo "🚀 Starting Expense Tracker Backend Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as ubuntu user
if [ "$USER" != "ubuntu" ]; then
    echo -e "${RED}Error: This script must run as ubuntu user${NC}"
    exit 1
fi

# 1. Update System
echo -e "${YELLOW}[1/8] Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# 2. Install Dependencies
echo -e "${YELLOW}[2/8] Installing system dependencies...${NC}"
sudo apt install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    build-essential \
    libpq-dev \
    git \
    curl \
    wget \
    nano \
    nginx \
    certbot \
    python3-certbot-nginx \
    postgresql-client-15

# 3. Clone Repository
echo -e "${YELLOW}[3/8] Cloning repository...${NC}"
if [ ! -d "/var/www/expense_be" ]; then
    sudo git clone https://github.com/vjvishal8386/expense_be.git /var/www/expense_be
    sudo chown -R ubuntu:ubuntu /var/www/expense_be
else
    echo "Repository already exists, skipping clone"
fi

# 4. Create Virtual Environment
echo -e "${YELLOW}[4/8] Creating Python virtual environment...${NC}"
cd /var/www/expense_be
python3.10 -m venv venv
source venv/bin/activate

# 5. Install Python Dependencies
echo -e "${YELLOW}[5/8] Installing Python dependencies...${NC}"
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 6. Create .env file
echo -e "${YELLOW}[6/8] Creating .env file...${NC}"
if [ ! -f "/var/www/expense_be/.env" ]; then
    cat > /var/www/expense_be/.env << 'EOF'
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
EOF
    echo -e "${YELLOW}⚠️  Created .env file. Please edit with your values:${NC}"
    echo "   nano /var/www/expense_be/.env"
else
    echo "✓ .env file already exists"
fi

# 7. Create Systemd Service
echo -e "${YELLOW}[7/8] Creating systemd service...${NC}"
sudo tee /etc/systemd/system/expense-tracker.service > /dev/null << 'EOF'
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

EnvironmentFile=/var/www/expense_be/.env

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable expense-tracker.service

# 8. Setup Nginx
echo -e "${YELLOW}[8/8] Configuring Nginx...${NC}"
sudo tee /etc/nginx/sites-available/expense-tracker > /dev/null << 'EOF'
upstream uvicorn {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name _;

    # Placeholder - replace with your domain after deployment
    location / {
        proxy_pass http://uvicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    access_log /var/log/nginx/expense-tracker-access.log;
    error_log /var/log/nginx/expense-tracker-error.log;
}
EOF

sudo ln -sf /etc/nginx/sites-available/expense-tracker /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl enable nginx

echo -e "${GREEN}✓ Deployment preparation complete!${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Edit .env file with your configuration:"
echo "   nano /var/www/expense_be/.env"
echo ""
echo "2. Run database migrations:"
echo "   cd /var/www/expense_be && source venv/bin/activate && alembic upgrade head"
echo ""
echo "3. Start the service:"
echo "   sudo systemctl start expense-tracker.service"
echo ""
echo "4. Check status:"
echo "   sudo systemctl status expense-tracker.service"
echo ""
echo "5. View logs:"
echo "   sudo journalctl -u expense-tracker.service -f"
echo ""
echo "6. Setup SSL/HTTPS:"
echo "   - Point your domain to this EC2 instance"
echo "   - Run: sudo certbot certonly --standalone -d your-domain.com"
echo "   - Update Nginx config with SSL certificate paths"
echo ""
echo "7. Restart Nginx:"
echo "   sudo systemctl restart nginx"
echo ""
echo -e "${GREEN}Deployment script completed! 🎉${NC}"
