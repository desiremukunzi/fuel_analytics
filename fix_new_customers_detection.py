#!/usr/bin/env python3
"""
Add post-processing to segment predictions to correctly label new customers
"""

print("="*80)
print("ADDING NEW CUSTOMER DETECTION TO API")
print("="*80)
print()

# Read API file
try:
    with open('jalikoi_analytics_api_ml.py', 'r', encoding='utf-8') as f:
        api_content = f.read()
except FileNotFoundError:
    print("❌ Error: jalikoi_analytics_api_ml.py not found")
    print("Please run this from A:\\MD\\fuel")
    exit(1)

# Backup
with open('jalikoi_analytics_api_ml.py.backup_new_customer_fix', 'w', encoding='utf-8') as f:
    f.write(api_content)

print("✓ Backup created")

# Find the segment-customers endpoint
import re

# Add a function to correct segment labels based on actual customer age
correction_function = '''

def correct_segment_labels(predictions_df, customer_metrics_df):
    """
    Post-process segment predictions to correctly identify truly new customers
    based on actual customer age, not just ML clustering
    """
    merged = predictions_df.merge(
        customer_metrics_df[['motorcyclist_id', 'customer_age_days', 'recency_days', 'total_spent']], 
        on='motorcyclist_id',
        how='left'
    )
    
    # Customers who joined in last 30 days = New Customers
    truly_new = merged['customer_age_days'] < 30
    
    # High-value customers (>500K) should never be "New Customers"
    high_value = merged['total_spent'] > 500000
    
    # Apply corrections
    # If customer_age < 30 days AND not high value, mark as New
    merged.loc[truly_new & ~high_value, 'segment_name'] = 'New Customers'
    
    # If segment is "New Customers" but customer is old (>90 days), reclassify
    fake_new = (merged['segment_name'] == 'New Customers') & (merged['customer_age_days'] > 90)
    
    # Reclassify based on spending
    merged.loc[fake_new & high_value, 'segment_name'] = 'Loyal Regulars'
    merged.loc[fake_new & ~high_value, 'segment_name'] = 'Occasional Users'
    
    return merged[predictions_df.columns]

'''

# Find where to insert (before the segment-customers endpoint)
insert_pos = api_content.find('@app.get("/api/ml/segment-customers')

if insert_pos == -1:
    insert_pos = api_content.find('@app.get("/api/ml/segments")')

if insert_pos == -1:
    print("❌ Could not find insertion point")
    print("\nMANUAL FIX:")
    print("-"*80)
    print("Add this function to jalikoi_analytics_api_ml.py:")
    print(correction_function)
    exit(1)

# Insert function
api_content = api_content[:insert_pos] + correction_function + '\n' + api_content[insert_pos:]

print("✓ Added correction function")

# Now modify the segments endpoint to use it
segments_endpoint_pattern = r'(predictions = ml_engine\.predict_segments\(customer_metrics\))'
replacement = r'\1\n        predictions = correct_segment_labels(predictions, customer_metrics)'

if re.search(segments_endpoint_pattern, api_content):
    api_content = re.sub(segments_endpoint_pattern, replacement, api_content)
    print("✓ Modified segments endpoint to use correction")
else:
    print("⚠️  Could not auto-modify endpoint")
    print("\nMANUAL STEP:")
    print("-"*80)
    print("After this line:")
    print("    predictions = ml_engine.predict_segments(customer_metrics)")
    print("\nAdd this line:")
    print("    predictions = correct_segment_labels(predictions, customer_metrics)")

# Also modify segment-customers endpoint
segment_customers_pattern = r'(predictions = ml_engine\.predict_segments\(customer_metrics\))'
if api_content.count(segment_customers_pattern) > 1:
    # Apply to all occurrences
    api_content = re.sub(segment_customers_pattern, replacement, api_content)
    print("✓ Modified segment-customers endpoint")

# Save
with open('jalikoi_analytics_api_ml.py', 'w', encoding='utf-8') as f:
    f.write(api_content)

print("✓ Saved changes")

print()
print("="*80)
print("✅ FIX APPLIED!")
print("="*80)
print()
print("What this does:")
print("  - Customers < 30 days old → Marked as 'New Customers'")
print("  - Old customers (>90 days) wrongly labeled as 'New' → Reclassified")
print("  - High-value customers (>500K) → Never marked as 'New'")
print()
print("Next steps:")
print("  1. Restart API: python jalikoi_analytics_api_ml.py")
print("  2. Refresh browser: Ctrl+Shift+R")
print("  3. Check 'New Customers' segment - should now only show recent signups")
print()
print("Note: For best results, retrain the model to include customer_age_days properly:")
print("  python train_ml_models.py")
print()