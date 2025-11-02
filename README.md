# 🚀 Jalikoi Analytics Platform

> ML-powered customer analytics and predictive insights for fuel station networks

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.0+-blue.svg)](https://reactjs.org/)

## 📋 Overview

Jalikoi Analytics is a comprehensive analytics platform that provides:

- 📊 **Real-time Dashboard** - Monitor key metrics and performance
- 🤖 **ML Predictions** - Churn prediction & revenue forecasting
- 👥 **Customer Segmentation** - 8 AI-discovered customer segments
- 🛡️ **Anomaly Detection** - Fraud prevention & suspicious transaction monitoring
- 📈 **Advanced Analytics** - RFM analysis, CLV calculation, trend analysis

## ✨ Features

### Machine Learning Models
- **Churn Prediction**: Random Forest classifier (95%+ accuracy)
- **Revenue Forecasting**: Gradient Boosting regressor
- **Customer Segmentation**: K-Means clustering (8 segments)
- **Anomaly Detection**: Isolation Forest for fraud detection

### Dashboard Features
- Real-time metrics and KPIs
- Interactive charts and visualizations
- Date range filtering
- Customer health monitoring
- Station performance analytics
- Payment status tracking

## 🛠️ Tech Stack

### Backend
- Python 3.10+
- FastAPI - REST API framework
- scikit-learn - Machine learning
- pandas/numpy - Data processing
- MySQL - Database
- uvicorn - ASGI server

### Frontend
- React 18
- Recharts - Data visualization
- Axios - HTTP client
- Modern responsive UI

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher
- MySQL 8.0 or higher
- Git

### Quick Start (Local Development)

**1. Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/jalikoi-analytics-backend.git
cd jalikoi-analytics-backend
```

**2. Setup Backend:**
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure database
cp db_config_template.py db_config.py
# Edit db_config.py with your credentials

# Train ML models
python train_ml_models.py

# Start API
python jalikoi_analytics_api_ml.py
```

**3. Setup Frontend:**
```bash
cd ../jalikoi-analytics-frontend
npm install
npm start
```

**4. Access:**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🚀 Production Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete deployment instructions to Ubuntu server.

**Quick Deploy:**
```bash
# On server
bash server_setup.sh
bash deploy_backend.sh
```

## 📊 API Endpoints

### Core Analytics
- `GET /api/insights` - Key metrics and statistics
- `GET /api/visualizations` - Chart data

### ML Endpoints
- `GET /api/ml/churn-predictions` - Customer churn predictions
- `GET /api/ml/revenue-forecast` - Revenue forecasting
- `GET /api/ml/segments` - Customer segmentation
- `GET /api/ml/anomalies` - Anomaly detection
- `GET /api/ml/model-info` - Model status and metadata

### Admin
- `POST /api/ml/train` - Trigger model retraining

See full API documentation at `/docs` when running.

## 🎯 Customer Segments

The platform automatically discovers 8 customer segments:

1. **🌟 Premium VIPs** - Highest value customers
2. **💚 Loyal Regulars** - Consistent, reliable customers
3. **📈 Growth Potential** - Rising stars
4. **⚠️ At Risk** - Need immediate intervention
5. **🔵 Occasional Users** - Infrequent usage
6. **🆕 New Customers** - Recent sign-ups
7. **😴 Dormant** - Inactive but recoverable
8. **❌ Lost** - Churned customers

See [SEGMENT_CRITERIA_EXPLAINED.md](SEGMENT_CRITERIA_EXPLAINED.md) for details.

## 📈 ML Model Performance

| Model | Metric | Performance |
|-------|--------|-------------|
| Churn Prediction | Accuracy | 95-98% |
| Churn Prediction | Precision | 92-96% |
| Revenue Forecasting | R² Score | 0.85-0.92 |
| Customer Segmentation | Clusters | 8 segments |
| Anomaly Detection | Detection Rate | 5% flagged |

## 🔧 Configuration

### Database Configuration

Edit `db_config.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database'
}
```

### Environment Variables (Optional)

Create `.env`:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database
API_PORT=8000
```

## 📝 Development

### Running Tests
```bash
# Backend tests
python -m pytest tests/

# Frontend tests
npm test
```

### Code Quality
```bash
# Format code
black *.py

# Lint
pylint *.py
```

### Updating Dependencies
```bash
# Backend
pip freeze > requirements.txt

# Frontend
npm install
```

## 🔄 Updating Application

### Pull Latest Changes
```bash
git pull origin main
```

### Update Backend
```bash
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart jalikoi-api
```

### Update Frontend
```bash
npm install
npm run build
sudo cp -r build/* /var/www/jalikoi/
```

## 📊 Monitoring

### Check Service Status
```bash
sudo systemctl status jalikoi-api
```

### View Logs
```bash
# API logs
sudo journalctl -u jalikoi-api -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
```

## 🐛 Troubleshooting

### API Won't Start
```bash
# Check logs
sudo journalctl -u jalikoi-api -n 50

# Common fixes:
# 1. Check database connection
# 2. Verify ML models trained
# 3. Check port availability
```

### Frontend Build Fails
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Database Connection Issues
```bash
# Test connection
python -c "from database_connector import JalikoiDatabaseConnector; from db_config import DB_CONFIG; print('OK')"
```

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment
- [Pre-Deployment Checklist](PRE_DEPLOYMENT_CHECKLIST.md) - Before pushing to GitHub
- [Segment Criteria](SEGMENT_CRITERIA_EXPLAINED.md) - How segments are created
- [API Documentation](API_DOCUMENTATION.md) - Complete API reference

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- FastAPI for the excellent API framework
- scikit-learn for ML capabilities
- React team for the frontend framework
- DigitalOcean for hosting

## 📞 Support

For support:
- Open an issue on GitHub
- Email: support@jalikoi.com
- Documentation: [Link to docs]

## 🗺️ Roadmap

- [ ] Add more ML models (RNN for time series)
- [ ] Implement recommendation engine
- [ ] Add mobile app
- [ ] Multi-language support
- [ ] Advanced reporting features
- [ ] Integration with payment gateways
- [ ] Real-time notifications

---

**⭐ Star this repo if you find it useful!**

**Built with ❤️ for data-driven decision making**
