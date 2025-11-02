#!/bin/bash
# 🚀 BACKEND DEPLOYMENT SCRIPT
# Run this in your backend directory

set -e

echo "=================================="
echo "DEPLOYING BACKEND"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get current directory
BACKEND_DIR=$(pwd)
echo "Backend directory: $BACKEND_DIR"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment created"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo -e "${GREEN}✓${NC} Pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"
echo ""

# Configure database
if [ ! -f "db_config.py" ]; then
    echo -e "${YELLOW}⚠${NC} db_config.py not found!"
    read -p "Create from template? (y/n): " create_config
    if [ "$create_config" = "y" ]; then
        cp db_config_template.py db_config.py
        echo -e "${GREEN}✓${NC} Created db_config.py"
        echo -e "${YELLOW}⚠${NC} IMPORTANT: Edit db_config.py with your credentials!"
        echo "Run: nano db_config.py"
        exit 0
    fi
else
    echo -e "${GREEN}✓${NC} db_config.py exists"
fi
echo ""

# Test database connection
echo "Testing database connection..."
python3 -c "from database_connector import JalikoiDatabaseConnector; from db_config import DB_CONFIG; print('Connection test passed!')" || {
    echo -e "${YELLOW}⚠${NC} Database connection failed!"
    echo "Check db_config.py settings"
    exit 1
}
echo -e "${GREEN}✓${NC} Database connection successful"
echo ""

# Train ML models
read -p "Train ML models now? (y/n - takes 5-10 min): " train_models
if [ "$train_models" = "y" ]; then
    echo "Training ML models..."
    python3 train_ml_models.py
    echo -e "${GREEN}✓${NC} Models trained"
fi
echo ""

# Create systemd service
echo "Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/jalikoi-api.service"

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Jalikoi Analytics API
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$BACKEND_DIR
Environment="PATH=$BACKEND_DIR/venv/bin"
ExecStart=$BACKEND_DIR/venv/bin/python jalikoi_analytics_api_ml.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓${NC} Service file created"
echo ""

# Enable and start service
echo "Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable jalikoi-api
sudo systemctl start jalikoi-api
echo -e "${GREEN}✓${NC} Service started"
echo ""

# Check service status
sudo systemctl status jalikoi-api --no-pager

echo ""
echo "=================================="
echo "✅ BACKEND DEPLOYED!"
echo "=================================="
echo ""
echo "API running on: http://localhost:8000"
echo "Test: curl http://localhost:8000/api/health"
echo ""
echo "View logs: sudo journalctl -u jalikoi-api -f"
echo "Restart: sudo systemctl restart jalikoi-api"
echo ""
echo "Next: Configure Nginx reverse proxy"
echo ""
