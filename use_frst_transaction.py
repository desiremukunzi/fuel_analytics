#!/usr/bin/env python3
"""
Update segment-customers endpoint to use ONLY DailyTransactionPayments table
- Use payer_phone instead of motari_phone
- Use MIN(created_at) as first transaction date
- No need for motorcyclists table at all
"""

print("="*80)
print("SIMPLIFYING CUSTOMER LIST - USE ONLY DailyTransactionPayments")
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
with open('jalikoi_analytics_api_ml.py.backup_payer_phone', 'w', encoding='utf-8') as f:
    f.write(api_content)

print("✓ Backup created")
print()

import re

# Find the segment-customers endpoint section that fetches customer details
print("Searching for customer data fetch section...")

# Pattern to find the entire customer data fetching block
pattern = r"(# Fetch customer details from motorcyclists table.*?)(\n        return \{)"

match = re.search(pattern, api_content, re.DOTALL)

if match:
    print("✓ Found customer data fetch section")
    print()
    
    # New implementation using only DailyTransactionPayments
    new_implementation = '''# Fetch customer details from DailyTransactionPayments table only
        customer_query = f"""
            SELECT 
                motorcyclist_id,
                payer_phone,
                MIN(created_at) as first_transaction_date
            FROM DailyTransactionPayments
            WHERE motorcyclist_id IN ({customer_ids_str})
            GROUP BY motorcyclist_id, payer_phone
            ORDER BY first_transaction_date DESC
        """
        
        with JalikoiDatabaseConnector(DB_CONFIG) as db:
            customers_df = db.fetch_data(customer_query)
        
        if customers_df is None or customers_df.empty:
            # If no data, return basic info from predictions
            customers_list = []
            for _, row in segment_customers.head(limit).iterrows():
                customers_list.append({
                    'motorcyclist_id': int(row['motorcyclist_id']),
                    'payer_phone': 'N/A',
                    'created_at': 'N/A',
                    'ml_segment': int(row['ml_segment'])
                })
        else:
            # Merge with segment data
            merged = segment_customers.merge(
                customers_df,
                on='motorcyclist_id',
                how='left'
            )
            
            customers_list = []
            for _, row in merged.head(limit).iterrows():
                customers_list.append({
                    'motorcyclist_id': int(row['motorcyclist_id']),
                    'payer_phone': str(row['payer_phone']) if pd.notna(row['payer_phone']) else 'N/A',
                    'created_at': str(row['first_transaction_date']) if pd.notna(row['first_transaction_date']) else 'N/A',
                    'ml_segment': int(row['ml_segment'])
                })
        '''
    
    # Replace the old implementation
    old_section = match.group(1)
    api_content = api_content.replace(old_section, new_implementation)
    
    print("✓ Replaced customer data fetch with DailyTransactionPayments query")
    print()
    
else:
    print("⚠️  Could not find exact pattern")
    print()
    print("MANUAL FIX REQUIRED:")
    print("="*80)
    print()
    print("In jalikoi_analytics_api_ml.py, in the @app.get('/api/ml/segment-customers/{segment_name}') endpoint:")
    print()
    print("FIND the section that fetches customer details (around line 1100-1150)")
    print()
    print("REPLACE the entire customer fetching block with:")
    print("-"*80)
    print('''
        # Fetch customer details from DailyTransactionPayments table only
        customer_query = f"""
            SELECT 
                motorcyclist_id,
                payer_phone,
                MIN(created_at) as first_transaction_date
            FROM DailyTransactionPayments
            WHERE motorcyclist_id IN ({customer_ids_str})
            GROUP BY motorcyclist_id, payer_phone
            ORDER BY first_transaction_date DESC
        """
        
        with JalikoiDatabaseConnector(DB_CONFIG) as db:
            customers_df = db.fetch_data(customer_query)
        
        if customers_df is None or customers_df.empty:
            customers_list = []
            for _, row in segment_customers.head(limit).iterrows():
                customers_list.append({
                    'motorcyclist_id': int(row['motorcyclist_id']),
                    'payer_phone': 'N/A',
                    'created_at': 'N/A',
                    'ml_segment': int(row['ml_segment'])
                })
        else:
            merged = segment_customers.merge(
                customers_df,
                on='motorcyclist_id',
                how='left'
            )
            
            customers_list = []
            for _, row in merged.head(limit).iterrows():
                customers_list.append({
                    'motorcyclist_id': int(row['motorcyclist_id']),
                    'payer_phone': str(row['payer_phone']) if pd.notna(row['payer_phone']) else 'N/A',
                    'created_at': str(row['first_transaction_date']) if pd.notna(row['first_transaction_date']) else 'N/A',
                    'ml_segment': int(row['ml_segment'])
                })
    ''')
    print("-"*80)
    print()

# Save
with open('jalikoi_analytics_api_ml.py', 'w', encoding='utf-8') as f:
    f.write(api_content)

print("✓ Saved changes")
print()
print("="*80)
print("✅ UPDATE COMPLETE!")
print("="*80)
print()
print("Changes made:")
print("  ✓ Removed dependency on motorcyclists table")
print("  ✓ Using payer_phone from DailyTransactionPayments")
print("  ✓ Using MIN(created_at) as first transaction date")
print("  ✓ Simpler, faster query")
print()
print("Next steps:")
print("  1. Restart API: python jalikoi_analytics_api_ml.py")
print("  2. Refresh browser")
print("  3. Click on any segment to see customer list")
print("  4. Should now show payer_phone and first transaction date")
print()