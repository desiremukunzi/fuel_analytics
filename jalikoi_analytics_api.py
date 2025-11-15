#!/usr/bin/env python3
"""
Jalikoi Analytics REST API
============================
FastAPI endpoint for retrieving insights and visualizations
Supports date ranges, comparisons, and Postman testing

Endpoints:
- GET /api/insights - Yesterday's insights (default)
- GET /api/insights?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD - Date range
- GET /api/insights?period=all - All data since start
- GET /api/visualizations - Get chart data
- GET /api/health - Health check

Run with: uvicorn jalikoi_analytics_api:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np
import json
import os
import base64
import io
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns

# Import database components
try:
    from database_connector import JalikoiDatabaseConnector
    from db_config import DB_CONFIG, PAYMENTS_QUERY
    DATABASE_MODE = True
except ImportError:
    DATABASE_MODE = False

# Initialize FastAPI
app = FastAPI(
    title="Jalikoi Analytics API",
    description="REST API for customer analytics and insights",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

COLORS = {
    'primary': '#2E86AB',
    'success': '#06D6A0',
    'warning': '#F77F00',
    'danger': '#D62828',
    'info': '#023E8A',
}

def convert_to_native_types(obj):
    """Convert numpy/pandas types to native Python types for JSON serialization"""
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_native_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native_types(item) for item in obj]
    else:
        return obj

class AnalyticsEngine:
    """Core analytics engine for API"""
    
    def __init__(self):
        self.currency = "RWF"
        
    def fetch_data_from_db(self, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """Fetch data from database with optional date filtering"""
        if not DATABASE_MODE:
            raise HTTPException(status_code=500, detail="Database mode not available")
        
        # Build query with date filtering
        query = f"""
            SELECT 
                id, station_id, motorcyclist_id, source, payer_phone,
                fuel_type, liter, pump_price, amount, motari_code,
                cashback_wallet_enabled, sp_txn_id, payment_status,
                payment_method_id, created_at, updated_at
            FROM DailyTransactionPayments
            WHERE payment_status = 200
        """
        
        if start_date:
            query += f" AND DATE(created_at) >= '{start_date}'"
        if end_date:
            query += f" AND DATE(created_at) <= '{end_date}'"
            
        query += " ORDER BY created_at DESC"
        
        try:
            with JalikoiDatabaseConnector(DB_CONFIG) as db:
                df = db.fetch_data(query)
                if df is None or df.empty:
                    return None
                return df
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare data"""
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['date'] = df['created_at'].dt.date
        df['hour'] = df['created_at'].dt.hour
        df['day_of_week'] = df['created_at'].dt.dayofweek
        df['day_name'] = df['created_at'].dt.day_name()
        return df
    
    def calculate_customer_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate customer-level metrics"""
        df_success = df[df['payment_status'] == 200].copy()
        reference_date = df['created_at'].max()
        
        customer_metrics = df_success.groupby('motorcyclist_id').agg({
            'id': 'count',
            'amount': ['sum', 'mean', 'std', 'min', 'max'],
            'liter': ['sum', 'mean'],
            'station_id': lambda x: x.nunique(),
            'created_at': ['min', 'max'],
            'payment_method_id': 'first',
            'source': lambda x: (x == 'APP').sum() / len(x)
        }).reset_index()
        
        customer_metrics.columns = [
            'motorcyclist_id', 'transaction_count', 'total_spent', 'avg_transaction',
            'std_transaction', 'min_transaction', 'max_transaction',
            'total_liters', 'avg_liters', 'station_diversity', 
            'first_transaction', 'last_transaction', 'payment_method', 'app_usage_rate'
        ]
        
        customer_metrics['recency_days'] = (
            reference_date - customer_metrics['last_transaction']
        ).dt.total_seconds() / (24 * 3600)
        
        customer_metrics['customer_age_days'] = (
            customer_metrics['last_transaction'] - customer_metrics['first_transaction']
        ).dt.total_seconds() / (24 * 3600)
        customer_metrics['customer_age_days'] = customer_metrics['customer_age_days'].replace(0, 0.1)
        
        customer_metrics['frequency'] = (
            customer_metrics['transaction_count'] / customer_metrics['customer_age_days']
        )
        
        # Calculate CLV
        days_ahead = 180
        customer_metrics['predicted_transactions'] = customer_metrics['frequency'] * days_ahead
        customer_metrics['predicted_clv_6m'] = (
            customer_metrics['predicted_transactions'] * customer_metrics['avg_transaction']
        )
        churn_factor = np.clip(1 - (customer_metrics['recency_days'] / 30), 0.1, 1.0)
        customer_metrics['predicted_clv_6m_adjusted'] = (
            customer_metrics['predicted_clv_6m'] * churn_factor
        )
        
        # Calculate churn risk
        recency_score = np.clip((customer_metrics['recency_days'] / 7) * 20, 0, 40)
        freq_percentile = customer_metrics['frequency'].rank(pct=True)
        frequency_score = (1 - freq_percentile) * 30
        
        failure_rates = df.groupby('motorcyclist_id').agg({
            'payment_status': lambda x: (x == 500).sum() / len(x)
        }).reset_index()
        failure_rates.columns = ['motorcyclist_id', 'failure_rate']
        customer_metrics = customer_metrics.merge(failure_rates, on='motorcyclist_id', how='left')
        customer_metrics['failure_rate'] = customer_metrics['failure_rate'].fillna(0)
        
        failure_score = customer_metrics['failure_rate'] * 20
        txn_percentile = customer_metrics['transaction_count'].rank(pct=True)
        commitment_score = (1 - txn_percentile) * 10
        
        customer_metrics['churn_risk_score'] = (
            recency_score + frequency_score + failure_score + commitment_score
        )
        
        def categorize_churn(score):
            if score >= 60:
                return 'High Risk'
            elif score >= 35:
                return 'Medium Risk'
            else:
                return 'Low Risk'
        
        customer_metrics['churn_risk'] = customer_metrics['churn_risk_score'].apply(categorize_churn)
        
        # RFM Segmentation
        def score_metric(series, reverse=False):
            percentiles = series.rank(pct=True)
            if reverse:
                percentiles = 1 - percentiles
            return np.ceil(percentiles * 5).clip(1, 5)
        
        customer_metrics['R_score'] = score_metric(customer_metrics['recency_days'], reverse=True)
        customer_metrics['F_score'] = score_metric(customer_metrics['transaction_count'])
        customer_metrics['M_score'] = score_metric(customer_metrics['total_spent'])
        
        def assign_segment(row):
            R, F, M = row['R_score'], row['F_score'], row['M_score']
            if R >= 4 and F >= 4 and M >= 4:
                return 'Champions'
            elif R >= 3 and F >= 3 and M >= 3:
                return 'Loyal Customers'
            elif R >= 4 and F <= 2:
                return 'Potential Loyalists'
            elif R <= 2 and F >= 3 and M >= 3:
                return 'At Risk'
            elif R <= 2 and F >= 4 and M >= 4:
                return "Can't Lose Them"
            elif R <= 2 and F <= 2 and M <= 2:
                return 'Lost'
            elif R == 3 and F <= 2:
                return 'Hibernating'
            else:
                return 'Need Attention'
        
        customer_metrics['segment'] = customer_metrics.apply(assign_segment, axis=1)
        
        return customer_metrics
    
    def generate_insights(self, df: pd.DataFrame, customer_metrics: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive insights"""
        df_success = df[df['payment_status'] == 200]
        
        # Basic metrics
        total_transactions = len(df)
        successful_transactions = len(df_success)
        failed_transactions = len(df[df['payment_status'] == 500])
        success_rate = (successful_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        total_revenue = customer_metrics['total_spent'].sum()
        avg_transaction = df_success['amount'].mean() if len(df_success) > 0 else 0
        total_liters = df_success['liter'].sum() if len(df_success) > 0 else 0
        
        # Customer metrics
        total_customers = len(customer_metrics)
        active_customers = len(customer_metrics[customer_metrics['recency_days'] <= 30])
        
        # Segmentation
        segment_distribution = customer_metrics['segment'].value_counts().to_dict()
        segment_revenue = customer_metrics.groupby('segment')['total_spent'].sum().to_dict()
        
        # Churn analysis
        churn_distribution = customer_metrics['churn_risk'].value_counts().to_dict()
        high_risk_count = len(customer_metrics[customer_metrics['churn_risk'] == 'High Risk'])
        revenue_at_risk = customer_metrics[
            customer_metrics['churn_risk'] == 'High Risk'
        ]['predicted_clv_6m_adjusted'].sum()
        
        # Top customers
        top_customers = customer_metrics.nlargest(10, 'total_spent')[
            ['motorcyclist_id', 'total_spent', 'transaction_count', 'segment']
        ].to_dict('records')
        
        # CLV projection
        total_clv_projection = customer_metrics['predicted_clv_6m_adjusted'].sum()
        
        # Station analysis
        station_performance = df_success.groupby('station_id').agg({
            'id': 'count',
            'amount': 'sum',
            'liter': 'sum'
        }).reset_index()
        station_performance.columns = ['station_id', 'transactions', 'revenue', 'liters']
        top_stations = station_performance.nlargest(5, 'revenue').to_dict('records')
        
        # Time analysis
        hourly_transactions = df_success.groupby('hour').size().to_dict()
        daily_transactions = df_success.groupby(df_success['created_at'].dt.date).agg({
            'id': 'count',
            'amount': 'sum'
        }).reset_index()
        daily_transactions.columns = ['date', 'transactions', 'revenue']
        daily_trend = daily_transactions.tail(7).to_dict('records')
        
        insights = {
            'period': {
                'start_date': str(df['created_at'].min().date()),
                'end_date': str(df['created_at'].max().date()),
                'total_days': (df['created_at'].max() - df['created_at'].min()).days + 1
            },
            'overview': {
                'total_transactions': int(total_transactions),
                'successful_transactions': int(successful_transactions),
                'failed_transactions': int(failed_transactions),
                'success_rate': round(success_rate, 2),
                'total_revenue': round(total_revenue, 2),
                'avg_transaction_value': round(avg_transaction, 2),
                'total_liters_sold': round(total_liters, 2),
                'currency': self.currency
            },
            'customers': {
                'total_customers': int(total_customers),
                'active_customers_30d': int(active_customers),
                'avg_customer_value': round(total_revenue / total_customers, 2) if total_customers > 0 else 0,
                'avg_transactions_per_customer': round(successful_transactions / total_customers, 2) if total_customers > 0 else 0
            },
            'segmentation': {
                'segment_distribution': segment_distribution,
                'segment_revenue': {k: round(v, 2) for k, v in segment_revenue.items()}
            },
            'churn_analysis': {
                'churn_distribution': churn_distribution,
                'high_risk_customers': int(high_risk_count),
                'revenue_at_risk': round(revenue_at_risk, 2),
                'churn_rate': round((high_risk_count / total_customers * 100), 2) if total_customers > 0 else 0
            },
            'clv_projection': {
                'total_6m_projection': round(total_clv_projection, 2),
                'avg_customer_clv': round(total_clv_projection / total_customers, 2) if total_customers > 0 else 0
            },
            'top_customers': [
                {
                    'customer_id': int(c['motorcyclist_id']),
                    'total_spent': round(c['total_spent'], 2),
                    'transactions': int(c['transaction_count']),
                    'segment': c['segment']
                } for c in top_customers
            ],
            'station_performance': [
                {
                    'station_id': int(s['station_id']),
                    'transactions': int(s['transactions']),
                    'revenue': round(s['revenue'], 2),
                    'liters': round(s['liters'], 2)
                } for s in top_stations
            ],
            'time_analysis': {
                'hourly_distribution': {int(k): int(v) for k, v in hourly_transactions.items()},
                'daily_trend': [
                    {
                        'date': str(d['date']),
                        'transactions': int(d['transactions']),
                        'revenue': round(d['revenue'], 2)
                    } for d in daily_trend
                ]
            }
        }
        
        # Convert all numpy types to native Python types for JSON serialization
        return convert_to_native_types(insights)
    
    def compare_periods(self, current_insights: Dict, previous_insights: Dict) -> Dict[str, Any]:
        """Compare current period with previous period"""
        def calc_change(current, previous):
            if previous == 0:
                return None
            return round(((current - previous) / previous) * 100, 2)
        
        comparison = {
            'revenue_change': calc_change(
                current_insights['overview']['total_revenue'],
                previous_insights['overview']['total_revenue']
            ),
            'transactions_change': calc_change(
                current_insights['overview']['total_transactions'],
                previous_insights['overview']['total_transactions']
            ),
            'customers_change': calc_change(
                current_insights['customers']['total_customers'],
                previous_insights['customers']['total_customers']
            ),
            'avg_transaction_change': calc_change(
                current_insights['overview']['avg_transaction_value'],
                previous_insights['overview']['avg_transaction_value']
            ),
            'success_rate_change': calc_change(
                current_insights['overview']['success_rate'],
                previous_insights['overview']['success_rate']
            )
        }
        
        return comparison

# Initialize analytics engine
engine = AnalyticsEngine()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Jalikoi Analytics API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "insights": "/api/insights",
            "visualizations": "/api/visualizations",
            "docs": "/docs"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database_available": DATABASE_MODE,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/insights")
