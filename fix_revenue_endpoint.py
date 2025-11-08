#!/usr/bin/env python3
"""
Manually fix revenue endpoint to apply constraints
"""

import re

print("="*80)
print("FIXING REVENUE ENDPOINT MANUALLY")
print("="*80)
print()

# Read API file
print("Reading API file...")
with open('jalikoi_analytics_api_ml.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check if constraint function exists
if 'apply_realistic_constraints' not in content:
    print("✗ Constraint function not found!")
    print("  Run: python add_api_constraints.py first")
    exit(1)

print("✓ Constraint function found")

# Find the revenue forecast endpoint
print("\nSearching for revenue forecast endpoint...")

# Pattern to find the function
patterns = [
    r'(@app\.get\(["\']\/api\/ml\/revenue-forecast.*?\n.*?def .*?\(.*?\):.*?)(\n    .*?return )',
    r'(def get_revenue_forecast.*?\(.*?\):.*?)(\n    .*?return )',
]

found = False
for pattern in patterns:
    matches = list(re.finditer(pattern, content, re.DOTALL))
    if matches:
        print(f"✓ Found revenue endpoint using pattern")
        found = True
        break

if not found:
    print("⚠️  Could not automatically find revenue endpoint")
    print("\nManual instructions:")
    print("-"*80)
    print("Find this in jalikoi_analytics_api_ml.py:")
    print()
    print("    predictions = ml.predict_revenue(customer_metrics)")
    print()
    print("Add this line IMMEDIATELY after it:")
    print()
    print("    predictions = apply_realistic_constraints(predictions, customer_metrics)")
    print()
    print("-"*80)
    exit(1)

# Show what we found
print("\nModifying revenue endpoint...")

# Look for where predictions are made
predict_pattern = r'(predictions\s*=\s*ml\.predict_revenue\([^)]+\))'

# Find all occurrences in the revenue forecast function
modified = False
new_content = content

for match in re.finditer(predict_pattern, content):
    line_end = match.end()
    
    # Check if constraints already applied right after this line
    next_50_chars = content[line_end:line_end+100]
    if 'apply_realistic_constraints' in next_50_chars:
        print("⚠️  Constraints already applied at this location, skipping...")
        continue
    
    # Find the end of this line
    newline_pos = content.find('\n', line_end)
    if newline_pos == -1:
        newline_pos = len(content)
    
    # Get indentation
    line_start = content.rfind('\n', 0, match.start()) + 1
    indent = content[line_start:match.start()]
    
    # Insert constraint call
    constraint_line = f"\n{indent}predictions = apply_realistic_constraints(predictions, customer_metrics)"
    
    new_content = (
        new_content[:newline_pos] + 
        constraint_line + 
        new_content[newline_pos:]
    )
    
    modified = True
    print(f"✓ Added constraint call after line {content[:match.start()].count(chr(10)) + 1}")

if not modified:
    print("\n⚠️  Could not automatically modify the code")
    print("\nMANUAL FIX REQUIRED:")
    print("-"*80)
    print("\n1. Open: jalikoi_analytics_api_ml.py")
    print("\n2. Find this line:")
    print("   predictions = ml.predict_revenue(customer_metrics)")
    print("\n3. Add this line IMMEDIATELY after it (same indentation):")
    print("   predictions = apply_realistic_constraints(predictions, customer_metrics)")
    print("\n4. Save and restart API")
    print("-"*80)
    exit(1)

# Backup
print("\nCreating backup...")
with open('jalikoi_analytics_api_ml.py.before_revenue_fix', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Backup created")

# Save
print("\nSaving modified file...")
with open('jalikoi_analytics_api_ml.py', 'w', encoding='utf-8') as f:
    f.write(new_content)
print("✓ File saved")

print("\n" + "="*80)
print("✅ REVENUE ENDPOINT FIXED!")
print("="*80)
print()
print("Now restart your API:")
print("  python jalikoi_analytics_api_ml.py")
print()
print("Then test in browser - revenue predictions should be realistic!")
print()
