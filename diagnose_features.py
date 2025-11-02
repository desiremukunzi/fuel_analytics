#!/usr/bin/env python3
"""
Diagnostic script to identify the exact feature mismatch issue
Run this to see what's wrong
"""

import sys
import pickle
from pathlib import Path

print("="*80)
print("ML FEATURE MISMATCH DIAGNOSTIC")
print("="*80)
print()

# Step 1: Load the trained model and check what features it expects
print("Step 1: Checking what features the trained model expects...")
print("-"*80)

model_path = Path("ml_models/ml_models.pkl")
if not model_path.exists():
    print("❌ No trained models found at ml_models/ml_models.pkl")
    print("   Run: python train_ml_models.py")
    sys.exit(1)

try:
    with open(model_path, 'rb') as f:
        models = pickle.load(f)
    
    churn_model = models.get('churn_model')
    scaler = models.get('scaler')
    
    if churn_model is None:
        print("❌ Churn model not found in saved models")
        sys.exit(1)
    
    # Get feature names from the model
    if hasattr(churn_model, 'feature_names_in_'):
        expected_features = list(churn_model.feature_names_in_)
        print(f"✓ Model expects {len(expected_features)} features:")
        for i, feat in enumerate(expected_features, 1):
            print(f"   {i}. {feat}")
    else:
        print("⚠ Cannot determine expected features (old sklearn version?)")
        print("   Model type:", type(churn_model))
    
except Exception as e:
    print(f"❌ Error loading models: {e}")
    sys.exit(1)

print()
print("="*80)
print("Step 2: Checking what features the API provides...")
print("-"*80)

try:
    # Try to import and use the analytics engine
    from datetime import datetime, timedelta
    
    # First, try the database version
    try:
        from jalikoi_analytics_db import JalikoiAnalyticsEngine
        engine = JalikoiAnalyticsEngine()
        source = "jalikoi_analytics_db.JalikoiAnalyticsEngine"
    except:
        # Fallback to regular version
        try:
            from jalikoi_analytics_api import engine
            source = "jalikoi_analytics_api"
        except:
            print("❌ Cannot import analytics engine")
            print("   Check if jalikoi_analytics_db.py or jalikoi_analytics_api.py exists")
            sys.exit(1)
    
    print(f"✓ Using: {source}")
    
    # Fetch sample data
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    print(f"  Fetching data from {start_date} to {end_date}...")
    df = engine.fetch_data_from_db(str(start_date), str(end_date))
    
    if df is None or df.empty:
        print("❌ No data available in database")
        print("   Cannot determine what features API provides")
        sys.exit(1)
    
    print(f"  ✓ Fetched {len(df)} transactions")
    
    # Preprocess
    df = engine.preprocess_data(df)
    
    # Calculate customer metrics
    customer_metrics = engine.calculate_customer_metrics(df)
    
    provided_features = list(customer_metrics.columns)
    print(f"✓ API provides {len(provided_features)} features:")
    for i, feat in enumerate(provided_features, 1):
        print(f"   {i}. {feat}")
    
except Exception as e:
    print(f"❌ Error checking API features: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("="*80)
print("Step 3: Comparing features...")
print("-"*80)

if 'expected_features' in locals() and 'provided_features' in locals():
    expected_set = set(expected_features)
    provided_set = set(provided_features)
    
    missing = expected_set - provided_set
    extra = provided_set - expected_set
    
    if missing:
        print(f"\n❌ MISSING FEATURES (Model expects but API doesn't provide):")
        for feat in sorted(missing):
            print(f"   - {feat}")
    
    if extra:
        print(f"\n⚠  EXTRA FEATURES (API provides but model doesn't expect):")
        for feat in sorted(extra):
            print(f"   - {feat}")
    
    if not missing and not extra:
        print("\n✅ FEATURES MATCH! No mismatch detected.")
        print("   The issue might be elsewhere.")
    else:
        print(f"\n🔧 SOLUTION:")
        print(f"   The model and API have different features.")
        print(f"   You need to retrain the models with the correct features.")
        print()
        print(f"   Run this command:")
        print(f"   python train_ml_models.py")

else:
    print("❌ Could not complete comparison")

print()
print("="*80)
print("DIAGNOSIS COMPLETE")
print("="*80)
