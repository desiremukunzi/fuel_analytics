#!/usr/bin/env python3
"""
FINAL FIX - Force reload models after training
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import sys

print("="*80)
print("COMPLETE ML RESET - FINAL VERSION")
print("="*80)
print()

# Step 1: Delete old models
print("STEP 1: Deleting old models...")
print("-"*80)

model_dir = Path("ml_models")
if model_dir.exists():
    try:
        shutil.rmtree(model_dir)
        print("✓ Deleted old models")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nManually delete: A:\\MD\\fuel\\ml_models")
        print("Then run this script again")
        sys.exit(1)
else:
    print("✓ No old models")

# Recreate
model_dir.mkdir(exist_ok=True)
print("✓ Fresh directory created")

# Step 2: Clear Python cache
print("\nSTEP 2: Clearing Python cache...")
print("-"*80)

# Remove any cached ml_engine imports
if 'ml_engine' in sys.modules:
    del sys.modules['ml_engine']
    print("✓ Cleared ml_engine from cache")

# Step 3: Train models
print("\nSTEP 3: Training fresh models...")
print("-"*80)
print("This takes 3-7 minutes...\n")

try:
    from train_ml_models import train_all_models
    train_all_models()
    print("\n✓ Training completed")
    
except Exception as e:
    print(f"\n❌ Training failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Force reload and test
print("\nSTEP 4: Testing models...")
print("-"*80)

# Clear cache again before loading
if 'ml_engine' in sys.modules:
    del sys.modules['ml_engine']

# Import fresh
from ml_engine import MLEngine

# Create NEW instance (don't use any cached instance)
ml = MLEngine(model_dir="ml_models")

# Verify
info = ml.get_model_info()
print("\nModel Status:")
print(f"  Churn: {'✓ Trained' if info['churn_model_trained'] else '✗ Not Trained'}")
print(f"  Revenue: {'✓ Trained' if info['revenue_model_trained'] else '✗ Not Trained'}")
print(f"  Segmentation: {'✓ Trained' if info['segmentation_model_trained'] else '✗ Not Trained'}")
print(f"  Anomaly: {'✓ Trained' if info['anomaly_model_trained'] else '✗ Not Trained'}")

if not info['segmentation_model_trained']:
    print("\n❌ Segmentation model not trained!")
    sys.exit(1)

# Test with actual data
print("\nTesting segmentation...")

try:
    from jalikoi_analytics_db import JalikoiAnalyticsVisualized
    from db_config import DB_CONFIG
    
    analytics = JalikoiAnalyticsVisualized(DB_CONFIG, use_database=True)
    customer_metrics = analytics.customer_metrics
    
    print(f"  Customer data: {len(customer_metrics)} customers")
    print(f"  Columns available: {len(customer_metrics.columns)}")
    
    # Check required columns
    required = ['recency_days', 'frequency', 'transaction_count', 'total_spent',
                'avg_transaction', 'std_transaction', 'total_liters', 'station_diversity',
                'failure_rate', 'app_usage_rate', 'customer_age_days']
    
    missing = [col for col in required if col not in customer_metrics.columns]
    if missing:
        print(f"\n⚠ Missing columns: {missing}")
        print("  Available columns:", list(customer_metrics.columns))
    else:
        print(f"  ✓ All required columns present")
    
    # Try prediction
    predictions = ml.predict_segments(customer_metrics)
    
    print(f"\n✓ SUCCESS! Segmented {len(predictions)} customers")
    print("\nSegment distribution:")
    for seg, count in predictions['segment_name'].value_counts().items():
        print(f"  {seg}: {count} customers")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80)
    print("\nYou can now:")
    print("1. Restart API: python jalikoi_analytics_api_ml.py")
    print("2. Run analysis: python analyze_segments.py")
    print("3. Test in browser")
    print()
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    print("\nDEBUG INFO:")
    print("-"*80)
    
    # Debug: Check what the model expects
    import pickle
    with open('ml_models/ml_models.pkl', 'rb') as f:
        models = pickle.load(f)
    
    seg_model = models.get('segmentation_model')
    scaler = models.get('scaler')
    
    if scaler and hasattr(scaler, 'feature_names_in_'):
        print("Scaler expects these features:")
        for feat in scaler.feature_names_in_:
            print(f"  - {feat}")
    
    print("\nCustomer metrics has these columns:")
    for col in customer_metrics.columns:
        print(f"  - {col}")
    
    print("\n" + "="*80)
    import traceback
    traceback.print_exc()
    sys.exit(1)
