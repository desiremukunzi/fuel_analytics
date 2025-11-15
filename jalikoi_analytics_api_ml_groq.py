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
    
    uvicorn.run("jalikoi_analytics_api_ml_groq:app", host="0.0.0.0", port=8000, reload=True)
