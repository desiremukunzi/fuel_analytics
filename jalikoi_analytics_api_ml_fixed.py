#!/usr/bin/env python3
"""
Jalikoi Analytics REST API with ML & Groq AI Chatbot
=====================================================
Enhanced FastAPI endpoint with Machine Learning and AI Chatbot

Chatbot Endpoint:
- POST /api/chatbot - Groq AI-powered chatbot

Run with: python jalikoi_analytics_api_ml.py
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add imports for ML
try:
    from ml_engine import MLEngine
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠ ML Engine not available. Install scikit-learn to enable ML features.")

# Import Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠ Groq not available. Install with: pip install groq")

# Import working metrics calculator
from train_ml_models import calculate_customer_metrics as calc_customer_metrics

# Import everything from the original API
from jalikoi_analytics_api import *

# Add Pydantic model for chatbot
from pydantic import BaseModel
from typing import Optional

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None

# Initialize ML Engine
if ML_AVAILABLE:
    ml_engine = MLEngine(model_dir="ml_models")
    print("✓ ML Engine initialized")
else:
    ml_engine = None


# ============================================================================
# GROQ AI CHATBOT CLASS
# ============================================================================

class GroqChatbot:
    """Groq AI-powered chatbot for Jalikoi Analytics"""
    
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.engine = engine  # Use the analytics engine from imported API
        self.conversation_history = {}
    
    def get_database_stats(self, start_date: str = None, end_date: str = None) -> dict:
        """Fetch current database statistics"""
        if not end_date:
            end_date = str(datetime.now().date())
        if not start_date:
            start_date = str(datetime.now().date() - timedelta(days=30))
        
        df = self.engine.fetch_data_from_db(start_date, end_date)
        
        if df is None or df.empty:
            return {'error': 'No data available'}
        
        df = self.engine.preprocess_data(df)
        
        return {
            'total_revenue': float(df['amount'].sum()),
            'total_transactions': len(df),
            'total_customers': int(df['motorcyclist_id'].nunique()),
            'total_liters': float(df['liter'].sum()),
            'avg_transaction': float(df['amount'].mean()),
            'active_stations': int(df['station_id'].nunique()),
            'date_range': {'start': start_date, 'end': end_date}
        }
    
    def get_top_customers(self, start_date: str = None, end_date: str = None, n: int = 5) -> dict:
        """Get top N customers by revenue"""
        if not end_date:
            end_date = str(datetime.now().date())
        if not start_date:
            start_date = str(datetime.now().date() - timedelta(days=30))
        
        df = self.engine.fetch_data_from_db(start_date, end_date)
        
        if df is None or df.empty:
            return {'error': 'No data available'}
        
        df = self.engine.preprocess_data(df)
        top_customers = df.groupby('motorcyclist_id')['amount'].sum().nlargest(n)
        
        return {
            'top_customers': [
                {'customer_id': int(cid), 'revenue': float(amount), 'rank': i + 1}
                for i, (cid, amount) in enumerate(top_customers.items())
            ]
        }
    
    def get_station_performance(self, start_date: str = None, end_date: str = None) -> dict:
        """Get station performance metrics"""
        if not end_date:
            end_date = str(datetime.now().date())
        if not start_date:
            start_date = str(datetime.now().date() - timedelta(days=30))
        
        df = self.engine.fetch_data_from_db(start_date, end_date)
        
        if df is None or df.empty:
            return {'error': 'No data available'}
        
        df = self.engine.preprocess_data(df)
        station_stats = df.groupby('station_id').agg({
            'amount': ['sum', 'mean', 'count'],
            'liter': 'sum'
        }).reset_index()
        
        station_stats.columns = ['station_id', 'total_revenue', 'avg_transaction', 'transaction_count', 'total_liters']
        station_stats = station_stats.sort_values('total_revenue', ascending=False)
        
        return {
            'stations': [
                {
                    'station_id': int(row['station_id']),
                    'revenue': float(row['total_revenue']),
                    'transactions': int(row['transaction_count']),
                    'avg_transaction': float(row['avg_transaction']),
                    'total_liters': float(row['total_liters'])
                }
                for _, row in station_stats.head(10).iterrows()
            ]
        }
    
    def get_revenue_trend(self, days: int = 30) -> dict:
        """Get revenue trend over time"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        df = self.engine.fetch_data_from_db(str(start_date), str(end_date))
        
        if df is None or df.empty:
            return {'error': 'No data available'}
        
        df = self.engine.preprocess_data(df)
        daily_revenue = df.groupby(df['created_at'].dt.date)['amount'].sum().reset_index()
        daily_revenue.columns = ['date', 'revenue']
        
        return {
            'trend': [
                {'date': str(row['date']), 'revenue': float(row['revenue'])}
                for _, row in daily_revenue.iterrows()
            ]
        }
    
    def chat(self, user_message: str, user_id: str = "default") -> str:
        """Process user message and return AI response"""
        
        # Initialize conversation history for user
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Update system prompt with current date
        current_system_prompt = f"""
You are an AI assistant for Jalikoi Analytics, a fuel station analytics platform in Rwanda.

Today's date is: {datetime.now().strftime('%Y-%m-%d')}
Yesterday's date was: {(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')}

You help users understand their business data by answering questions about:
- Revenue and sales (always display amounts in RWF - Rwandan Francs)
- Customer statistics
- Station performance
- Transaction trends
- Business insights

IMPORTANT: All monetary amounts are in RWF (Rwandan Francs), not dollars.
When displaying amounts, always use "RWF" or "Rwandan Francs", never use "$" or "dollars".

Format large numbers with commas for readability (e.g., 15,234,567 RWF).

When interpreting dates:
- "today" = {datetime.now().strftime('%Y-%m-%d')}
- "yesterday" = {(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')}
- "last week" = last 7 days ending today
- "this week" = from Monday to today
- "this month" = from 1st of current month to today
- "last month" = the previous calendar month
- "last 30 days" = 30 days before today

Always use the correct dates based on today's date shown above.

When users ask questions, call the appropriate function to get real data.
Be conversational, helpful, and provide actionable insights.
Keep responses concise but informative.
"""
        
        # Define tools
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_database_stats",
                    "description": "Get overall statistics including revenue (in RWF), transactions, customers for a date range. Defaults to last 30 days if dates not provided. All amounts are in Rwandan Francs (RWF).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format. Optional, defaults to 30 days ago."},
                            "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format. Optional, defaults to today."}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_top_customers",
                    "description": "Get top customers ranked by revenue in RWF (Rwandan Francs). Defaults to last 30 days.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format. Optional."},
                            "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format. Optional."},
                            "n": {"type": "integer", "description": "Number of top customers to return", "default": 5}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_station_performance",
                    "description": "Get performance metrics for all stations including revenue in RWF. Defaults to last 30 days.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format. Optional."},
                            "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format. Optional."}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_revenue_trend",
                    "description": "Get daily revenue trend in RWF (Rwandan Francs) over time. Defaults to last 30 days.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "days": {"type": "integer", "description": "Number of days to analyze", "default": 30}
                        }
                    }
                }
            }
        ]
        
        # Add user message to history
        self.conversation_history[user_id].append({"role": "user", "content": user_message})
        
        # Call Groq API
        messages = [
            {"role": "system", "content": current_system_prompt},
            *self.conversation_history[user_id]
        ]
        
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=1024
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        # Process tool calls
        if tool_calls:
            self.conversation_history[user_id].append(response_message)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Call the function
                if function_name == "get_database_stats":
                    result = self.get_database_stats(
                        start_date=function_args.get('start_date'),
                        end_date=function_args.get('end_date')
                    )
                elif function_name == "get_top_customers":
                    result = self.get_top_customers(
                        start_date=function_args.get('start_date'),
                        end_date=function_args.get('end_date'),
                        n=function_args.get('n', 5)
                    )
                elif function_name == "get_station_performance":
                    result = self.get_station_performance(
                        start_date=function_args.get('start_date'),
                        end_date=function_args.get('end_date')
                    )
                elif function_name == "get_revenue_trend":
                    result = self.get_revenue_trend(days=function_args.get('days', 30))
                else:
                    result = {"error": "Unknown function"}
                
                # Add function result
                self.conversation_history[user_id].append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result)
                })
            
            # Get final response
            second_response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": current_system_prompt},
                    *self.conversation_history[user_id]
                ]
            )
            
            final_message = second_response.choices[0].message.content
        else:
            final_message = response_message.content
        
        # Add to history
        self.conversation_history[user_id].append({"role": "assistant", "content": final_message})
        
        return final_message


