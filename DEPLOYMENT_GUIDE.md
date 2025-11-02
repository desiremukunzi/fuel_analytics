# 🚀 DEPLOYMENT GUIDE - GITHUB TO UBUNTU SERVER

## 📋 TABLE OF CONTENTS
1. [Prepare Local Code](#prepare-local-code)
2. [Push to GitHub](#push-to-github)
3. [Server Setup](#server-setup)
4. [Deploy Backend](#deploy-backend)
5. [Deploy Frontend](#deploy-frontend)
6. [Configure Domain & SSL](#configure-domain--ssl)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## 🔧 PART 1: PREPARE LOCAL CODE

### Step 1.1: Clean Your Project

**Remove sensitive/unnecessary files:**

```bash
cd A:\MD\fuel

# Remove backup files
del /S *.backup*
del /S *.bak

# Remove test files (optional)
# Keep only what you need in production
```

### Step 1.2: Create .gitignore

Already created! Located at: `A:\MD\fuel\.gitignore`

**Verify it includes:**
- `venv/` (Don't push virtual environment)
- `db_config.py` (Don't push database credentials!)
- `ml_models/` (Models are too large, will train on server)
- `__pycache__/` (Python cache)
- `*.log` (Log files)

### Step 1.3: Create Database Config Template

Already created! Located at: `A:\MD\fuel\db_config_template.py`

**Users will copy this and fill in their credentials:**
```bash
# On server, users will do:
cp db_config_template.py db_config.py
nano db_config.py  # Edit with actual credentials
```

### Step 1.4: Update Requirements Files

**Backend requirements:**
```bash
cd A:\MD\fuel
pip freeze > requirements.txt
```

**Frontend requirements:**
Frontend already has `package.json`, so you're good!

### Step 1.5: Create README.md

Create a comprehensive README:

```bash
# See DEPLOYMENT_README.md below
```

---

## 📤 PART 2: PUSH TO GITHUB

### Step 2.1: Initialize Git (if not already)

```bash
cd A:\MD\fuel

# Initialize git
git init

# Add .gitignore
git add .gitignore

# Check what will be committed
git status
```

### Step 2.2: Create GitHub Repository

**On GitHub.com:**
1. Go to https://github.com
2. Click "New Repository"
3. Name: `jalikoi-analytics` (or your preferred name)
4. Description: "ML-powered fuel station analytics platform"
5. Choose: **Private** (if you have sensitive code)
6. **Do NOT** initialize with README (you already have files)
7. Click "Create Repository"

### Step 2.3: Connect Local to GitHub

GitHub will show you commands. Use these:

```bash
cd A:\MD\fuel

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/jalikoi-analytics.git

# Check remote
git remote -v
```

### Step 2.4: Commit and Push

```bash
# Add all files (respecting .gitignore)
git add .

# Commit
git commit -m "Initial commit: Fuel Analytics Platform with ML"

# Push to GitHub
git push -u origin main
```

If it asks for `main` vs `master`:
```bash
git branch -M main
git push -u origin main
```

**⚠️ IMPORTANT: Verify db_config.py was NOT pushed!**

```bash
# Check files on GitHub
# db_config.py should NOT be there
# db_config_template.py SHOULD be there
```

---

## 🔧 PART 3: PREPARE SEPARATE REPOSITORIES (OPTIONAL BUT RECOMMENDED)

For better organization, split into 2 repos:

### Option A: Separate Repos (Recommended)

**Backend Repo:**
```bash
cd A:\MD\fuel
git init
git remote add origin https://github.com/YOUR_USERNAME/jalikoi-analytics-backend.git
git add .
git commit -m "Backend: API and ML models"
git push -u origin main
```

**Frontend Repo:**
```bash
cd A:\MD\fuel_frontend
git init
git remote add origin https://github.com/YOUR_USERNAME/jalikoi-analytics-frontend.git
git add .
git commit -m "Frontend: React dashboard"
git push -u origin main
```

### Option B: Monorepo (Single Repo)

Keep both in one repo with this structure:
```
jalikoi-analytics/
├── backend/
│   ├── (all backend files)
│   └── requirements.txt
├── frontend/
│   ├── (all frontend files)
│   └── package.json
└── README.md
```

---

## 🖥️ PART 4: SERVER SETUP (Ubuntu 22.04 - DigitalOcean)

### Step 4.1: Create Droplet

**On DigitalOcean:**
1. Create Droplet
2. Choose: Ubuntu 22.04 LTS
3. Choose Plan: 
   - Basic: $12/month (2GB RAM) - Minimum
   - Recommended: $24/month (4GB RAM) - Better for ML
4. Add SSH Key (Generate if you don't have one)
5. Choose Datacenter: Closest to your users
6. Create Droplet

**Get your server IP:**
```
Your Droplet IP: 123.456.789.012
```

### Step 4.2: Initial Server Login

**From Windows (use PowerShell or Windows Terminal):**

```bash
# SSH into server
ssh root@YOUR_SERVER_IP

# Update system
apt update && apt upgrade -y

# Install essentials
apt install -y build-essential git curl wget
```

### Step 4.3: Create Non-Root User (Security Best Practice)

```bash
# Create user
adduser jalikoi

# Add to sudo group
usermod -aG sudo jalikoi

# Switch to new user
su - jalikoi

# From now on, use this user (not root)
```

### Step 4.4: Setup SSH Key for New User

**On your Windows machine:**
```bash
# If you don't have SSH key:
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

**Copy key to server:**
```bash
# From Windows
ssh-copy-id jalikoi@YOUR_SERVER_IP

# Or manually:
# 1. Copy your public key from: C:\Users\YourName\.ssh\id_rsa.pub
# 2. On server, create: mkdir -p ~/.ssh
# 3. Add key: nano ~/.ssh/authorized_keys (paste key)
# 4. Set permissions: chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
```

### Step 4.5: Install Python 3.11+

```bash
# Update package list
sudo apt update

# Install Python
sudo apt install -y python3 python3-pip python3-venv

# Verify
python3 --version  # Should be 3.10+
```

### Step 4.6: Install Node.js (for Frontend)

```bash
# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify
node --version  # Should be v20.x
npm --version
```

### Step 4.7: Install Nginx (Web Server)

```bash
sudo apt install -y nginx

# Start and enable
sudo systemctl start nginx
sudo systemctl enable nginx

# Test: Visit http://YOUR_SERVER_IP in browser
# Should see "Welcome to nginx"
```

### Step 4.8: Install MySQL (if not using external DB)

**If database is on same server:**

```bash
sudo apt install -y mysql-server

# Secure installation
sudo mysql_secure_installation

# Create database and user
sudo mysql
```

**In MySQL:**
```sql
CREATE DATABASE jalikoi_analytics;
CREATE USER 'jalikoi_user'@'localhost' IDENTIFIED BY 'STRONG_PASSWORD_HERE';
GRANT ALL PRIVILEGES ON jalikoi_analytics.* TO 'jalikoi_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## 🚀 PART 5: DEPLOY BACKEND

### Step 5.1: Clone Repository

```bash
# Create project directory
cd ~
mkdir projects
cd projects

# Clone your repo
git clone https://github.com/YOUR_USERNAME/jalikoi-analytics.git
cd jalikoi-analytics

# Or if separate repos:
git clone https://github.com/YOUR_USERNAME/jalikoi-analytics-backend.git backend
cd backend
```

### Step 5.2: Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 5.3: Configure Database

```bash
# Copy template
cp db_config_template.py db_config.py

# Edit with your credentials
nano db_config.py
```

**Update with your actual credentials:**
```python
DB_CONFIG = {
    'host': 'localhost',  # or external DB host
    'port': 3306,
    'user': 'jalikoi_user',
    'password': 'your_actual_password',
    'database': 'jalikoi_analytics'
}
```

**Save:** `Ctrl+O`, `Enter`, `Ctrl+X`

### Step 5.4: Train ML Models

```bash
# Make sure venv is activated
source venv/bin/activate

# Train models (takes 5-10 minutes)
python train_ml_models.py
```

**Verify models created:**
```bash
ls -la ml_models/
# Should see: ml_models.pkl, metadata.json
```

### Step 5.5: Test API Locally

```bash
# Test run
python jalikoi_analytics_api_ml.py

# Should see:
# ✓ ML Engine initialized
# ML Models Status: ✓ Trained
# API running on http://0.0.0.0:8000
```

**Test from another terminal:**
```bash
curl http://localhost:8000/api/health
# Should return JSON with success: true
```

**Stop test:** `Ctrl+C`

### Step 5.6: Setup Systemd Service (Run API as Service)

**Create service file:**
```bash
sudo nano /etc/systemd/system/jalikoi-api.service
```

**Add this content:**
```ini
[Unit]
Description=Jalikoi Analytics API
After=network.target

[Service]
Type=simple
User=jalikoi
WorkingDirectory=/home/jalikoi/projects/jalikoi-analytics
Environment="PATH=/home/jalikoi/projects/jalikoi-analytics/venv/bin"
ExecStart=/home/jalikoi/projects/jalikoi-analytics/venv/bin/python jalikoi_analytics_api_ml.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable (start on boot)
sudo systemctl enable jalikoi-api

# Start service
sudo systemctl start jalikoi-api

# Check status
sudo systemctl status jalikoi-api

# View logs
sudo journalctl -u jalikoi-api -f
```

### Step 5.7: Configure Nginx for API

**Create Nginx config:**
```bash
sudo nano /etc/nginx/sites-available/jalikoi-api
```

**Add this:**
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;  # Change this!

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/jalikoi-api /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

**Test API:**
```bash
curl http://YOUR_SERVER_IP/api/health
# Should return success!
```

---

## 🎨 PART 6: DEPLOY FRONTEND

### Step 6.1: Clone Frontend (if separate repo)

```bash
cd ~/projects
git clone https://github.com/YOUR_USERNAME/jalikoi-analytics-frontend.git frontend
cd frontend
```

### Step 6.2: Update API URL

**Edit API endpoint:**
```bash
nano src/App.js
```

**Change from:**
```javascript
const API_URL = 'http://localhost:8000';
```

**To:**
```javascript
const API_URL = 'http://api.yourdomain.com';  // Or your server IP
```

### Step 6.3: Build Production Version

```bash
# Install dependencies
npm install

# Build for production
npm run build

# This creates: build/ folder with optimized files
```

### Step 6.4: Deploy to Nginx

```bash
# Copy build to web directory
sudo mkdir -p /var/www/jalikoi
sudo cp -r build/* /var/www/jalikoi/

# Set permissions
sudo chown -R www-data:www-data /var/www/jalikoi
```

### Step 6.5: Configure Nginx for Frontend

```bash
sudo nano /etc/nginx/sites-available/jalikoi-frontend
```

**Add this:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;  # Change this!

    root /var/www/jalikoi;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**Enable:**
```bash
sudo ln -s /etc/nginx/sites-available/jalikoi-frontend /etc/nginx/sites-enabled/

sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔒 PART 7: SETUP SSL (HTTPS)

### Step 7.1: Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Step 7.2: Get SSL Certificates

**For API:**
```bash
sudo certbot --nginx -d api.yourdomain.com
```

**For Frontend:**
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**Follow prompts:**
- Enter email
- Agree to terms
- Choose redirect HTTP to HTTPS: Yes

**Auto-renewal is configured automatically!**

**Test renewal:**
```bash
sudo certbot renew --dry-run
```

---

## 📊 PART 8: MONITORING & MAINTENANCE

### Step 8.1: Check Service Status

```bash
# API status
sudo systemctl status jalikoi-api

# API logs
sudo journalctl -u jalikoi-api -f

# Nginx status
sudo systemctl status nginx

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Step 8.2: Update Application

**When you push changes to GitHub:**

```bash
# SSH to server
ssh jalikoi@YOUR_SERVER_IP

# Pull latest changes
cd ~/projects/jalikoi-analytics
git pull

# Restart API (backend changes)
sudo systemctl restart jalikoi-api

# Rebuild frontend (if frontend changes)
cd ~/projects/frontend
git pull
npm install
npm run build
sudo cp -r build/* /var/www/jalikoi/
```

### Step 8.3: Backup ML Models

```bash
# Create backup script
nano ~/backup_models.sh
```

**Add:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf ~/backups/ml_models_$DATE.tar.gz ~/projects/jalikoi-analytics/ml_models/
# Keep only last 7 backups
ls -t ~/backups/ml_models_*.tar.gz | tail -n +8 | xargs rm -f
```

**Make executable:**
```bash
chmod +x ~/backup_models.sh
mkdir -p ~/backups
```

**Add to cron (daily backup):**
```bash
crontab -e

# Add this line:
0 2 * * * /home/jalikoi/backup_models.sh
```

### Step 8.4: Setup Firewall

```bash
# Install UFW
sudo apt install -y ufw

# Allow SSH
sudo ufw allow OpenSSH

# Allow HTTP/HTTPS
sudo ufw allow 'Nginx Full'

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## ✅ DEPLOYMENT CHECKLIST

### Pre-Deployment:
- [ ] `.gitignore` created
- [ ] `db_config_template.py` created
- [ ] Sensitive files excluded
- [ ] Code pushed to GitHub
- [ ] README.md created

### Server Setup:
- [ ] Droplet created
- [ ] Non-root user created
- [ ] SSH key configured
- [ ] Python 3.11+ installed
- [ ] Node.js 20+ installed
- [ ] Nginx installed
- [ ] MySQL configured (if applicable)

### Backend Deployment:
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `db_config.py` configured
- [ ] ML models trained
- [ ] API tested locally
- [ ] Systemd service created
- [ ] Nginx configured
- [ ] API accessible via domain/IP

### Frontend Deployment:
- [ ] Repository cloned
- [ ] API URL updated
- [ ] Dependencies installed
- [ ] Production build created
- [ ] Files copied to `/var/www`
- [ ] Nginx configured
- [ ] Frontend accessible

### Security:
- [ ] SSL certificates installed
- [ ] HTTPS working
- [ ] Firewall configured
- [ ] Database secured

### Monitoring:
- [ ] Service logs checked
- [ ] Backup script created
- [ ] Monitoring setup

---

## 🆘 TROUBLESHOOTING

### API Not Starting

```bash
# Check logs
sudo journalctl -u jalikoi-api -n 50

# Common issues:
# 1. Database connection failed → Check db_config.py
# 2. Port already in use → Check: sudo lsof -i :8000
# 3. Missing dependencies → pip install -r requirements.txt
```

### Frontend Not Loading

```bash
# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Common issues:
# 1. API URL incorrect → Check src/App.js
# 2. Build failed → Run: npm run build
# 3. Permissions → sudo chown -R www-data:www-data /var/www/jalikoi
```

### SSL Not Working

```bash
# Verify Certbot
sudo certbot certificates

# Renew manually
sudo certbot renew

# Check Nginx config
sudo nginx -t
```

---

## 📝 QUICK COMMANDS REFERENCE

```bash
# Restart API
sudo systemctl restart jalikoi-api

# View API logs
sudo journalctl -u jalikoi-api -f

# Restart Nginx
sudo systemctl restart nginx

# Update application
cd ~/projects/jalikoi-analytics && git pull
sudo systemctl restart jalikoi-api

# Rebuild frontend
cd ~/projects/frontend && git pull && npm run build
sudo cp -r build/* /var/www/jalikoi/

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
htop
```

---

## 🎯 PRODUCTION BEST PRACTICES

1. **Use Environment Variables** for sensitive data
2. **Setup Automated Backups** (database + ML models)
3. **Monitor Server Resources** (CPU, RAM, Disk)
4. **Setup Logging** (centralized logging solution)
5. **Use PM2 or Gunicorn** instead of direct Python (optional)
6. **Setup Rate Limiting** on API endpoints
7. **Enable CORS** properly
8. **Use PostgreSQL** instead of MySQL (optional, better for analytics)
9. **Setup Redis** for caching (optional)
10. **Setup CI/CD** with GitHub Actions (optional)

---

## 📞 SUPPORT

If you encounter issues:
1. Check logs first
2. Verify configurations
3. Google the error message
4. Check DigitalOcean documentation
5. Ask in relevant forums

---

**Deployment complete! Your analytics platform is now live! 🎉**

Access:
- Frontend: https://yourdomain.com
- API: https://api.yourdomain.com
- API Docs: https://api.yourdomain.com/docs
