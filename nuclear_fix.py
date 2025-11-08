#!/usr/bin/env python3
"""
ULTIMATE ML FIX - Delete old models and retrain from scratch
"""

import shutil
import sys
from pathlib import Path

print("="*80)
print("ULTIMATE ML FIX - NUCLEAR OPTION")
print("="*80)
print()

# Step 1: Delete ALL old models
print("Step 1: Deleting old models...")
model_dir = Path("ml_models")

if model_dir.exists():
    try:
        shutil.rmtree(model_dir)
        print("✓ Deleted old models")
    except Exception as e:
        print(f"✗ Error deleting: {e}")
        print("  Manually delete ml_models folder and run again")
        sys.exit(1)
else:
    print("  No old models found")

# Recreate directory
model_dir.mkdir(exist_ok=True)
print("✓ Created fresh directory")

# Step 2: Import and retrain
print("\nStep 2: Now retraining ALL models from scratch...")
print("-"*80)
print()

# Run the retraining script by importing it
try:
    exec(open("retrain_all_models.py").read())
except Exception as e:
    print(f"\n✗ Retraining failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*80)
print("✅ COMPLETE! Models retrained successfully!")
print("="*80)
print()
print("NOW: Restart your API")
print()
print("  1. Stop API (Ctrl+C if running)")
print("  2. Start: python jalikoi_analytics_api_ml.py")
print("  3. Wait 30 seconds")
print("  4. Refresh browser (Ctrl+F5)")
print()
