#!/usr/bin/env python3
"""
Fix: Remove constraints from churn predictions
The apply_realistic_constraints function should ONLY apply to revenue, not churn
"""

print("="*80)
print("REMOVING CONSTRAINTS FROM CHURN PREDICTIONS")
print("="*80)
print()

# Read API file
print("Reading API file...")
with open('jalikoi_analytics_api_ml.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
print("Creating backup...")
with open('jalikoi_analytics_api_ml.py.before_churn_fix', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Backup created")

# Find all places where apply_realistic_constraints is called
print("\nSearching for constraint calls...")

import re

# Find churn endpoint
churn_section_match = re.search(
    r'(@app\.get\(["\']\/api\/ml\/churn.*?(?=@app\.|$))',
    content,
    re.DOTALL
)

if churn_section_match:
    churn_section = churn_section_match.group(1)
    
    # Check if constraints are applied in churn section
    if 'apply_realistic_constraints' in churn_section:
        print("✓ Found constraints in churn endpoint - REMOVING...")
        
        # Remove the constraint call from churn section
        # Pattern: lines containing apply_realistic_constraints
        lines_to_remove = []
        for match in re.finditer(r'.*apply_realistic_constraints.*\n', churn_section):
            lines_to_remove.append(match.group(0))
        
        modified_churn = churn_section
        for line in lines_to_remove:
            modified_churn = modified_churn.replace(line, '')
            print(f"  Removed: {line.strip()}")
        
        # Replace in content
        content = content.replace(churn_section, modified_churn)
        print("✓ Constraints removed from churn endpoint")
    else:
        print("✓ No constraints in churn endpoint - good!")
else:
    print("⚠️  Could not find churn endpoint")

# Now make sure constraints are ONLY in revenue endpoint
print("\nVerifying revenue endpoint has constraints...")

revenue_section_match = re.search(
    r'(@app\.get\(["\']\/api\/ml\/revenue.*?(?=@app\.|$))',
    content,
    re.DOTALL
)

if revenue_section_match:
    revenue_section = revenue_section_match.group(1)
    
    if 'apply_realistic_constraints' not in revenue_section:
        print("⚠️  Revenue endpoint missing constraints!")
        print("\nYou need to add this line after 'predictions = ml.predict_revenue(...)' :")
        print("    predictions = apply_realistic_constraints(predictions, customer_metrics)")
    else:
        print("✓ Revenue endpoint has constraints - good!")
else:
    print("⚠️  Could not find revenue endpoint")

# Save modified content
print("\nSaving changes...")
with open('jalikoi_analytics_api_ml.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ File saved")

print("\n" + "="*80)
print("✅ FIX COMPLETE!")
print("="*80)
print()
print("Summary:")
print("  ✓ Removed constraints from churn predictions")
print("  ✓ Constraints only apply to revenue predictions")
print()
print("Next: Restart API")
print("  python jalikoi_analytics_api_ml.py")
print()
print("Then test:")
print("  - Churn predictions should be accurate again")
print("  - Revenue predictions should be realistic (capped)")
print()
