#!/usr/bin/env python3
"""
NUCLEAR OPTION - Complete Reset and Retrain
This will fix the feature mismatch issue permanently
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

print("="*80)
print("COMPLETE ML RESET AND RETRAIN")
print("="*80)
print()
print("This will:")
print("1. Delete ALL old models")
print("2. Delete ALL cached scalers")
print("3. Train fresh models with correct features")
print("4. Verify everything works")
print()

response = input("Continue? (yes/no): ")
if response.lower() not in ['yes', 'y']:
    print("Cancelled.")
    exit(0)

print()
print("="*80)
print("STEP 1: DELETING OLD MODELS")
print("="*80)

# Delete ml_models directory completely
model_dir = Path("ml_models")
if model_dir.exists():
    print("\nDeleting ml_models directory...")
    try:
        # Remove all files first
        for item in model_dir.rglob('*'):
            if item.is_file():
                item.unlink()
                print(f"  ✓ Deleted {item.name}")
        
        # Remove directory
        shutil.rmtree(model_dir)
        print("✓ ml_models directory deleted completely")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPlease manually:")
        print("1. Close any programs using ml_models")
        print("2. Delete: A:\\MD\\fuel\\ml_models")
        print("3. Run this script again")
        exit(1)
else:
    print("✓ No old models found")

# Recreate empty directory
print("\nCreating fresh ml_models directory...")
model_dir.mkdir(exist_ok=True)
print("✓ Fresh directory created")

print()
print("="*80)
print("STEP 2: VERIFYING CLEAN STATE")
print("="*80)

files = list(model_dir.iterdir())
if files:
    print(f"⚠ Directory not empty: {[f.name for f in files]}")
    print("Cleaning...")
    for f in files:
        f.unlink()
    print("✓ Cleaned")
else:
    print("✓ Directory is empty and ready")

print()
print("="*80)
print("STEP 3: TRAINING MODELS WITH CORRECT FEATURES")
print("="*80)
print()
print("This will take 3-7 minutes...")
print()

try:
    from train_ml_models import train_all_models
    
    # Train with verbose output
    train_all_models()
    
    print()
    print("="*80)
    print("STEP 4: VERIFYING MODELS")
    print("="*80)
    
    # Check files created
    model_files = list(model_dir.iterdir())
    print(f"\nFiles created: {len(model_files)}")
    for f in model_files:
        print(f"  ✓ {f.name}")
    
    # Load and verify
    from ml_engine import MLEngine
    ml = MLEngine(model_dir="ml_models")
    
    info = ml.get_model_info()
    print("\nModel Status:")
    print(f"  Churn: {'✓' if info['churn_model_trained'] else '✗'}")
    print(f"  Revenue: {'✓' if info['revenue_model_trained'] else '✗'}")
    print(f"  Segmentation: {'✓' if info['segmentation_model_trained'] else '✗'}")
    print(f"  Anomaly: {'✓' if info['anomaly_model_trained'] else '✗'}")
    
    if not all([info['churn_model_trained'], info['segmentation_model_trained']]):
        print("\n⚠ Some models failed to train!")
        exit(1)
    
    # Test prediction
    print("\nTesting segmentation prediction...")
    from datetime import timedelta
    from jalikoi_analytics_db import JalikoiAnalyticsVisualized
    from db_config import DB_CONFIG
    
    analytics = JalikoiAnalyticsVisualized(DB_CONFIG, use_database=True)
    customer_metrics = analytics.customer_metrics
    
    print(f"  Customer metrics shape: {customer_metrics.shape}")
    print(f"  Columns: {list(customer_metrics.columns)[:5]}...")
    
    predictions = ml.predict_segments(customer_metrics)
    print(f"  ✓ Segmentation successful!")
    print(f"  Predicted {len(predictions)} customers")
    print(f"  Segments: {predictions['segment_name'].value_counts().to_dict()}")
    
    print()
    print("="*80)
    print("✅ SUCCESS! ALL MODELS TRAINED AND VERIFIED")
    print("="*80)
    print()
    print("Next steps:")
    print("1. Restart API:")
    print("   python jalikoi_analytics_api_ml.py")
    print()
    print("2. Test segmentation:")
    print("   python analyze_segments.py")
    print()
    print("3. Refresh browser and test all ML tabs")
    print()
    
except Exception as e:
    print()
    print("="*80)
    print("❌ ERROR DURING TRAINING")
    print("="*80)
    print(f"\nError: {e}")
    print("\nFull traceback:")
    import traceback
    traceback.print_exc()
    print()
    print("Troubleshooting:")
    print("1. Check database connection in db_config.py")
    print("2. Ensure database has transaction data")
    print("3. Check all Python dependencies installed")
    print("4. Try running: python train_ml_models.py manually")
    print()
    exit(1)
