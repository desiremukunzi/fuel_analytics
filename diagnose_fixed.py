#!/usr/bin/env python3
"""
Fixed diagnosis script
"""

import sys
import pandas as pd
import numpy as np

print("="*80)
print("REVENUE PREDICTION DIAGNOSIS")
print("="*80)
print()

# Step 1: Load models
print("Loading ML models...")
try:
    from ml_engine import MLEngine
    ml = MLEngine(model_dir="ml_models")
    print("✓ Models loaded")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Step 2: Load customer data
print("\nLoading customer data...")
try:
    from jalikoi_analytics_db import JalikoiAnalyticsVisualized
    from db_config import DB_CONFIG
    
    analytics = JalikoiAnalyticsVisualized(DB_CONFIG, use_database=True)
    customer_metrics = analytics.customer_metrics
    
    print(f"✓ Loaded {len(customer_metrics)} customers")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Step 3: Make predictions
print("\nMaking revenue predictions...")
try:
    predictions = ml.predict_revenue(customer_metrics)
    print(f"✓ Made {len(predictions)} predictions")
    print(f"  Columns: {list(predictions.columns)}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Analyze predictions
print("\n" + "="*80)
print("ANALYSIS RESULTS")
print("="*80)

print("\nPrediction Statistics:")
print(f"  Min: {predictions['predicted_revenue'].min():,.2f} RWF")
print(f"  Max: {predictions['predicted_revenue'].max():,.2f} RWF")
print(f"  Mean: {predictions['predicted_revenue'].mean():,.2f} RWF")
print(f"  Median: {predictions['predicted_revenue'].median():,.2f} RWF")

# Get historical revenue from customer_metrics
predictions_with_history = predictions.merge(
    customer_metrics[['motorcyclist_id', 'total_spent']], 
    on='motorcyclist_id', 
    how='left'
)

# Calculate ratios
predictions_with_history['ratio'] = (
    predictions_with_history['predicted_revenue'] / 
    predictions_with_history['total_spent'].replace(0, 1)
)

print("\nPredicted/Historical Ratios:")
print(f"  Min: {predictions_with_history['ratio'].min():.2f}x")
print(f"  Max: {predictions_with_history['ratio'].max():.2f}x")
print(f"  Mean: {predictions_with_history['ratio'].mean():.2f}x")
print(f"  Median: {predictions_with_history['ratio'].median():.2f}x")

# Check for problems
print("\n" + "-"*80)
print("PROBLEM DETECTION")
print("-"*80)

# Problem 0: Negative predictions
negative_preds = predictions_with_history[predictions_with_history['predicted_revenue'] < 0]
if len(negative_preds) > 0:
    print(f"\n🚨 PROBLEM 0: {len(negative_preds)} NEGATIVE predictions!")
    print("Examples:")
    for _, row in negative_preds.head(3).iterrows():
        print(f"  Customer {row['motorcyclist_id']}: "
              f"{row['predicted_revenue']:,.0f} RWF "
              f"(historical: {row['total_spent']:,.0f})")
else:
    print("\n✓ No negative predictions")

# Problem 1: Predictions > 100M
huge_predictions = predictions_with_history[predictions_with_history['predicted_revenue'] > 100_000_000]
if len(huge_predictions) > 0:
    print(f"\n🚨 PROBLEM 1: {len(huge_predictions)} predictions > 100M RWF!")
    print("Examples:")
    for _, row in huge_predictions.head(3).iterrows():
        print(f"  Customer {row['motorcyclist_id']}: "
              f"{row['predicted_revenue']:,.0f} RWF "
              f"(historical: {row['total_spent']:,.0f})")
else:
    print("\n✓ No predictions > 100M")

# Problem 2: Extreme ratios
extreme_ratios = predictions_with_history[predictions_with_history['ratio'] > 100]
if len(extreme_ratios) > 0:
    print(f"\n🚨 PROBLEM 2: {len(extreme_ratios)} predictions with ratio > 100x!")
    print("Examples:")
    for _, row in extreme_ratios.head(3).iterrows():
        print(f"  Customer {row['motorcyclist_id']}: "
              f"{row['ratio']:.0f}x "
              f"(predicted: {row['predicted_revenue']:,.0f}, "
              f"historical: {row['total_spent']:,.0f})")
else:
    print("\n✓ No extreme ratios")

# Problem 3: Very high ratios
high_ratios = predictions_with_history[
    (predictions_with_history['ratio'] > 10) & 
    (predictions_with_history['total_spent'] > 100000)  # Only check for customers with >100K spent
]
if len(high_ratios) > 0:
    print(f"\n⚠️  PROBLEM 3: {len(high_ratios)} predictions with ratio > 10x (for established customers)")
    print("Examples:")
    for _, row in high_ratios.head(3).iterrows():
        print(f"  Customer {row['motorcyclist_id']}: "
              f"{row['ratio']:.1f}x "
              f"(predicted: {row['predicted_revenue']:,.0f}, "
              f"historical: {row['total_spent']:,.0f})")
else:
    print("\n✓ All ratios reasonable")

# Show top predictions
print("\n" + "-"*80)
print("TOP 5 REVENUE PREDICTIONS")
print("-"*80)
top5 = predictions_with_history.nlargest(5, 'predicted_revenue')
for i, row in top5.iterrows():
    print(f"\nCustomer {row['motorcyclist_id']}:")
    print(f"  Predicted (6m): {row['predicted_revenue']:,.2f} RWF")
    print(f"  Historical (total): {row['total_spent']:,.2f} RWF")
    print(f"  Ratio: {row['ratio']:.2f}x")

# Show worst predictions
print("\n" + "-"*80)
print("WORST 3 PREDICTIONS (Highest Ratios)")
print("-"*80)
worst3 = predictions_with_history.nlargest(3, 'ratio')
for i, row in worst3.iterrows():
    print(f"\nCustomer {row['motorcyclist_id']}:")
    print(f"  Predicted (6m): {row['predicted_revenue']:,.2f} RWF")
    print(f"  Historical (total): {row['total_spent']:,.2f} RWF")
    print(f"  Ratio: {row['ratio']:.2f}x ⚠️")

# Final verdict
print("\n" + "="*80)
print("VERDICT")
print("="*80)

problems_found = (
    len(negative_preds) > 0 or
    len(huge_predictions) > 0 or 
    len(extreme_ratios) > 0 or 
    len(high_ratios) > 10
)

if problems_found:
    print("\n🚨 CRITICAL PROBLEMS DETECTED!")
    print("\nIssues found:")
    if len(negative_preds) > 0:
        print(f"  - {len(negative_preds)} negative predictions")
    if len(huge_predictions) > 0:
        print(f"  - {len(huge_predictions)} predictions > 100M RWF")
    if len(extreme_ratios) > 0:
        print(f"  - {len(extreme_ratios)} predictions > 100x historical")
    if len(high_ratios) > 10:
        print(f"  - {len(high_ratios)} predictions > 10x for established customers")
    
    print("\n⚠️  The revenue model is BROKEN and needs immediate fix!")
    print("\n📋 Next step: Run 'python fix_revenue_model.py'")
else:
    print("\n✓ No major problems detected")
    print("\nBut if predictions still look wrong, manual review recommended.")

print()