# Initialize Groq Chatbot
groq_chatbot = None
if GROQ_AVAILABLE:
    groq_api_key = os.environ.get('GROQ_API_KEY')
    if groq_api_key:
        try:
            groq_chatbot = GroqChatbot(groq_api_key)
            print("✓ Groq AI Chatbot initialized")
        except Exception as e:
            print(f"⚠ Groq initialization failed: {e}")
    else:
        print("⚠ GROQ_API_KEY not set. Chatbot will not be available.")


# ============================================================================
# CHATBOT ENDPOINT
# ============================================================================

@app.post("/api/chatbot")
async def chatbot_query(chat_message: ChatMessage):
    """
    Groq AI-powered chatbot for analytics queries
    
    Example queries:
    - "What's our total revenue?"
    - "Who were the top customers yesterday?"
    - "Show me station performance"
    - "Revenue trend for last week"
    """
    if not GROQ_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Groq chatbot not available. Install with: pip install groq"
        )
    
    if not groq_chatbot:
        raise HTTPException(
            status_code=503,
            detail="Groq chatbot not initialized. Set GROQ_API_KEY environment variable."
        )
    
    try:
        response = groq_chatbot.chat(
            chat_message.message,
            chat_message.user_id or "default"
        )
        
        return {
            "success": True,
            "message": response,
            "data": {}
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/chatbot/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = Query(20)):
    """Get conversation history for a user"""
    if not groq_chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not available")
    
    if user_id in groq_chatbot.conversation_history:
        history = groq_chatbot.conversation_history[user_id][-limit:]
        return {
            'success': True,
            'user_id': user_id,
            'messages': history
        }
    else:
        return {
            'success': True,
            'user_id': user_id,
            'messages': []
        }


