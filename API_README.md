# 🚀 Jalikoi Analytics REST API

Transform your customer analytics into accessible, flexible API endpoints!

## ⚡ Quick Start

### 1. Install
```bash
pip install -r requirements_api.txt
```

### 2. Start
```bash
start_api.bat
```
or
```bash
python jalikoi_analytics_api.py
```

### 3. Test
Open Postman → Import `Jalikoi_Analytics_API.postman_collection.json` → Start testing!

**API Running at:** http://localhost:8000  
**Documentation:** http://localhost:8000/docs

---

## 📋 What You Get

✅ **Yesterday's insights** by default  
✅ **Custom date ranges** for any period  
✅ **All historical data** with one request  
✅ **Period comparisons** (current vs previous)  
✅ **Visualization data** for dashboards  
✅ **25+ pre-built Postman requests**  

---

## 🎯 Common Requests

### Yesterday's Performance
```bash
GET http://localhost:8000/api/insights
```

### Last Week with Comparison
```bash
GET http://localhost:8000/api/insights?period=week&compare=true
```

### Custom Date Range
```bash
GET http://localhost:8000/api/insights?start_date=2025-10-01&end_date=2025-10-27
```

### All Historical Data
```bash
GET http://localhost:8000/api/insights?period=all
```

### Get Chart Data
```bash
GET http://localhost:8000/api/visualizations
```

---

## 📊 Response Preview

```json
{
  "success": true,
  "data": {
    "overview": {
      "total_revenue": 45000000,
      "total_transactions": 1250,
      "success_rate": 94.4,
      "currency": "RWF"
    },
    "customers": {
      "total_customers": 450,
      "active_customers_30d": 380
    },
    "churn_analysis": {
      "high_risk_customers": 50,
      "revenue_at_risk": 5000000
    },
    "clv_projection": {
      "total_6m_projection": 180000000
    }
  }
}
```

---

## 📁 Files Created

| File | Description |
|------|-------------|
| `jalikoi_analytics_api.py` | Main API application |
| `API_DOCUMENTATION.md` | Complete API reference |
| `API_QUICK_START.md` | Quick start guide |
| `API_TRANSFORMATION_SUMMARY.md` | What was created and why |
| `Jalikoi_Analytics_API.postman_collection.json` | Postman collection (25+ requests) |
| `requirements_api.txt` | Python dependencies |
| `start_api.bat` | Windows startup script |

---

## 🎨 Postman Collection

**Import the collection to get:**
- Health checks
- Default period queries (yesterday, week, month, all)
- Custom date ranges
- Period comparisons
- Visualization endpoints
- All pre-configured and ready to use!

---

## 📖 Full Documentation

**Quick Start:** `API_QUICK_START.md`  
**Complete Reference:** `API_DOCUMENTATION.md`  
**Interactive Docs:** http://localhost:8000/docs (when running)

---

## 🔥 Key Features

### Default Behavior
No parameters = yesterday's data. Perfect for daily monitoring.

### Flexible Queries
- Specific dates: `start_date=2025-10-01&end_date=2025-10-27`
- Pre-defined: `period=week`, `period=month`, `period=all`

### Built-in Comparison
Add `compare=true` to see percentage changes vs previous period.

### Comprehensive Insights
Every response includes:
- Revenue metrics
- Transaction analytics
- Customer segmentation
- Churn risk analysis
- CLV projections
- Top performers
- Time-based trends

---

## 🛠️ Built With

- **FastAPI** - Modern, fast web framework
- **Uvicorn** - Lightning-fast ASGI server
- **Pandas** - Data analysis
- **MySQL** - Database connection
- **Pydantic** - Data validation

---

## 📞 Need Help?

1. **Quick Start:** Read `API_QUICK_START.md`
2. **Full Guide:** Check `API_DOCUMENTATION.md`
3. **Interactive:** Visit http://localhost:8000/docs
4. **Examples:** Use the Postman collection

---

## ✅ Health Check

After starting the API, verify it's working:

```bash
GET http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database_available": true,
  "timestamp": "2025-10-29T10:30:00"
}
```

---

## 🎉 You're Ready!

Your analytics are now accessible via API. Start testing in Postman and build amazing integrations!

**Happy coding! 🚀**
