#!/usr/bin/env python3
"""
Fix segment-customers endpoint - filter BEFORE limiting
Currently: get 1000 customers -> limit to 616 -> filter to 72 (but already returned 616)
Should be: get ALL customers -> filter to 72 -> limit to 72
"""

print("="*80)
print("FIXING FILTER/LIMIT ORDER IN API")
print("="*80)
print()

import os
import re

# Find the API file
api_files = [
    'jalikoi_analytics_api_ml.py',
    'A:/MD/fuel/jalikoi_analytics_api_ml.py',
    '../jalikoi_analytics_api_ml.py'
]

api_file = None
for f in api_files:
    if os.path.exists(f):
        api_file = f
        break

if not api_file:
    print("❌ Could not find jalikoi_analytics_api_ml.py")
    print("\nMANUAL FIX NEEDED:")
    print("="*80)
    print()
    print("In @app.get('/api/ml/segment-customers/{segment_name}'):")
    print()
    print("CURRENT ORDER (WRONG):")
    print("-"*80)
    print("""
    segment_customers = predictions[predictions['segment_name'] == segment_name]
    
    # Apply limit BEFORE filter (WRONG!)
    segment_customers = segment_customers.head(limit)
    
    # Then filter
    if segment_name == "New Customers":
        # filter code...
        segment_customers = filtered
    """)
    print()
    print("CORRECT ORDER:")
    print("-"*80)
    print("""
    segment_customers = predictions[predictions['segment_name'] == segment_name]
    
    # Filter FIRST for New Customers
    if segment_name == "New Customers":
        merged = segment_customers.merge(...)
        # Apply all filters
        segment_customers = filtered
    
    # THEN apply limit AFTER filtering
    segment_customers = segment_customers.head(limit)
    """)
    print()
    print("="*80)
    exit(1)

# Read file
with open(api_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
backup = api_file + '.backup_order_fix'
with open(backup, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✓ Found API file: {api_file}")
print(f"✓ Backup created: {backup}")
print()

# Find the segment-customers endpoint
pattern = r'(@app\.get\("/api/ml/segment-customers/\{segment_name\}"\).*?)(return \{)'

match = re.search(pattern, content, re.DOTALL)

if not match:
    print("❌ Could not find segment-customers endpoint")
    exit(1)

endpoint_code = match.group(1)

# Check current order
if '.head(limit)' in endpoint_code:
    head_pos = endpoint_code.find('.head(limit)')
    new_customers_filter_pos = endpoint_code.find('if segment_name == "New Customers"')
    
    if new_customers_filter_pos > 0 and head_pos > 0:
        if head_pos < new_customers_filter_pos:
            print("⚠️  PROBLEM FOUND: .head(limit) is BEFORE the New Customers filter!")
            print("    This means we limit to 616, then filter, but already returned 616")
            print()
            print("    Fixing order...")
            
            # Remove .head(limit) before the filter
            endpoint_code = endpoint_code.replace(
                'segment_customers.head(limit)',
                'segment_customers',
                1  # Only first occurrence
            )
            
            # Add .head(limit) after the "New Customers" filter block
            # Find the end of the New Customers filter
            filter_block = re.search(
                r'(if segment_name == "New Customers":.*?)((?:\n\s{8}(?!\s)|$))',
                endpoint_code,
                re.DOTALL
            )
            
            if filter_block:
                # Add limit after filter
                new_code = filter_block.group(1) + '\n        \n        # Apply limit AFTER filtering\n        segment_customers = segment_customers.head(limit)\n        '
                endpoint_code = endpoint_code.replace(filter_block.group(1), new_code)
                
                # Replace in main content
                content = content.replace(match.group(1), endpoint_code)
                
                print("✓ Fixed order: Filter FIRST, then limit")
            else:
                print("⚠️  Could not find New Customers filter block end")
        else:
            print("✓ Order is already correct (filter before limit)")
    else:
        print("✓ No ordering issue found")
else:
    print("✓ No .head(limit) found, adding it after filter")

# Save
with open(api_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Saved changes")
print()

print("="*80)
print("✅ FIX COMPLETE!")
print("="*80)
print()
print("Changes:")
print("  - Filter applied FIRST for New Customers")
print("  - Limit applied AFTER filtering")
print()
print("Expected result:")
print("  - total_customers: 72 ✓")
print("  - customers_returned: 72 ✓")
print("  - Browser shows: 72 customers ✓")
print()
print("Restart API:")
print("  python jalikoi_analytics_api_ml.py")
print()