# ============================================================================
# ML ENDPOINTS  
# ============================================================================

def apply_realistic_constraints(predictions_df, customer_metrics_df):
    """
    Apply realistic constraints to revenue predictions
    
    Rules:
    1. Max 2x historical spending
    2. Absolute ceiling: 50M RWF
    3. Non-negative
    4. New customers (<5 trans): Max 1.5x
    5. Inactive (>30 days): Reduce by inactivity factor
    """
    import numpy as np
    import pandas as pd
    
    # Merge to get historical data
    if 'motorcyclist_id' in predictions_df.columns and 'motorcyclist_id' in customer_metrics_df.columns:
        merged = predictions_df.merge(
            customer_metrics_df[['motorcyclist_id', 'total_spent', 'transaction_count', 'recency_days']], 
            on='motorcyclist_id', 
            how='left'
        )
    else:
        # Already merged or different structure
        merged = predictions_df.copy()
    
    original_predictions = merged['predicted_revenue'].copy()
    
    # Rule 1: Non-negative
    merged['predicted_revenue'] = merged['predicted_revenue'].clip(lower=0)
    
    # Rule 2: Max 2x historical spending
    if 'total_spent' in merged.columns:
        max_allowed = merged['total_spent'] * 2
        merged['predicted_revenue'] = np.minimum(merged['predicted_revenue'], max_allowed)
    
    # Rule 3: Absolute ceiling - 50M RWF
    merged['predicted_revenue'] = merged['predicted_revenue'].clip(upper=50_000_000)
    
    # Rule 4: New customers - max 1.5x
    if 'transaction_count' in merged.columns and 'total_spent' in merged.columns:
        new_customers = merged['transaction_count'] < 5
        new_customer_max = merged.loc[new_customers, 'total_spent'] * 1.5
        merged.loc[new_customers, 'predicted_revenue'] = np.minimum(
            merged.loc[new_customers, 'predicted_revenue'],
            new_customer_max
        )
    
    # Rule 5: Inactive customers - reduce prediction
    if 'recency_days' in merged.columns:
        inactive = merged['recency_days'] > 30
        inactivity_factor = np.maximum(0.1, 1 - (merged.loc[inactive, 'recency_days'] / 180))
        merged.loc[inactive, 'predicted_revenue'] = merged.loc[inactive, 'predicted_revenue'] * inactivity_factor
    
    # Log adjustments
    num_adjusted = (merged['predicted_revenue'] != original_predictions).sum()
    if num_adjusted > 0:
        print(f"   ⚠️  Adjusted {num_adjusted} unrealistic predictions")
        max_before = original_predictions.max()
        max_after = merged['predicted_revenue'].max()
        print(f"   Max prediction: {max_before:,.0f} → {max_after:,.0f} RWF")
    
    return merged[predictions_df.columns]


