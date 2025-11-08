#!/usr/bin/env python3
"""
Add realistic constraints to revenue predictions in the API
This fixes predictions AFTER the model makes them
"""

import sys

print("="*80)
print("ADDING REALISTIC CONSTRAINTS TO API")
print("="*80)
print()

# First, let's check the current API file
print("Checking API file...")

try:
    with open('jalikoi_analytics_api_ml.py', 'r', encoding='utf-8') as f:
        api_content = f.read()
    print("✓ API file loaded")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Check if we already added constraints
if 'apply_realistic_constraints' in api_content:
    print("⚠️  Constraints already added to API!")
    print("   Models need retraining instead.")
    print("   Run: python fix_revenue_strict.py")
    sys.exit(0)

print("\nAdding constraint function to API...")

# Create the constraint function
constraint_function = '''
def apply_realistic_constraints(predictions_df, customer_metrics_df):
    """
    Apply realistic constraints to revenue predictions
    
    Rules:
    1. Max 2x historical spending
    2. Absolute ceiling: 50M RWF
    3. Non-negative
    4. New customers (<5 trans): Max 1.5x
    5. Inactive (>30 days): Reduce by inactivity factor
    """
    import numpy as np
    import pandas as pd
    
    # Merge to get historical data
    if 'motorcyclist_id' in predictions_df.columns and 'motorcyclist_id' in customer_metrics_df.columns:
        merged = predictions_df.merge(
            customer_metrics_df[['motorcyclist_id', 'total_spent', 'transaction_count', 'recency_days']], 
            on='motorcyclist_id', 
            how='left'
        )
    else:
        # Already merged or different structure
        merged = predictions_df.copy()
    
    original_predictions = merged['predicted_revenue'].copy()
    
    # Rule 1: Non-negative
    merged['predicted_revenue'] = merged['predicted_revenue'].clip(lower=0)
    
    # Rule 2: Max 2x historical spending
    if 'total_spent' in merged.columns:
        max_allowed = merged['total_spent'] * 2
        merged['predicted_revenue'] = np.minimum(merged['predicted_revenue'], max_allowed)
    
    # Rule 3: Absolute ceiling - 50M RWF
    merged['predicted_revenue'] = merged['predicted_revenue'].clip(upper=50_000_000)
    
    # Rule 4: New customers - max 1.5x
    if 'transaction_count' in merged.columns and 'total_spent' in merged.columns:
        new_customers = merged['transaction_count'] < 5
        new_customer_max = merged.loc[new_customers, 'total_spent'] * 1.5
        merged.loc[new_customers, 'predicted_revenue'] = np.minimum(
            merged.loc[new_customers, 'predicted_revenue'],
            new_customer_max
        )
    
    # Rule 5: Inactive customers - reduce prediction
    if 'recency_days' in merged.columns:
        inactive = merged['recency_days'] > 30
        inactivity_factor = np.maximum(0.1, 1 - (merged.loc[inactive, 'recency_days'] / 180))
        merged.loc[inactive, 'predicted_revenue'] = merged.loc[inactive, 'predicted_revenue'] * inactivity_factor
    
    # Log adjustments
    num_adjusted = (merged['predicted_revenue'] != original_predictions).sum()
    if num_adjusted > 0:
        print(f"   ⚠️  Adjusted {num_adjusted} unrealistic predictions")
        max_before = original_predictions.max()
        max_after = merged['predicted_revenue'].max()
        print(f"   Max prediction: {max_before:,.0f} → {max_after:,.0f} RWF")
    
    return merged[predictions_df.columns]

'''

# Find where to insert this function (after imports, before routes)
insert_position = api_content.find('@app.get')
if insert_position == -1:
    insert_position = api_content.find('app = FastAPI')
    if insert_position != -1:
        # Find end of that line
        insert_position = api_content.find('\n', insert_position) + 1

if insert_position == -1:
    print("✗ Could not find insertion point in API file")
    sys.exit(1)

# Insert the function
api_content_new = (
    api_content[:insert_position] + 
    '\n' + constraint_function + '\n' +
    api_content[insert_position:]
)

print("✓ Constraint function added")

# Now modify the revenue forecast endpoint to use constraints
print("\nModifying revenue forecast endpoint...")

# Find the revenue forecast endpoint
revenue_endpoint_start = api_content_new.find('@app.get("/api/ml/revenue-forecast"')
if revenue_endpoint_start == -1:
    revenue_endpoint_start = api_content_new.find('def get_revenue_forecast')

if revenue_endpoint_start == -1:
    print("✗ Could not find revenue forecast endpoint")
    sys.exit(1)

# Find where predictions are returned (look for the return statement in that function)
# We need to add the constraint call before the return

# Find the function body
func_start = api_content_new.find('def get_revenue_forecast', revenue_endpoint_start)
func_body_start = api_content_new.find(':', func_start) + 1

# Find the next function or end
next_func = api_content_new.find('\n@app.', func_body_start)
if next_func == -1:
    next_func = len(api_content_new)

func_body = api_content_new[func_body_start:next_func]

# Find where predictions are made
if 'ml.predict_revenue' in func_body:
    # Find the line after predict_revenue
    predict_line = func_body.find('ml.predict_revenue')
    predict_line_end = func_body.find('\n', predict_line)
    
    # Add constraint call right after
    constraint_call = '\n        \n        # Apply realistic constraints\n        predictions = apply_realistic_constraints(predictions, customer_metrics)\n'
    
    func_body_new = func_body[:predict_line_end] + constraint_call + func_body[predict_line_end:]
    
    api_content_new = (
        api_content_new[:func_body_start] + 
        func_body_new + 
        api_content_new[next_func:]
    )
    
    print("✓ Modified revenue forecast endpoint")
else:
    print("⚠️  Could not automatically modify endpoint")
    print("   Will save constraint function, but you'll need to manually call it")

# Save the modified API
print("\nSaving modified API...")

# Backup original
try:
    with open('jalikoi_analytics_api_ml.py.backup_before_constraints', 'w', encoding='utf-8') as f:
        with open('jalikoi_analytics_api_ml.py', 'r', encoding='utf-8') as orig:
            f.write(orig.read())
    print("✓ Backup created")
except Exception as e:
    print(f"⚠️  Could not create backup: {e}")

# Save modified version
try:
    with open('jalikoi_analytics_api_ml.py', 'w', encoding='utf-8') as f:
        f.write(api_content_new)
    print("✓ Modified API saved")
except Exception as e:
    print(f"✗ Error saving: {e}")
    sys.exit(1)

print("\n" + "="*80)
print("✅ REALISTIC CONSTRAINTS ADDED TO API!")
print("="*80)
print()
print("The API will now automatically cap predictions at:")
print("  • Max 2x historical spending")
print("  • Absolute ceiling: 50M RWF")
print("  • New customers: Max 1.5x")
print("  • Inactive customers: Reduced by inactivity")
print()
print("Next steps:")
print("  1. Restart API: python jalikoi_analytics_api_ml.py")
print("  2. Test in browser")
print("  3. Predictions should now be realistic!")
print()
print("Backup saved to: jalikoi_analytics_api_ml.py.backup_before_constraints")
print()
