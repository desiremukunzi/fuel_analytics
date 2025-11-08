#!/usr/bin/env python3
"""
Diagnose and fix revenue prediction issues
"""

import sys
import pandas as pd
import numpy as np

print("="*80)
print("DIAGNOSING REVENUE PREDICTION ISSUES")
print("="*80)
print()

# Step 1: Load ML models and check
print("Step 1: Checking ML models...")
print("-"*80)

try:
    from ml_engine import MLEngine
    ml = MLEngine(model_dir="ml_models")
    
    info = ml.get_model_info()
    print(f"Revenue model trained: {info['revenue_model_trained']}")
    print(f"Last trained: {info['last_trained']}")
    print()
    
except Exception as e:
    print(f"Error loading models: {e}")
    sys.exit(1)

# Step 2: Load customer data
print("Step 2: Loading customer data...")
print("-"*80)

try:
    from jalikoi_analytics_db import JalikoiAnalyticsVisualized
    from db_config import DB_CONFIG
    
    analytics = JalikoiAnalyticsVisualized(DB_CONFIG, use_database=True)
    customer_metrics = analytics.customer_metrics
    
    print(f"Loaded {len(customer_metrics)} customers")
    print(f"Columns: {list(customer_metrics.columns)}")
    print()
    
except Exception as e:
    print(f"Error loading data: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Check data ranges
print("Step 3: Checking data ranges...")
print("-"*80)

print("\nCustomer Metrics Summary:")
print(customer_metrics[['total_spent', 'avg_transaction', 'frequency', 
                         'transaction_count']].describe())

print("\nChecking for extreme values:")
print(f"Max total_spent: {customer_metrics['total_spent'].max():,.2f} RWF")
print(f"Max avg_transaction: {customer_metrics['avg_transaction'].max():,.2f} RWF")
print(f"Max frequency: {customer_metrics['frequency'].max():.4f}")

# Check for infinities or NaNs
print(f"\nNaN values: {customer_metrics.isna().sum().sum()}")
print(f"Inf values: {np.isinf(customer_metrics.select_dtypes(include=[np.number])).sum().sum()}")
print()

# Step 4: Test prediction on sample
print("Step 4: Testing predictions on sample customers...")
print("-"*80)

# Get top 3 customers by spending
sample = customer_metrics.nlargest(3, 'total_spent')[['motorcyclist_id', 'total_spent', 
                                                         'avg_transaction', 'transaction_count',
                                                         'frequency']].copy()

print("\nSample customers:")
print(sample)
print()

# Try to predict
try:
    predictions = ml.predict_revenue(customer_metrics)
    
    print("\nRevenue Predictions:")
    print(f"Min prediction: {predictions['predicted_revenue'].min():,.2f} RWF")
    print(f"Max prediction: {predictions['predicted_revenue'].max():,.2f} RWF")
    print(f"Mean prediction: {predictions['predicted_revenue'].mean():,.2f} RWF")
    print(f"Median prediction: {predictions['predicted_revenue'].median():,.2f} RWF")
    
    # Show top 5 predictions
    print("\nTop 5 predicted revenues:")
    top5 = predictions.nlargest(5, 'predicted_revenue')[['motorcyclist_id', 'predicted_revenue', 
                                                          'historical_revenue', 'confidence']]
    for _, row in top5.iterrows():
        print(f"  Customer {row['motorcyclist_id']}: "
              f"Predicted={row['predicted_revenue']:,.2f} RWF, "
              f"Historical={row['historical_revenue']:,.2f} RWF")
    
    # Check for unrealistic predictions
    unrealistic = predictions[predictions['predicted_revenue'] > 100_000_000]  # > 100M
    if len(unrealistic) > 0:
        print(f"\n⚠️  WARNING: {len(unrealistic)} customers with predictions > 100M RWF!")
        print("This is likely incorrect!")
    
    # Check ratio
    predictions['ratio'] = predictions['predicted_revenue'] / predictions['historical_revenue']
    extreme_ratios = predictions[predictions['ratio'] > 100]
    if len(extreme_ratios) > 0:
        print(f"\n⚠️  WARNING: {len(extreme_ratios)} customers with predicted/historical ratio > 100x!")
        print("Examples:")
        for _, row in extreme_ratios.head(3).iterrows():
            print(f"  Customer {row['motorcyclist_id']}: "
                  f"Ratio={row['ratio']:.1f}x "
                  f"(Predicted={row['predicted_revenue']:,.0f}, Historical={row['historical_revenue']:,.0f})")
    
except Exception as e:
    print(f"Error making predictions: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Step 5: Diagnose issue
print("Step 5: Diagnosing issue...")
print("-"*80)

# Check model internals
import pickle

with open('ml_models/ml_models.pkl', 'rb') as f:
    models = pickle.load(f)

revenue_model = models.get('revenue_model')
revenue_scaler = models.get('revenue_scaler')

if revenue_scaler:
    print("\nRevenue Scaler Info:")
    if hasattr(revenue_scaler, 'scale_'):
        print(f"  Scale factors: {revenue_scaler.scale_[:5]}...")  # First 5
        print(f"  Mean: {revenue_scaler.mean_[:5]}...")
    if hasattr(revenue_scaler, 'feature_names_in_'):
        print(f"  Features: {list(revenue_scaler.feature_names_in_[:5])}...")

if revenue_model:
    print("\nRevenue Model Info:")
    print(f"  Type: {type(revenue_model).__name__}")
    if hasattr(revenue_model, 'n_features_in_'):
        print(f"  Features expected: {revenue_model.n_features_in_}")

print()

# Step 6: Recommendation
print("="*80)
print("DIAGNOSIS COMPLETE")
print("="*80)
print()

if len(unrealistic) > 0 or len(extreme_ratios) > 0:
    print("⚠️  ISSUE FOUND: Unrealistic revenue predictions detected!")
    print()
    print("RECOMMENDED FIXES:")
    print("1. Retrain revenue model with cleaned data")
    print("2. Add sanity checks to predictions (max 10x historical)")
    print("3. Check for data quality issues")
    print()
    print("Run: python fix_revenue_model.py")
else:
    print("✅ No obvious issues found")
    print("But predictions still seem high - may need manual inspection")

print()
