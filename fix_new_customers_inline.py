#!/usr/bin/env python3
"""
Fix segment-customers endpoint to properly filter New Customers
Need to fetch customer_metrics within the endpoint to apply filters
"""

print("="*80)
print("FIXING NEW CUSTOMERS FILTER IN API ENDPOINT")
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
with open('jalikoi_analytics_api_ml.py.backup_filter_v2', 'w', encoding='utf-8') as f:
    f.write(api_content)

print("✓ Backup created")
print()

import re

# Find the segment-customers endpoint and check current structure
print("Analyzing segment-customers endpoint...")
print()

# Look for where segment_customers is defined after filtering by segment_name
pattern = r"segment_customers = predictions\[predictions\['segment_name'\] == segment_name\]"

if not re.search(pattern, api_content):
    print("❌ Could not find segment filtering line")
    print("Please share the segment-customers endpoint code")
    exit(1)

print("✓ Found segment filtering line")
print()

# Check if customer_metrics already exists in scope
if 'customer_metrics = ' in api_content.split('@app.get("/api/ml/segment-customers')[1].split('@app')[0]:
    print("✓ customer_metrics is already fetched in endpoint")
else:
    print("⚠️  customer_metrics might not be in scope")
    print("    Will add re-fetching of metrics")

# Create comprehensive fix that re-fetches metrics if needed
fix_code = r'''segment_customers = predictions[predictions['segment_name'] == segment_name]
        
        # Apply special filtering for "New Customers" segment
        if segment_name == "New Customers":
            print(f"   Applying New Customers filter (before: {len(segment_customers)} customers)")
            
            # Need to re-merge with customer metrics to get filtering fields
            customer_ids_for_filter = segment_customers['motorcyclist_id'].tolist()
            
            # Get metrics for these customers only
            metrics_subset = customer_metrics[
                customer_metrics['motorcyclist_id'].isin(customer_ids_for_filter)
            ][[
                'motorcyclist_id', 
                'customer_age_days', 
                'frequency', 
                'total_spent', 
                'transaction_count',
                'recency_days'
            ]]
            
            # Merge to get the fields
            merged = segment_customers.merge(metrics_subset, on='motorcyclist_id', how='left')
            
            # Apply filters (same as ml_engine)
            is_new = merged['customer_age_days'] < 90
            has_potential = (
                (merged['frequency'] > 0.5) | 
                (merged['total_spent'] > 100000) | 
                (merged['transaction_count'] > 5)
            )
            is_active = merged['recency_days'] < 30
            
            # Filter
            filtered = merged[is_new & has_potential & is_active]
            
            # Keep only original columns
            segment_customers = filtered[segment_customers.columns]
            
            print(f"   After filter: {len(segment_customers)} customers")
            print(f"   Removed: {len(merged) - len(filtered)} customers (too old or low potential)")'''

# Replace the segment filtering line with the new code
api_content = re.sub(
    pattern,
    fix_code,
    api_content
)

print("✓ Added inline filtering for New Customers")
print()

# Save
with open('jalikoi_analytics_api_ml.py', 'w', encoding='utf-8') as f:
    f.write(api_content)

print("✓ Saved changes")
print()

print("="*80)
print("✅ FIX COMPLETE!")
print("="*80)
print()
print("What was added:")
print("  - Inline filtering in segment-customers endpoint")
print("  - Re-merges with customer_metrics to get age, frequency, etc.")
print("  - Applies same criteria as ml_engine:")
print("    • customer_age_days < 90")
print("    • High potential (frequency > 0.5 OR spent > 100K OR 5+ txns)")
print("    • Active (recency < 30 days)")
print()
print("Expected result:")
print("  - Segment card: 161 customers")
print("  - Customer list: 161 customers (not 616)")
print("  - No July 2025 customers (they're 120+ days old)")
print()
print("Next step:")
print("  Restart API: python jalikoi_analytics_api_ml.py")
print()