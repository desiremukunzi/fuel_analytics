#!/usr/bin/env python3
"""
ML Model Training Script
=========================
Train all machine learning models with historical data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys

try:
    from database_connector import JalikoiDatabaseConnector
    from db_config import DB_CONFIG
    from ml_engine import MLEngine
    DATABASE_MODE = True
except ImportError as e:
    print(f"Error importing modules: {e}")
    DATABASE_MODE = False
    sys.exit(1)


def fetch_training_data(days_back: int = 90):
    """Fetch historical data for training
    
    Args:
        days_back: Number of days of historical data
        
    Returns:
        DataFrame with transaction data
    """
    print(f"Fetching {days_back} days of historical data...")
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days_back)
    
    query = f"""
        SELECT 
            id, station_id, motorcyclist_id, source, payer_phone,
            fuel_type, liter, pump_price, amount, motari_code,
            cashback_wallet_enabled, sp_txn_id, payment_status,
            payment_method_id, created_at, updated_at
        FROM DailyTransactionPayments
        WHERE payment_status IN (200, 500)
        AND DATE(created_at) >= '{start_date}'
        AND DATE(created_at) <= '{end_date}'
        ORDER BY created_at DESC
    """
    
    try:
        with JalikoiDatabaseConnector(DB_CONFIG) as db:
            df = db.fetch_data(query)
            if df is None or df.empty:
                print("No data found!")
                return None
            print(f"✓ Fetched {len(df):,} transactions")
            return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess transaction data
    
    Args:
        df: Raw transaction dataframe
        
    Returns:
        Preprocessed dataframe
    """
    print("Preprocessing data...")
    
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['date'] = df['created_at'].dt.date
    df['hour'] = df['created_at'].dt.hour
    df['day_of_week'] = df['created_at'].dt.dayofweek
    df['day_name'] = df['created_at'].dt.day_name()
    
    print("✓ Data preprocessed")
    return df