async def get_insights(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    period: Optional[str] = Query(None, description="Period: 'yesterday', 'week', 'month', 'all'"),
    compare: bool = Query(False, description="Include comparison with previous period")
):
    """
    Get analytics insights for specified period
    
    Examples:
    - /api/insights - Yesterday's data (default)
    - /api/insights?period=week - Last 7 days
    - /api/insights?period=month - Last 30 days
    - /api/insights?period=all - All historical data
    - /api/insights?start_date=2025-10-01&end_date=2025-10-27 - Custom range
    - /api/insights?start_date=2025-10-01&end_date=2025-10-27&compare=true - With comparison
    """
    
    try:
        # Determine date range
        today = datetime.now().date()
        
        if period == 'all':
            # All data
            current_start = None
            current_end = None
        elif period == 'week':
            current_start = str(today - timedelta(days=7))
            current_end = str(today)
        elif period == 'month':
            current_start = str(today - timedelta(days=30))
            current_end = str(today)
        elif start_date and end_date:
            # Custom range
            current_start = start_date
            current_end = end_date
        else:
            # Default: yesterday
            yesterday = today - timedelta(days=1)
            current_start = str(yesterday)
            current_end = str(yesterday)
        
        # Fetch current period data
        df_current = engine.fetch_data_from_db(current_start, current_end)
        
        if df_current is None or df_current.empty:
            raise HTTPException(status_code=404, detail="No data found for specified period")
        
        df_current = engine.preprocess_data(df_current)
        customer_metrics_current = engine.calculate_customer_metrics(df_current)
        current_insights = engine.generate_insights(df_current, customer_metrics_current)
        
        response = {
            "success": True,
            "data": current_insights
        }
        
        # Add comparison if requested
        if compare and current_start and current_end:
            # Calculate previous period
            current_start_dt = datetime.strptime(current_start, '%Y-%m-%d').date()
            current_end_dt = datetime.strptime(current_end, '%Y-%m-%d').date()
            period_length = (current_end_dt - current_start_dt).days + 1
            
            previous_end = current_start_dt - timedelta(days=1)
            previous_start = previous_end - timedelta(days=period_length - 1)
            
            # Fetch previous period data
            df_previous = engine.fetch_data_from_db(str(previous_start), str(previous_end))
            
            if df_previous is not None and not df_previous.empty:
                df_previous = engine.preprocess_data(df_previous)
                customer_metrics_previous = engine.calculate_customer_metrics(df_previous)
                previous_insights = engine.generate_insights(df_previous, customer_metrics_previous)
                
                comparison = engine.compare_periods(current_insights, previous_insights)
                
                response['comparison'] = {
                    'previous_period': {
                        'start_date': str(previous_start),
                        'end_date': str(previous_end)
                    },
                    'changes': comparison,
                    'previous_data': previous_insights
                }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

