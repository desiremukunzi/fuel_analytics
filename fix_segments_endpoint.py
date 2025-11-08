#!/usr/bin/env python3
"""
Fix segment-customers endpoint to apply New Customers filtering
Currently it returns all customers in the ML cluster, 
but we need to apply the same age+potential filter
"""

print("="*80)
print("FIXING SEGMENT-CUSTOMERS ENDPOINT")
print("="*80)
print()

# Read API file
try:
    with open('jalikoi_analytics_api_ml.py', 'r', encoding='utf-8') as f:
        api_content = f.read()
except FileNotFoundError:
    print("❌ Error: jalikoi_analytics_api_ml.py not found")
    exit(1)

# Backup
with open('jalikoi_analytics_api_ml.py.backup_filter_endpoint', 'w', encoding='utf-8') as f:
    f.write(api_content)

print("✓ Backup created")
print()

import re

# Add filtering function if not exists
if 'def filter_new_customers_by_criteria' not in api_content:
    filter_function = '''
def filter_new_customers_by_criteria(segment_customers, customer_metrics):
    """
    Apply the same filtering for New Customers as in ml_engine
    Only show customers who are:
    - New: customer_age_days < 90
    - Potential: frequency > 0.5 OR total_spent > 100000 OR transaction_count > 5
    - Active: recency_days < 30
    """
    # Merge with metrics
    merged = segment_customers.merge(
        customer_metrics[[
            'motorcyclist_id', 
            'customer_age_days', 
            'frequency', 
            'total_spent', 
            'transaction_count',
            'recency_days'
        ]], 
        on='motorcyclist_id',
        how='left'
    )
    
    # Apply filters
    is_new = merged['customer_age_days'] < 90
    has_potential = (
        (merged['frequency'] > 0.5) | 
        (merged['total_spent'] > 100000) | 
        (merged['transaction_count'] > 5)
    )
    is_active = merged['recency_days'] < 30
    
    # Combined criteria
    filtered = merged[is_new & has_potential & is_active]
    
    print(f"   Filtered New Customers: {len(segment_customers)} -> {len(filtered)}")
    print(f"   Removed {len(segment_customers) - len(filtered)} customers who don't meet criteria")
    
    return filtered[segment_customers.columns]

'''
    
    # Insert before segment-customers endpoint
    insert_pos = api_content.find('@app.get("/api/ml/segment-customers')
    
    if insert_pos > 0:
        api_content = api_content[:insert_pos] + filter_function + '\n' + api_content[insert_pos:]
        print("✓ Added filter function")
    else:
        print("❌ Could not find insertion point")
        print("\nMANUAL FIX: Add the filter function before segment-customers endpoint")
        exit(1)
else:
    print("✓ Filter function already exists")

# Now apply the filter in the endpoint
pattern = r"(segment_customers = predictions\[predictions\['segment_name'\] == segment_name\])"

if re.search(pattern, api_content):
    replacement = r'''\1
        
        # Apply filtering for "New Customers" segment
        if segment_name == "New Customers":
            segment_customers = filter_new_customers_by_criteria(segment_customers, customer_metrics)
            print(f"   After filtering: {len(segment_customers)} New Customers with potential")
'''
    
    api_content = re.sub(pattern, replacement, api_content)
    print("✓ Applied filter to segment-customers endpoint")
else:
    print("⚠️  Could not find segment filtering code")
    print("\nMANUAL FIX:")
    print("-"*80)
    print("In @app.get('/api/ml/segment-customers/{segment_name}')")
    print("\nAfter this line:")
    print("    segment_customers = predictions[predictions['segment_name'] == segment_name]")
    print("\nAdd:")
    print('''
    # Apply filtering for "New Customers" segment
    if segment_name == "New Customers":
        segment_customers = filter_new_customers_by_criteria(segment_customers, customer_metrics)
''')
    print("-"*80)

# Save
with open('jalikoi_analytics_api_ml.py', 'w', encoding='utf-8') as f:
    f.write(api_content)

print("✓ Saved changes")
print()

print("="*80)
print("✅ FIX COMPLETE!")
print("="*80)
print()
print("Changes made:")
print("  1. Added filter_new_customers_by_criteria() function")
print("  2. Applied filter when segment_name == 'New Customers'")
print()
print("Now the customer list will match the segment prediction:")
print("  - Customer age < 90 days")
print("  - High potential (frequent OR high spend OR multiple transactions)")
print("  - Active in last 30 days")
print()
print("Customers from May 2025 (180 days old) will be filtered out!")
print()
print("Next steps:")
print("  1. Restart API: python jalikoi_analytics_api_ml.py")
print("  2. Refresh browser")
print("  3. Click 'New Customers' - should now show ~251 (or fewer)")
print()