def calculate_customer_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate customer-level metrics
    
    Args:
        df: Transaction dataframe
        
    Returns:
        Customer metrics dataframe
    """
    print("Calculating customer metrics...")
    
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
    
    # Calculate failure rate
    failure_rates = df.groupby('motorcyclist_id').agg({
        'payment_status': lambda x: (x == 500).sum() / len(x)
    }).reset_index()
    failure_rates.columns = ['motorcyclist_id', 'failure_rate']
    customer_metrics = customer_metrics.merge(failure_rates, on='motorcyclist_id', how='left')
    customer_metrics['failure_rate'] = customer_metrics['failure_rate'].fillna(0)
    
    print(f"✓ Calculated metrics for {len(customer_metrics):,} customers")
    return customer_metrics


def create_churn_labels(customer_metrics: pd.DataFrame, churn_threshold_days: int = 30) -> pd.Series:
    """Create churn labels for training
    
    Args:
        customer_metrics: Customer metrics dataframe
        churn_threshold_days: Days of inactivity to consider churned
        
    Returns:
        Series of churn labels (1=churned, 0=active)
    """
    print(f"Creating churn labels (threshold: {churn_threshold_days} days)...")
    
    # Label customers as churned if inactive for > threshold days
    churn_labels = (customer_metrics['recency_days'] > churn_threshold_days).astype(int)
    
    n_churned = churn_labels.sum()
    n_active = len(churn_labels) - n_churned
    churn_rate = n_churned / len(churn_labels) * 100
    
    print(f"✓ Churned: {n_churned:,} ({churn_rate:.1f}%), Active: {n_active:,} ({100-churn_rate:.1f}%)")
    
    return churn_labels


def create_revenue_labels(customer_metrics: pd.DataFrame) -> pd.Series:
    """Create future revenue labels for training
    
    Args:
        customer_metrics: Customer metrics dataframe
        
    Returns:
        Series of future revenue (6-month projection)
    """
    print("Creating revenue labels...")
    
    # Simple projection: avg_transaction * frequency * 180 days
    future_revenue = (
        customer_metrics['avg_transaction'] * 
        customer_metrics['frequency'] * 
        180
    )
    
    # Add some noise for realism
    noise = np.random.normal(0, future_revenue * 0.1)
    future_revenue = future_revenue + noise
    future_revenue = future_revenue.clip(lower=0)
    
    print(f"✓ Created revenue labels - Avg: {future_revenue.mean():,.2f}")
    
    return future_revenue


def train_all_models():
    """Train all ML models"""
    print("=" * 80)
    print("JALIKOI ANALYTICS - ML MODEL TRAINING")
    print("=" * 80)
    print()
    
    # Initialize ML engine
    ml_engine = MLEngine(model_dir="ml_models")
    
    # Fetch data
    df = fetch_training_data(days_back=90)
    if df is None:
        print("❌ Failed to fetch training data")
        return
    
    # Preprocess
    df = preprocess_data(df)
    
    # Calculate customer metrics
    customer_metrics = calculate_customer_metrics(df)
    
    # Check if we have enough data
    if len(customer_metrics) < 100:
        print(f"⚠ Warning: Only {len(customer_metrics)} customers. Need at least 100 for reliable training.")
        return
    
    print()
    print("=" * 80)
    print("TRAINING MODELS")
    print("=" * 80)
    print()
    
    # 1. Train Churn Model
    print("1. CHURN PREDICTION MODEL")
    print("-" * 80)
    churn_labels = create_churn_labels(customer_metrics, churn_threshold_days=30)
    churn_results = ml_engine.train_churn_model(customer_metrics, churn_labels)
    print(f"   Accuracy: {churn_results['accuracy']:.2%}")
    print(f"   Precision: {churn_results['precision']:.2%}")
    print(f"   Recall: {churn_results['recall']:.2%}")
    print(f"   F1 Score: {churn_results['f1_score']:.2%}")
    print()
    
    # 2. Train Revenue Model
    print("2. REVENUE FORECASTING MODEL")
    print("-" * 80)
    revenue_labels = create_revenue_labels(customer_metrics)
    revenue_results = ml_engine.train_revenue_model(customer_metrics, revenue_labels)
    print(f"   MAE: {revenue_results['mae']:,.2f}")
    print(f"   RMSE: {revenue_results['rmse']:,.2f}")
    print(f"   R² Score: {revenue_results['r2_score']:.4f}")
    print()
    
    # 3. Train Segmentation Model
    print("3. CUSTOMER SEGMENTATION MODEL")
    print("-" * 80)
    segmentation_results = ml_engine.train_segmentation_model(customer_metrics, n_clusters=8)
    print(f"   Clusters: {segmentation_results['n_clusters']}")
    print(f"   Total Customers: {segmentation_results['total_customers']:,}")
    print()
    
    # 4. Train Anomaly Detector
    print("4. ANOMALY DETECTION MODEL")
    print("-" * 80)
    anomaly_results = ml_engine.train_anomaly_detector(df)
    print(f"   Total Transactions: {anomaly_results['total_transactions']:,}")
    print(f"   Anomalies Detected: {anomaly_results['anomalies_detected']:,}")
    print(f"   Anomaly Rate: {anomaly_results['anomaly_rate']:.2%}")
    print()
    
    print("=" * 80)
    print("TRAINING COMPLETE!")
    print("=" * 80)
    print()
    print("Model Performance Summary:")
    print(f"  • Churn Prediction: {churn_results['accuracy']:.2%} accuracy")
    print(f"  • Revenue Forecast: MAE of {revenue_results['mae']:,.2f}")
    print(f"  • Customer Segments: {segmentation_results['n_clusters']} clusters")
    print(f"  • Anomaly Detection: {anomaly_results['anomaly_rate']:.2%} flagged")
    print()
    print("Models saved to: ml_models/")
    print()
    print("Next steps:")
    print("  1. Review model performance metrics")
    print("  2. Restart API to load new models")
    print("  3. Test predictions via API endpoints")
    print()


if __name__ == "__main__":
    train_all_models()
