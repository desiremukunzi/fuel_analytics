#!/usr/bin/env python3
"""
Complete fix for ML feature mismatch and date range issues
Run this to fix everything!
"""

import os
import shutil
from pathlib import Path

print("="*80)
print("JALIKOI ML - COMPLETE FIX SCRIPT")
print("="*80)
print()

# Step 1: Delete old models
print("Step 1: Removing old ML models...")
model_dir = Path("ml_models")
if model_dir.exists():
    try:
        shutil.rmtree(model_dir)
        print("✓ Deleted old models")
    except Exception as e:
        print(f"⚠ Could not delete models: {e}")
        print("  Please manually delete the ml_models folder")
        input("Press Enter after deleting the folder manually...")
else:
    print("✓ No old models found")

# Step 2: Create fresh directory
print("\nStep 2: Creating fresh model directory...")
model_dir.mkdir(exist_ok=True)
print("✓ Created ml_models directory")

# Step 3: Train fresh models
print("\nStep 3: Training fresh models...")
print("This will take 3-7 minutes...")
print("-"*80)
print()

try:
    from train_ml_models import train_all_models
    train_all_models()
    
    print()
    print("="*80)
    print("✅ FIX COMPLETE!")
    print("="*80)
    print()
    print("Next steps:")
    print("1. Restart your API:")
    print("   python jalikoi_analytics_api_ml.py")
    print()
    print("2. Refresh your browser (Ctrl+Shift+R)")
    print()
    print("3. Test the tabs:")
    print("   - 🤖 Predictions")
    print("   - 👥 Segments")
    print("   - 🛡️ Anomalies")
    print()
    print("All should work now!")
    print("="*80)
    
except Exception as e:
    print()
    print("="*80)
    print("❌ ERROR DURING TRAINING")
    print("="*80)
    print(f"\nError: {e}")
    print("\nTroubleshooting:")
    print("1. Check database connection in db_config.py")
    print("2. Make sure you have transaction data in database")
    print("3. Check database credentials are correct")
    print("4. Try running manually: python train_ml_models.py")
    print()
    import traceback
    traceback.print_exc()
