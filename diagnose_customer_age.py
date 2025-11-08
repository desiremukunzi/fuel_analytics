#!/usr/bin/env python3
"""
Fix customer_age_days to use actual registration date from motorcyclists table
Currently it uses first transaction date, which doesn't identify truly new customers
"""

print("="*80)
print("FIXING CUSTOMER AGE CALCULATION")
print("="*80)
print()

print("The problem:")
print("-"*80)
print("Current: customer_age_days = days since FIRST TRANSACTION")
print("Correct: customer_age_days = days since REGISTRATION (motorcyclists.created_at)")
print()
print("This is why customers from 2022 appear as 'New Customers'")
print("Their first transaction in your data might be recent, but they registered in 2022")
print()

print("="*80)
print("SOLUTION: Update customer metrics calculation")
print("="*80)
print()

# Find where customer_age_days is calculated
import os
import glob

# Look for files that calculate customer metrics
files_to_check = [
    'jalikoi_analytics_db.py',
    'jalikoi_analytics.py', 
    'analytics_engine.py',
    'jalikoi_analytics_api_ml.py'
]

found_file = None
for filename in files_to_check:
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'customer_age_days' in content and 'def calc' in content:
                found_file = filename
                break

if found_file:
    print(f"✓ Found customer metrics calculation in: {found_file}")
    print()
    
    # Read the file
    with open(found_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the calculation
    for i, line in enumerate(lines):
        if 'customer_age_days' in line:
            print(f"Line {i+1}: {line.strip()}")
    
    print()
    print("MANUAL FIX REQUIRED:")
    print("-"*80)
else:
    print("⚠️  Could not find where customer_age_days is calculated")
    print()
    print("SEARCH FOR:")
    print("  customer_age_days")
    print("  or")
    print("  'first_transaction'")

print()
print("You need to modify the customer metrics calculation:")
print()
print("CURRENT (WRONG):")
print("-"*80)
print("""
# Calculate customer age from first transaction
customer_age_days = (today - first_transaction_date).days
""")
print()
print("CORRECT:")
print("-"*80)
print("""
# Get actual registration date from motorcyclists table
motorcyclists_query = '''
    SELECT id, created_at 
    FROM motorcyclists 
    WHERE id IN (SELECT DISTINCT motorcyclist_id FROM DailyTransactionPayments)
'''
motorcyclists_df = db.fetch_data(motorcyclists_query)

# Merge with customer metrics
customer_metrics = customer_metrics.merge(
    motorcyclists_df.rename(columns={'id': 'motorcyclist_id', 'created_at': 'registration_date'}),
    on='motorcyclist_id',
    how='left'
)

# Calculate customer age from registration date
from datetime import datetime
today = datetime.now()
customer_metrics['customer_age_days'] = customer_metrics['registration_date'].apply(
    lambda x: (today - pd.to_datetime(x)).days if pd.notna(x) else 0
)
""")

print()
print("="*80)
print("ALTERNATIVE: Rule-based 'New Customers' Definition")
print("="*80)
print()
print("Instead of fixing the age calculation, we can:")
print("1. Rename cluster 7 to something else (e.g., 'Low Activity')")
print("2. Create a separate 'New Customers' category based on registration date")
print("3. Add it as a 9th segment (not from ML)")
print()
print("This is easier and might be more accurate!")
print()
print("Would you like me to create this alternative solution?")
print()