@app.get("/api/visualizations")
async def get_visualizations(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    chart_type: Optional[str] = Query(None, description="Chart type: 'revenue', 'segmentation', 'churn', 'all'")
):
    """
    Get visualization data for charts
    
    Returns chart data in format suitable for frontend visualization libraries
    """
    try:
        # Use same date logic as insights endpoint
        today = datetime.now().date()
        if not start_date or not end_date:
            yesterday = today - timedelta(days=1)
            start_date = str(yesterday)
            end_date = str(yesterday)
        
        # Fetch data
        df = engine.fetch_data_from_db(start_date, end_date)
        
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="No data found for specified period")
        
        df = engine.preprocess_data(df)
        customer_metrics = engine.calculate_customer_metrics(df)
        
        charts = {}
        
        # Revenue chart data
        if chart_type in ['revenue', 'all', None]:
            top_customers = customer_metrics.nlargest(10, 'total_spent')
            charts['revenue_top_customers'] = {
                'labels': [f"Customer {int(id)}" for id in top_customers['motorcyclist_id']],
                'values': top_customers['total_spent'].round(2).tolist()
            }
        
        # Segmentation chart data
        if chart_type in ['segmentation', 'all', None]:
            segment_counts = customer_metrics['segment'].value_counts()
            charts['customer_segmentation'] = {
                'labels': segment_counts.index.tolist(),
                'values': segment_counts.values.tolist()
            }
            
            segment_revenue = customer_metrics.groupby('segment')['total_spent'].sum()
            charts['segment_revenue'] = {
                'labels': segment_revenue.index.tolist(),
                'values': segment_revenue.round(2).tolist()
            }
        
        # Churn chart data
        if chart_type in ['churn', 'all', None]:
            churn_dist = customer_metrics['churn_risk'].value_counts()
            risk_order = ['High Risk', 'Medium Risk', 'Low Risk']
            charts['churn_distribution'] = {
                'labels': [r for r in risk_order if r in churn_dist.index],
                'values': [int(churn_dist.get(r, 0)) for r in risk_order if r in churn_dist.index]
            }
            
            risk_clv = customer_metrics.groupby('churn_risk')['predicted_clv_6m_adjusted'].sum()
            charts['revenue_at_risk'] = {
                'labels': [r for r in risk_order if r in risk_clv.index],
                'values': [round(risk_clv.get(r, 0), 2) for r in risk_order if r in risk_clv.index]
            }
        
        result = {
            "success": True,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "charts": charts
        }
        
        # Convert all numpy types to native Python types for JSON serialization
        return convert_to_native_types(result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating visualizations: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("="*80)
    print("JALIKOI ANALYTICS API")
    print("="*80)
    print("\nStarting API server...")
    print("Access API at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("="*80)
    
    uvicorn.run("jalikoi_analytics_api:app", host="0.0.0.0", port=8000, reload=True)
