#!/usr/bin/env python3
"""
Automatic fix for jalikoi_analytics_api_ml.py
This replaces engine.calculate_customer_metrics() with the working version
"""

import os
import shutil
from datetime import datetime

print("="*80)
print("AUTOMATIC API FIX")
print("="*80)
print()

api_file = 'jalikoi_analytics_api_ml.py'

# Backup first
backup_file = f'{api_file}.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
print(f"Creating backup: {backup_file}")
shutil.copy(api_file, backup_file)
print("✓ Backup created")
print()

# Read the file
print("Reading API file...")
with open(api_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Add import statement after the ml_engine import section
print("Adding import for working calculate_customer_metrics...")
import_marker = '# Import everything from the original API'
if import_marker in content:
    parts = content.split(import_marker)
    new_import = '''# Import working metrics calculator
from train_ml_models import calculate_customer_metrics as calc_customer_metrics

'''
    if 'from train_ml_models import calculate_customer_metrics' not in content:
        content = parts[0] + new_import + import_marker + parts[1]
        print("✓ Import added")
    else:
        print("✓ Import already exists")
else:
    print("⚠ Could not find import section marker")

# Replace all instances
print("\nReplacing engine.calculate_customer_metrics() calls...")
replacements = 0
old_pattern = 'customer_metrics = engine.calculate_customer_metrics(df)'
new_pattern = 'customer_metrics = calc_customer_metrics(df)'

if old_pattern in content:
    count = content.count(old_pattern)
    content = content.replace(old_pattern, new_pattern)
    replacements = count
    print(f"✓ Replaced {count} occurrences")
else:
    print("✓ No replacements needed (already fixed or different pattern)")

# Write back
print("\nWriting fixed file...")
with open(api_file, 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ File updated")

print()
print("="*80)
print("FIX COMPLETE!")
print("="*80)
print()
print(f"Backup saved as: {backup_file}")
print(f"Replacements made: {replacements}")
print()
print("Next steps:")
print("1. Restart your API:")
print("   python jalikoi_analytics_api_ml.py")
print()
print("2. Test the endpoints:")
print("   curl http://localhost:8000/api/ml/churn-predictions")
print()
print("3. If there are issues, restore backup:")
print(f"   copy {backup_file} {api_file}")
print()
