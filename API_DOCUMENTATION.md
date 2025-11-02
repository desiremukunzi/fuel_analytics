# Jalikoi Analytics REST API

## Overview
REST API for retrieving customer analytics, insights, and visualizations from the Jalikoi fuel payment system.

## Features
- ✅ **Default Yesterday's Data**: Get insights for yesterday automatically
- ✅ **Date Range Queries**: Specify custom date ranges
- ✅ **All Historical Data**: Retrieve insights since inception
- ✅ **Period Comparison**: Compare current period with previous period
- ✅ **Visualization Data**: Get chart-ready data for frontend
- ✅ **Postman Ready**: Test all endpoints in Postman

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements_api.txt
```

### 2. Configure Database
Make sure `db_config.py` is configured with your MySQL credentials.

### 3. Start API Server
```bash
python jalikoi_analytics_api.py
```

Or using uvicorn directly:
```bash
uvicorn jalikoi_analytics_api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json

## API Endpoints

### 1. Health Check
**GET** `/api/health`

Check if API is running and database is available.

**Example:**
```bash
curl http://localhost:8000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "database_available": true,
  "timestamp": "2025-10-29T10:30:00"
}
```

---

### 2. Get Insights (Default: Yesterday)
**GET** `/api/insights`

Get insights for yesterday by default.

**Example:**
```bash
curl http://localhost:8000/api/insights
```

**Response Structure:**
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
      "failed_transactions": 70,
      "success_rate": 94.4,
      "total_revenue": 45000000,
      "avg_transaction_value": 38135.59,
      "total_liters_sold": 28500.5,
      "currency": "RWF"
    },
    "customers": {
      "total_customers": 450,
      "active_customers_30d": 380,
      "avg_customer_value": 100000,
      "avg_transactions_per_customer": 2.62
    },
    "segmentation": {
      "segment_distribution": {
        "Champions": 45,
        "Loyal Customers": 120,
        "At Risk": 30,
        ...
      },
      "segment_revenue": {
        "Champions": 15000000,
        "Loyal Customers": 18000000,
        ...
      }
    },
    "churn_analysis": {
      "churn_distribution": {
        "Low Risk": 300,
        "Medium Risk": 100,
        "High Risk": 50
      },
      "high_risk_customers": 50,
      "revenue_at_risk": 5000000,
      "churn_rate": 11.11
    },
    "clv_projection": {
      "total_6m_projection": 180000000,
      "avg_customer_clv": 400000
    },
    "top_customers": [...],
    "station_performance": [...],
    "time_analysis": {...}
  }
}
```

---

### 3. Get Insights for Date Range
**GET** `/api/insights?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

Get insights for a specific date range.

**Examples:**

Last week:
```bash
curl "http://localhost:8000/api/insights?start_date=2025-10-21&end_date=2025-10-27"
```

October 2025:
```bash
curl "http://localhost:8000/api/insights?start_date=2025-10-01&end_date=2025-10-31"
```

---

### 4. Get All Historical Data
**GET** `/api/insights?period=all`

Get insights for all data since the beginning.

**Example:**
```bash
curl "http://localhost:8000/api/insights?period=all"
```

---

### 5. Get Insights with Period Comparison
**GET** `/api/insights?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&compare=true`

Get insights with comparison to the previous period.

**Example:**
```bash
curl "http://localhost:8000/api/insights?start_date=2025-10-21&end_date=2025-10-27&compare=true"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "period": {...},
    "overview": {...},
    ...
  },
  "comparison": {
    "previous_period": {
      "start_date": "2025-10-14",
      "end_date": "2025-10-20"
    },
    "changes": {
      "revenue_change": 12.5,
      "transactions_change": 8.3,
      "customers_change": 5.2,
      "avg_transaction_change": 3.8,
      "success_rate_change": 1.2
    },
    "previous_data": {...}
  }
}
```

**Changes Interpretation:**
- Positive numbers = increase
- Negative numbers = decrease
- Null = previous period had zero value

---

### 6. Get Pre-defined Period Insights
**GET** `/api/insights?period=PERIOD`

Available periods:
- `yesterday` - Yesterday's data
- `week` - Last 7 days
- `month` - Last 30 days
- `all` - All historical data

**Examples:**

Last week:
```bash
curl "http://localhost:8000/api/insights?period=week"
```

Last month:
```bash
curl "http://localhost:8000/api/insights?period=month"
```

Last week with comparison:
```bash
curl "http://localhost:8000/api/insights?period=week&compare=true"
```

---

### 7. Get Visualization Data
**GET** `/api/visualizations`

Get chart-ready data for frontend visualization.

**Example:**
```bash
curl "http://localhost:8000/api/visualizations?start_date=2025-10-27&end_date=2025-10-27"
```

**Optional Parameters:**
- `start_date` - Start date (defaults to yesterday)
- `end_date` - End date (defaults to yesterday)
- `chart_type` - Chart type: `revenue`, `segmentation`, `churn`, `all` (defaults to all)

**Response:**
```json
{
  "success": true,
  "period": {
    "start_date": "2025-10-27",
    "end_date": "2025-10-27"
  },
  "charts": {
    "revenue_top_customers": {
      "labels": ["Customer 1001", "Customer 1002", ...],
      "values": [500000, 450000, ...]
    },
    "customer_segmentation": {
      "labels": ["Champions", "Loyal Customers", ...],
      "values": [45, 120, ...]
    },
    "segment_revenue": {
      "labels": ["Champions", "Loyal Customers", ...],
      "values": [15000000, 18000000, ...]
    },
    "churn_distribution": {
      "labels": ["High Risk", "Medium Risk", "Low Risk"],
      "values": [50, 100, 300]
    },
    "revenue_at_risk": {
      "labels": ["High Risk", "Medium Risk", "Low Risk"],
      "values": [5000000, 8000000, 32000000]
    }
  }
}
```

