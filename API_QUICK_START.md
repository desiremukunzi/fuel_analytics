# Jalikoi Analytics API - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements_api.txt
```

### Step 2: Start the API
Double-click `start_api.bat` or run:
```bash
python jalikoi_analytics_api.py
```

### Step 3: Test in Postman
1. Open Postman
2. Import `Jalikoi_Analytics_API.postman_collection.json`
3. Start testing!

---

## 📱 Quick Test in Browser

Once the API is running, open these URLs in your browser:

**Health Check:**
```
http://localhost:8000/api/health
```

**Yesterday's Insights:**
```
http://localhost:8000/api/insights
```

**Interactive Documentation:**
```
http://localhost:8000/docs
```

---

## 🎯 Common Use Cases

### 1. Get Yesterday's Performance (Default)
```bash
GET http://localhost:8000/api/insights
```
Returns complete analytics for yesterday.

### 2. Get Last Week with Comparison
```bash
GET http://localhost:8000/api/insights?period=week&compare=true
```
Returns last week's data compared to the previous week.

### 3. Get Specific Date Range
```bash
GET http://localhost:8000/api/insights?start_date=2025-10-01&end_date=2025-10-27
```
Returns analytics for October 1-27, 2025.

### 4. Get All Historical Data
```bash
GET http://localhost:8000/api/insights?period=all
```
Returns insights since inception.

### 5. Get Chart Data
```bash
GET http://localhost:8000/api/visualizations
```
Returns chart-ready data for frontend visualization.

---

## 📊 Understanding the Response

### Key Metrics You'll Get:

**Revenue Metrics:**
- Total revenue (RWF)
- Average transaction value
- Revenue by customer segment
- 6-month CLV projection

**Transaction Metrics:**
- Total transactions
- Success rate
- Failed transactions
- Transactions by hour/day

**Customer Metrics:**
- Total customers
- Active customers (30 days)
- Customer segments (Champions, Loyal, At Risk, etc.)
- Churn risk analysis

**Operational Metrics:**
- Top performing stations
- Fuel volume sold
- Payment method usage
- Peak transaction hours

---

## 🧪 Testing in Postman

### Import the Collection
1. Open Postman
2. Click **Import**
3. Select `Jalikoi_Analytics_API.postman_collection.json`
4. Collection will appear with all pre-configured requests

### Folder Structure:
1. **Health & Status** - Check if API is working
2. **Insights - Default & Pre-defined Periods** - Quick access to common periods
3. **Insights - Custom Date Ranges** - Specify exact dates
4. **Insights - With Comparisons** - Compare periods
5. **Visualizations** - Get chart data

### Environment Variable
The collection uses `{{base_url}}` = `http://localhost:8000`
You can change this if your API runs on a different host/port.

---

## 📈 Sample Response Structure

```json
{
  "success": true,
  "data": {
    "period": {
      "start_date": "2025-10-28",
      "end_date": "2025-10-28",
      "total_days": 1
    },
    "overview": {
      "total_transactions": 1250,
      "successful_transactions": 1180,
      "total_revenue": 45000000,
      "success_rate": 94.4,
      "currency": "RWF"
    },
    "customers": {
      "total_customers": 450,
      "active_customers_30d": 380
    },
    "segmentation": {
      "segment_distribution": {...},
      "segment_revenue": {...}
    },
    "churn_analysis": {
      "high_risk_customers": 50,
      "revenue_at_risk": 5000000
    },
    "clv_projection": {
      "total_6m_projection": 180000000
    },
    "top_customers": [...],
    "station_performance": [...],
    "time_analysis": {...}
  }
}
```

---

## 🔥 Power Tips

### Tip 1: Use Comparison for Trends
Always add `&compare=true` to see if metrics are improving or declining:
```
/api/insights?period=week&compare=true
```

### Tip 2: Filter by Date for Reports
Create monthly/quarterly reports by specifying date ranges:
```
/api/insights?start_date=2025-10-01&end_date=2025-10-31
```

### Tip 3: Check Churn Daily
Monitor yesterday's churn risk daily:
```
/api/insights
```
Look at `churn_analysis.high_risk_customers` field.

### Tip 4: Use Visualization Endpoint for Dashboards
Get pre-formatted chart data:
```
/api/visualizations?start_date=2025-10-27&end_date=2025-10-27
```

### Tip 5: Identify Revenue at Risk
Check `churn_analysis.revenue_at_risk` to see potential revenue loss.

---

## 🎨 Frontend Integration Example

### JavaScript (Fetch API)
```javascript
// Get yesterday's insights
async function getInsights() {
  const response = await fetch('http://localhost:8000/api/insights');
  const data = await response.json();
  
  console.log('Revenue:', data.data.overview.total_revenue, 'RWF');
  console.log('Customers:', data.data.customers.total_customers);
  console.log('High Risk:', data.data.churn_analysis.high_risk_customers);
}
```

### Python (Requests)
```python
import requests

# Get weekly insights with comparison
response = requests.get(
    'http://localhost:8000/api/insights',
    params={'period': 'week', 'compare': True}
)

data = response.json()
revenue_change = data['comparison']['changes']['revenue_change']
print(f"Revenue change: {revenue_change}%")
```

---

## ⚠️ Troubleshooting

### API won't start
- **Check port 8000**: Make sure nothing else is using it
- **Check database config**: Verify `db_config.py` has correct credentials
- **Install dependencies**: Run `pip install -r requirements_api.txt`

### "No data found for specified period"
- Check if database has data for those dates
- Try `period=all` to see all available data
- Verify database connection is working

### Slow responses
- Use date ranges instead of `period=all` for large datasets
- Disable comparison when not needed
- Check database indexes

---

## 📚 Next Steps

1. **Read Full Documentation**: See `API_DOCUMENTATION.md` for complete details
2. **Test All Endpoints**: Try all requests in the Postman collection
3. **Build Dashboards**: Use `/api/visualizations` to create charts
4. **Automate Reports**: Schedule daily API calls for automated reporting
5. **Monitor Churn**: Set up alerts for high churn risk

---

## 🆘 Need Help?

- **API Documentation**: http://localhost:8000/docs (when API is running)
- **Full Guide**: `API_DOCUMENTATION.md`
- **Postman Collection**: `Jalikoi_Analytics_API.postman_collection.json`

---

## ✅ Quick Checklist

- [ ] Dependencies installed (`pip install -r requirements_api.txt`)
- [ ] Database configured (`db_config.py`)
- [ ] API started (`start_api.bat`)
- [ ] Health check passed (`http://localhost:8000/api/health`)
- [ ] Postman collection imported
- [ ] First test successful

**You're ready to go! 🎉**
