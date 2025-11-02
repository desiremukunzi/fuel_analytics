#!/usr/bin/env python3
"""
Force retrain - completely reset and retrain all models
"""

import os
import shutil
from pathlib import Path

print("="*80)
print("FORCE RETRAIN - COMPLETE RESET")
print("="*80)
print()

# Step 1: Delete ml_models folder
model_dir = Path("ml_models")
if model_dir.exists():
    print("Deleting old models...")
    try:
        # Try to remove all files first
        for item in model_dir.iterdir():
            if item.is_file():
                item.unlink()
                print(f"  ✓ Deleted {item.name}")
        # Then remove directory
        model_dir.rmdir()
        print("✓ ml_models folder deleted")
    except Exception as e:
        print(f"❌ Error deleting: {e}")
        print("\nPlease manually:")
        print("1. Close any programs using ml_models folder")
        print("2. Delete A:\\MD\\fuel\\ml_models folder")
        print("3. Run this script again")
        input("\nPress Enter after deleting...")

# Step 2: Create fresh folder
print("\nCreating fresh ml_models folder...")
model_dir.mkdir(exist_ok=True)
print("✓ Fresh folder created")

# Step 3: Verify it's empty
files = list(model_dir.iterdir())
if files:
    print(f"⚠ Folder not empty! Contains: {[f.name for f in files]}")
else:
    print("✓ Folder is empty and ready")

print()
print("="*80)
print("READY TO TRAIN")
print("="*80)
print()
print("Now run: python train_ml_models.py")
print()