---

## Postman Testing

### Setup Postman Collection

1. **Create New Collection**: "Jalikoi Analytics API"

2. **Set Base URL Variable**:
   - Key: `base_url`
   - Value: `http://localhost:8000`

### Sample Requests

#### 1. Health Check
```
GET {{base_url}}/api/health
```

#### 2. Yesterday's Insights (Default)
```
GET {{base_url}}/api/insights
```

#### 3. Date Range Insights
```
GET {{base_url}}/api/insights?start_date=2025-10-01&end_date=2025-10-27
```

#### 4. All Historical Data
```
GET {{base_url}}/api/insights?period=all
```

#### 5. Last Week with Comparison
```
GET {{base_url}}/api/insights?period=week&compare=true
```

#### 6. Custom Range with Comparison
```
GET {{base_url}}/api/insights?start_date=2025-10-21&end_date=2025-10-27&compare=true
```

#### 7. Visualization Data
```
GET {{base_url}}/api/visualizations?start_date=2025-10-27&end_date=2025-10-27
```

#### 8. Specific Chart Type
```
GET {{base_url}}/api/visualizations?start_date=2025-10-27&end_date=2025-10-27&chart_type=revenue
```

---

## Response Fields Explained

### Overview Section
- `total_transactions` - All transactions (successful + failed)
- `successful_transactions` - Successfully completed payments
- `failed_transactions` - Failed payment attempts
- `success_rate` - Percentage of successful transactions
- `total_revenue` - Total revenue in RWF
- `avg_transaction_value` - Average value per successful transaction
- `total_liters_sold` - Total fuel dispensed in liters

### Customers Section
- `total_customers` - Unique customers in period
- `active_customers_30d` - Customers active in last 30 days
- `avg_customer_value` - Average revenue per customer
- `avg_transactions_per_customer` - Average transaction count

### Segmentation Section
- Customer segments: Champions, Loyal Customers, Potential Loyalists, At Risk, Can't Lose Them, Lost, Hibernating, Need Attention
- Distribution by count and revenue

### Churn Analysis Section
- `churn_distribution` - Customers by risk level
- `high_risk_customers` - Count of high-risk customers
- `revenue_at_risk` - Projected revenue loss from churn
- `churn_rate` - Percentage at high risk

### CLV Projection Section
- `total_6m_projection` - Total projected 6-month customer lifetime value
- `avg_customer_clv` - Average CLV per customer

### Top Customers
- Top 10 customers by revenue with their segment

### Station Performance
- Top 5 stations by revenue with transaction counts and liters

### Time Analysis
- `hourly_distribution` - Transactions by hour of day
- `daily_trend` - Last 7 days trend

---

## Usage Examples

### Python Requests
```python
import requests

# Get yesterday's insights
response = requests.get('http://localhost:8000/api/insights')
data = response.json()
print(f"Revenue: {data['data']['overview']['total_revenue']} RWF")

# Get custom range with comparison
response = requests.get(
    'http://localhost:8000/api/insights',
    params={
        'start_date': '2025-10-01',
        'end_date': '2025-10-27',
        'compare': True
    }
)
data = response.json()
revenue_change = data['comparison']['changes']['revenue_change']
print(f"Revenue change: {revenue_change}%")
```

### JavaScript Fetch
```javascript
// Get yesterday's insights
fetch('http://localhost:8000/api/insights')
  .then(response => response.json())
  .then(data => {
    console.log('Revenue:', data.data.overview.total_revenue);
  });

// Get visualization data
fetch('http://localhost:8000/api/visualizations?start_date=2025-10-27&end_date=2025-10-27')
  .then(response => response.json())
  .then(data => {
    console.log('Chart data:', data.charts);
  });
```

### cURL
```bash
# Get insights with comparison
curl -X GET "http://localhost:8000/api/insights?start_date=2025-10-21&end_date=2025-10-27&compare=true" \
  -H "accept: application/json"
```

---

## Error Handling

### Common Errors

**404 - No Data Found**
```json
{
  "detail": "No data found for specified period"
}
```

**500 - Database Error**
```json
{
  "detail": "Database error: Connection failed"
}
```

**422 - Invalid Date Format**
```json
{
  "detail": [
    {
      "loc": ["query", "start_date"],
      "msg": "Invalid date format. Use YYYY-MM-DD",
      "type": "value_error"
    }
  ]
}
```

---

## Performance Tips

1. **Use Date Ranges**: For large datasets, specify date ranges instead of `period=all`
2. **Disable Comparison**: Set `compare=false` when not needed to reduce processing time
3. **Specific Charts**: Request specific chart types in visualizations endpoint
4. **Caching**: Consider implementing Redis caching for frequently accessed date ranges

---

## Development

### Run in Development Mode
```bash
uvicorn jalikoi_analytics_api:app --reload --host 0.0.0.0 --port 8000
```

### Run in Production Mode
```bash
uvicorn jalikoi_analytics_api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access Interactive Documentation
Visit http://localhost:8000/docs for Swagger UI documentation.

---

## Troubleshooting

### API won't start
1. Check if port 8000 is available
2. Verify database credentials in `db_config.py`
3. Ensure all dependencies are installed: `pip install -r requirements_api.txt`

### No data returned
1. Check database connection
2. Verify date ranges have data
3. Check database table name matches configuration

### Slow responses
1. Add indexes to database on `created_at`, `motorcyclist_id`, `payment_status`
2. Use date ranges instead of `period=all`
3. Consider implementing caching

---

## License
Proprietary - Jalikoi Analytics System

## Support
For issues or questions, contact the development team.
