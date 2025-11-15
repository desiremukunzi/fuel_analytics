
#!/usr/bin/env python3
"""
Groq AI-Powered Chatbot for Jalikoi Analytics
100% FREE - No credit card required!

Get free API key: https://console.groq.com
"""

import os
import json
from datetime import datetime, timedelta
from database_connector import JalikoiDatabaseConnector
from db_config import DB_CONFIG
# Import the engine from jalikoi_analytics_api
from jalikoi_analytics_api import engine as analytics_engine
from train_ml_models import calculate_customer_metrics

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file
    print("✓ Loaded environment variables from .env file")
except ImportError:
    print("⚠ python-dotenv not installed. Using system environment variables.")
    print("  Install with: pip install python-dotenv")

# Install: pip install groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Install groq: pip install groq")


class GroqAnalyticsChatbot:
    """
    FREE AI-powered chatbot using Groq
    Much faster than Claude and completely free!
    """
    
    def __init__(self, api_key: str = None):
        if not GROQ_AVAILABLE:
            raise ImportError("Please install: pip install groq")
        
        # Initialize Groq (FREE!)
        self.api_key = api_key or os.environ.get('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("Set GROQ_API_KEY environment variable")
        
        self.client = Groq(api_key=self.api_key)
        self.engine = analytics_engine  # Use the imported engine
        
        # System prompt
        self.system_prompt = f"""
You are an AI assistant for Jalikoi Analytics, a fuel station analytics platform in Rwanda.

Today's date is: {datetime.now().strftime('%Y-%m-%d')}

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
- "last week" = last 7 days from today
- "this month" = current month from day 1 to today
- "last 30 days" = 30 days before today

When users ask questions, call the appropriate function to get real data.
Be conversational, helpful, and provide actionable insights.
Keep responses concise but informative.
"""
        
        # Conversation history
        self.conversation_history = []
    
    def get_database_stats(self, start_date: str = None, end_date: str = None) -> dict:
        """Fetch current database statistics"""
        # Default to last 30 days if dates not provided
        if not end_date:
            end_date = str(datetime.now().date())
        if not start_date:
            start_date = str(datetime.now().date() - timedelta(days=30))
        
        df = self.engine.fetch_data_from_db(start_date, end_date)
        
        if df is None or df.empty:
            return {'error': 'No data available'}
        
        df = self.engine.preprocess_data(df)
        customer_metrics = calculate_customer_metrics(df)
        
        return {
            'total_revenue': float(df['amount'].sum()),
            'total_transactions': len(df),
            'total_customers': int(df['motorcyclist_id'].nunique()),
            'total_liters': float(df['liter'].sum()),
            'avg_transaction': float(df['amount'].mean()),
            'active_stations': int(df['station_id'].nunique()),
            'date_range': {
                'start': start_date,
                'end': end_date
            }
        }
    
    def get_top_customers(self, start_date: str = None, end_date: str = None, n: int = 5) -> dict:
        """Get top N customers by revenue"""
        # Default to last 30 days if dates not provided
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
                {
                    'customer_id': int(cid),
                    'revenue': float(amount),
                    'rank': i + 1
                }
                for i, (cid, amount) in enumerate(top_customers.items())
            ]
        }
    
    def get_station_performance(self, start_date: str = None, end_date: str = None) -> dict:
        """Get station performance metrics"""
        # Default to last 30 days if dates not provided
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
                {
                    'date': str(row['date']),
                    'revenue': float(row['revenue'])
                }
                for _, row in daily_revenue.iterrows()
            ]
        }
    
    def chat(self, user_message: str) -> str:
        """
        Process user message and return AI response
        Uses Groq with function calling (FREE!)
        """
        
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
                            "start_date": {
                                "type": "string",
                                "description": "Start date in YYYY-MM-DD format. Optional, defaults to 30 days ago."
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date in YYYY-MM-DD format. Optional, defaults to today."
                            }
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
                            "start_date": {
                                "type": "string",
                                "description": "Start date in YYYY-MM-DD format. Optional."
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date in YYYY-MM-DD format. Optional."
                            },
                            "n": {
                                "type": "integer",
                                "description": "Number of top customers to return",
                                "default": 5
                            }
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
                            "start_date": {
                                "type": "string",
                                "description": "Start date in YYYY-MM-DD format. Optional."
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date in YYYY-MM-DD format. Optional."
                            }
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
                            "days": {
                                "type": "integer",
                                "description": "Number of days to analyze",
                                "default": 30
                            }
                        }
                    }
                }
            }
        ]
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Call Groq API (FREE!)
        messages = [
            {"role": "system", "content": current_system_prompt},
            *self.conversation_history
        ]
        
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # FREE and very smart!
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=1024
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        # Process tool calls
        if tool_calls:
            self.conversation_history.append(response_message)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"🔧 Calling: {function_name}({function_args})")
                
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
                    result = self.get_revenue_trend(
                        days=function_args.get('days', 30)
                    )
                else:
                    result = {"error": "Unknown function"}
                
                # Add function result
                self.conversation_history.append({
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
                    *self.conversation_history
                ]
            )
            
            final_message = second_response.choices[0].message.content
        else:
            final_message = response_message.content
        
        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": final_message
        })
        
        return final_message


# Example usage
if __name__ == "__main__":
    import sys
    
    # Check for API key
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        print("❌ Please set GROQ_API_KEY environment variable")
        print("\n📝 Get free API key at: https://console.groq.com")
        print("   1. Sign up (no credit card)")
        print("   2. Create API key")
        print("   3. export GROQ_API_KEY='your-key-here'")
        sys.exit(1)
    
    print("="*70)
    print("🤖 GROQ AI CHATBOT - 100% FREE!")
    print("="*70)
    print("\nPowered by Llama 3.1 70B (Meta's latest AI)")
    print("I can help you understand your Jalikoi Analytics data!")
    print("\nTry asking:")
    print("  • What's our total revenue?")
    print("  • Who are our top customers?")
    print("  • Show me station performance")
    print("  • What's the revenue trend?")
    print("\nType 'exit' to quit\n")
    
    try:
        chatbot = GroqAnalyticsChatbot(api_key)
        
        while True:
            user_input = input("💬 You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 Thinking...\n")
            response = chatbot.chat(user_input)
            print(f"🤖 Assistant: {response}\n")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
