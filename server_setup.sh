#!/bin/bash
# 🚀 SERVER DEPLOYMENT SCRIPT
# Run this on your Ubuntu server after cloning the repo

set -e  # Exit on error

echo "=================================="
echo "JALIKOI ANALYTICS - SERVER SETUP"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo -e "${RED}Please run as root or with sudo${NC}"
   exit 1
fi

echo -e "${GREEN}✓${NC} Running as root"
echo ""

# Update system
echo "Updating system packages..."
apt update && apt upgrade -y
echo -e "${GREEN}✓${NC} System updated"
echo ""

# Install Python
echo "Installing Python 3..."
apt install -y python3 python3-pip python3-venv
echo -e "${GREEN}✓${NC} Python installed: $(python3 --version)"
echo ""

# Install Node.js
echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
echo -e "${GREEN}✓${NC} Node.js installed: $(node --version)"
echo ""

# Install Nginx
echo "Installing Nginx..."
apt install -y nginx
systemctl start nginx
systemctl enable nginx
echo -e "${GREEN}✓${NC} Nginx installed and started"
echo ""

# Install MySQL
read -p "Install MySQL on this server? (y/n): " install_mysql
if [ "$install_mysql" = "y" ]; then
    echo "Installing MySQL..."
    apt install -y mysql-server
    echo -e "${GREEN}✓${NC} MySQL installed"
    echo -e "${YELLOW}⚠${NC} Run: sudo mysql_secure_installation"
    echo ""
fi

# Install Certbot for SSL
echo "Installing Certbot..."
apt install -y certbot python3-certbot-nginx
echo -e "${GREEN}✓${NC} Certbot installed"
echo ""

# Setup UFW Firewall
echo "Configuring firewall..."
ufw --force enable
ufw allow OpenSSH
ufw allow 'Nginx Full'
echo -e "${GREEN}✓${NC} Firewall configured"
echo ""

# Create user
read -p "Create non-root user? (y/n): " create_user
if [ "$create_user" = "y" ]; then
    read -p "Enter username: " username
    adduser $username
    usermod -aG sudo $username
    echo -e "${GREEN}✓${NC} User $username created"
    echo ""
fi

echo "=================================="
echo "✅ SERVER SETUP COMPLETE!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Switch to your user: su - $username"
echo "2. Clone your repository"
echo "3. Run: bash deploy_backend.sh"
echo "4. Run: bash deploy_frontend.sh"
echo ""