@app.get("/api/ml/model-info")
async def get_ml_model_info():
    """Get information about trained ML models"""
    if not ML_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML features not available")
    
    return {
        "success": True,
        "ml_available": ML_AVAILABLE,
        "models": ml_engine.get_model_info() if ml_engine else {}
    }


@app.get("/api/ml/churn-predictions")
async def get_churn_predictions(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    min_probability: float = Query(0.0, description="Minimum churn probability (0-1)"),
    limit: int = Query(100, description="Maximum number of results")
):
    """Get ML-powered churn predictions for customers"""
    if not ML_AVAILABLE or ml_engine.churn_model is None:
        raise HTTPException(status_code=503, detail="Churn prediction model not available")
    
    try:
        today = datetime.now().date()
        if not start_date or not end_date:
            start_date = str(today - timedelta(days=30))
            end_date = str(today)
        
        df = engine.fetch_data_from_db(start_date, end_date)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        df = engine.preprocess_data(df)
        customer_metrics = calc_customer_metrics(df)
        predictions = ml_engine.predict_churn(customer_metrics)
        predictions = predictions[predictions['churn_probability'] >= min_probability]
        predictions = predictions.sort_values('churn_probability', ascending=False).head(limit)
        
        result_data = predictions.merge(
            customer_metrics[['motorcyclist_id', 'total_spent', 'transaction_count', 'recency_days']],
            on='motorcyclist_id'
        )
        
        customers_at_risk = []
        for _, row in result_data.iterrows():
            customers_at_risk.append({
                'customer_id': int(row['motorcyclist_id']),
                'churn_probability': float(row['churn_probability']),
                'risk_level': str(row['risk_level']),
                'total_spent': float(row['total_spent']),
                'transactions': int(row['transaction_count']),
                'recency_days': float(row['recency_days']),
                'prediction': 'Will Churn' if row['churn_prediction'] == 1 else 'Will Retain'
            })
        
        return {
            "success": True,
            "model_type": "RandomForestClassifier",
            "model_accuracy": ml_engine.metadata.get('churn_accuracy'),
            "total_customers_analyzed": len(customer_metrics),
            "high_risk_count": len(predictions[predictions['risk_level'] == 'High Risk']),
            "customers_at_risk": customers_at_risk
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/ml/revenue-forecast")
async def get_revenue_forecast(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    months: int = Query(6, description="Forecast period in months"),
    top_n: int = Query(50, description="Top N customers by forecasted revenue")
):
    """Get ML-powered revenue forecasts for customers"""
    if not ML_AVAILABLE or ml_engine.revenue_model is None:
        raise HTTPException(status_code=503, detail="Revenue forecast model not available")
    
    try:
        today = datetime.now().date()
        if not start_date or not end_date:
            start_date = str(today - timedelta(days=30))
            end_date = str(today)
        
        df = engine.fetch_data_from_db(start_date, end_date)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        df = engine.preprocess_data(df)
        customer_metrics = calc_customer_metrics(df)
        predictions = ml_engine.predict_revenue(customer_metrics, months=months)
        predictions = apply_realistic_constraints(predictions, customer_metrics)
        
        result_data = predictions.merge(
            customer_metrics[['motorcyclist_id', 'total_spent', 'transaction_count']],
            on='motorcyclist_id'
        )
        
        result_data = result_data.sort_values('predicted_revenue', ascending=False).head(top_n)
        
        forecasts = []
        total_forecast = 0
        for _, row in result_data.iterrows():
            forecast_value = float(row['predicted_revenue'])
            total_forecast += forecast_value
            forecasts.append({
                'customer_id': int(row['motorcyclist_id']),
                'predicted_revenue': forecast_value,
                'historical_revenue': float(row['total_spent']),
                'transactions': int(row['transaction_count']),
                'confidence': str(row['confidence']),
                'forecast_period_months': months
            })
        
        return {
            "success": True,
            "model_type": "GradientBoostingRegressor",
            "model_mae": ml_engine.metadata.get('revenue_mae'),
            "forecast_period_months": months,
            "total_customers_analyzed": len(customer_metrics),
            "total_forecasted_revenue": round(total_forecast, 2),
            "top_customers_forecast": forecasts
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/ml/segments")
async def get_ml_segments(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get ML-based customer segmentation"""
    if not ML_AVAILABLE or ml_engine.segmentation_model is None:
        raise HTTPException(status_code=503, detail="Segmentation model not available")
    
    try:
        today = datetime.now().date()
        start_date = "2025-08-01"
        end_date = str(today)
        
        df = engine.fetch_data_from_db(start_date, end_date)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        df = engine.preprocess_data(df)
        customer_metrics = calc_customer_metrics(df)
        predictions = ml_engine.predict_segments(customer_metrics)
        
        result_data = predictions.merge(
            customer_metrics[['motorcyclist_id', 'total_spent', 'transaction_count', 'recency_days', 'frequency']],
            on='motorcyclist_id'
        )
        
        segment_stats = result_data.groupby('segment_name').agg({
            'motorcyclist_id': 'count',
            'total_spent': ['sum', 'mean'],
            'transaction_count': 'mean',
            'recency_days': 'mean',
            'frequency': 'mean'
        }).reset_index()
        
        segment_stats.columns = [
            'segment_name', 'customer_count', 'total_revenue', 'avg_revenue',
            'avg_transactions', 'avg_recency', 'avg_frequency'
        ]
        
        segments_summary = []
        for _, row in segment_stats.iterrows():
            segments_summary.append({
                'segment_name': str(row['segment_name']),
                'customer_count': int(row['customer_count']),
                'total_revenue': float(row['total_revenue']),
                'avg_revenue_per_customer': float(row['avg_revenue']),
                'avg_transactions': float(row['avg_transactions']),
                'avg_recency_days': float(row['avg_recency']),
                'avg_frequency': float(row['avg_frequency'])
            })
        
        return {
            "success": True,
            "model_type": "KMeans",
            "n_clusters": 8,
            "total_customers_analyzed": len(customer_metrics),
            "segments": segments_summary
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/ml/segment-customers/{segment_name}")
async def get_segment_customers(
    segment_name: str,
    limit: int = Query(5000, description="Maximum customers to return")
):
    """Get detailed customer list for a specific segment"""
    if not ML_AVAILABLE or ml_engine.segmentation_model is None:
        raise HTTPException(status_code=503, detail="Segmentation model not available")
    
    try:
        import pandas as pd
        from database_connector import JalikoiDatabaseConnector
        from db_config import DB_CONFIG
        
        today = datetime.now().date()
        start_date = "2025-08-01"
        end_date = str(today)
        
        df = engine.fetch_data_from_db(start_date, end_date)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        df = engine.preprocess_data(df)
        customer_metrics = calc_customer_metrics(df)
        predictions = ml_engine.predict_segments(customer_metrics)
        
        segment_customers = predictions[predictions['segment_name'] == segment_name]
        
        if segment_name == "New Customers":
            metrics_subset = customer_metrics[
                customer_metrics['motorcyclist_id'].isin(segment_customers['motorcyclist_id'])
            ][['motorcyclist_id', 'customer_age_days', 'frequency', 'total_spent', 'transaction_count', 'recency_days']]
            
            merged = segment_customers.merge(metrics_subset, on='motorcyclist_id', how='left')
            is_new = merged['customer_age_days'] < 90
            has_potential = (merged['frequency'] > 0.5) | (merged['total_spent'] > 100000) | (merged['transaction_count'] > 5)
            is_active = merged['recency_days'] < 30
            filtered = merged[is_new & has_potential & is_active]
            segment_customers = filtered[segment_customers.columns]
        
        if len(segment_customers) == 0:
            return {"success": True, "segment_name": segment_name, "total_customers": 0, "customers": []}
        
        customer_ids = segment_customers['motorcyclist_id'].tolist()[:limit]
        customer_ids_str = ','.join(map(str, customer_ids))
        
        customer_query = f"""
            SELECT  
                d.motorcyclist_id,
                d.payer_phone,
                d.created_at AS first_transaction_date
            FROM DailyTransactionPayments d
            JOIN (
                SELECT motorcyclist_id, MIN(created_at) AS first_transaction_date
                FROM DailyTransactionPayments
                WHERE motorcyclist_id IN ({customer_ids_str})
                  AND created_at BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY motorcyclist_id
            ) AS first_txn
            ON d.motorcyclist_id = first_txn.motorcyclist_id
            AND d.created_at = first_txn.first_transaction_date
            ORDER BY first_txn.first_transaction_date DESC
        """
        
        with JalikoiDatabaseConnector(DB_CONFIG) as db:
            customers_df = db.fetch_data(customer_query)
        
        if customers_df is None or customers_df.empty:
            customers_list = []
            for _, row in segment_customers.head(limit).iterrows():
                customers_list.append({
                    'motorcyclist_id': int(row['motorcyclist_id']),
                    'payer_phone': 'N/A',
                    'created_at': 'N/A',
                    'ml_segment': int(row['ml_segment'])
                })
        else:
            merged = segment_customers.merge(customers_df, on='motorcyclist_id', how='left')
            customers_list = []
            for _, row in merged.head(limit).iterrows():
                customers_list.append({
                    'motorcyclist_id': int(row['motorcyclist_id']),
                    'payer_phone': str(row['payer_phone']) if pd.notna(row['payer_phone']) else 'N/A',
                    'created_at': str(row['first_transaction_date']) if pd.notna(row['first_transaction_date']) else 'N/A',
                    'ml_segment': int(row['ml_segment'])
                })
        
        return {
            "success": True,
            "segment_name": segment_name,
            "total_customers": len(segment_customers),
            "customers_returned": len(customers_list),
            "customers": customers_list
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/ml/anomalies")
async def detect_anomalies(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, description="Maximum number of anomalies to return")
):
    """Detect anomalous transactions using ML"""
    if not ML_AVAILABLE or ml_engine.anomaly_model is None:
        raise HTTPException(status_code=503, detail="Anomaly detection model not available")
    
    try:
        today = datetime.now().date()
        if not start_date or not end_date:
            start_date = str(today - timedelta(days=30))
            end_date = str(today)
        
        df = engine.fetch_data_from_db(start_date, end_date)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        df = engine.preprocess_data(df)
        predictions = ml_engine.detect_anomalies(df)
        result_data = df.merge(predictions, on='id')
        anomalies = result_data[result_data['is_anomaly'] == True].copy()
        anomalies = anomalies.sort_values('anomaly_score').head(limit)
        
        anomaly_list = []
        for _, row in anomalies.iterrows():
            anomaly_list.append({
                'transaction_id': int(row['id']),
                'customer_id': int(row['motorcyclist_id']),
                'amount': float(row['amount']),
                'liters': float(row['liter']),
                'station_id': int(row['station_id']),
                'timestamp': str(row['created_at']),
                'anomaly_score': float(row['anomaly_score']),
                'risk_level': str(row['risk_level']),
                'payment_status': int(row['payment_status'])
            })
        
        total_anomalies = len(anomalies)
        anomaly_rate = (total_anomalies / len(df)) * 100 if len(df) > 0 else 0
        
        return {
            "success": True,
            "model_type": "IsolationForest",
            "period": {"start_date": start_date, "end_date": end_date},
            "total_transactions_analyzed": len(df),
            "total_anomalies_detected": total_anomalies,
            "anomaly_rate": round(anomaly_rate, 2),
            "anomalies": anomaly_list
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/api/ml/train")
async def trigger_model_training(
    days_back: int = Query(90, description="Days of historical data to use"),
    admin_key: str = Query(..., description="Admin authentication key")
):
    """Trigger ML model training (admin only)"""
    if admin_key != "JALIKOI_ADMIN_2025":
        raise HTTPException(status_code=403, detail="Invalid admin key")
    
    if not ML_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML features not available")
    
    try:
        from train_ml_models import train_all_models
        import threading
        
        def train_in_background():
            train_all_models()
        
        thread = threading.Thread(target=train_in_background)
        thread.start()
        
        return {
            "success": True,
            "message": "Model training started in background",
            "days_back": days_back,
            "note": "Training may take 5-15 minutes depending on data size"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Update root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    endpoints = {
        "health": "/api/health",
        "insights": "/api/insights",
        "visualizations": "/api/visualizations",
        "chatbot": "/api/chatbot",
        "docs": "/docs"
    }
    
    if ML_AVAILABLE:
        endpoints.update({
            "ml_model_info": "/api/ml/model-info",
            "ml_churn_predictions": "/api/ml/churn-predictions",
            "ml_revenue_forecast": "/api/ml/revenue-forecast",
            "ml_segments": "/api/ml/segments",
            "ml_anomalies": "/api/ml/anomalies"
        })
    
    return {
        "message": "Jalikoi Analytics API with ML & Groq AI Chatbot",
        "version": "3.0.0-Groq",
        "ml_enabled": ML_AVAILABLE,
        "chatbot_enabled": GROQ_AVAILABLE and groq_chatbot is not None,
        "endpoints": endpoints
    }


if __name__ == "__main__":
    import uvicorn
    print("="*80)
    print("JALIKOI ANALYTICS API - ML & GROQ AI CHATBOT")
    print("="*80)
    print(f"\nML Features: {'✓ ENABLED' if ML_AVAILABLE else '✗ DISABLED'}")
    print(f"Groq AI Chatbot: {'✓ ENABLED' if (GROQ_AVAILABLE and groq_chatbot) else '✗ DISABLED'}")
    
    if not GROQ_AVAILABLE:
        print("\n⚠ To enable Groq chatbot:")
        print("   1. pip install groq python-dotenv")
        print("   2. Get free API key: https://console.groq.com")
        print("   3. Add to .env: GROQ_API_KEY=your_key")
    elif not groq_chatbot:
        print("\n⚠ Groq installed but not initialized")
        print("   Set GROQ_API_KEY in .env file")
    
    print("\nStarting API server...")
    print("Access API at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Chatbot endpoint: POST /api/chatbot")
    
    if ML_AVAILABLE and ml_engine:
        model_info = ml_engine.get_model_info()
        print("\nML Models Status:")
        print(f"  • Churn Prediction: {'✓ Trained' if model_info['churn_model_trained'] else '✗ Not Trained'}")
        print(f"  • Revenue Forecast: {'✓ Trained' if model_info['revenue_model_trained'] else '✗ Not Trained'}")
        print(f"  • Segmentation: {'✓ Trained' if model_info['segmentation_model_trained'] else '✗ Not Trained'}")
        print(f"  • Anomaly Detection: {'✓ Trained' if model_info['anomaly_model_trained'] else '✗ Not Trained'}")
    
    print("="*80)
    print()
    
    uvicorn.run("jalikoi_analytics_api_ml_fixed:app", host="0.0.0.0", port=8000, reload=True)
