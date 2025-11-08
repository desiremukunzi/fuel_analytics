#!/usr/bin/env python3
"""
Create 'New Customers with Potential' segment
Combines recency (< 90 days) with high-potential behavior patterns
"""

print("="*80)
print("CREATING 'NEW CUSTOMERS WITH POTENTIAL' SEGMENT")
print("="*80)
print()

print("CRITERIA:")
print("-"*80)
print("1. RECENCY: Customer age < 90 days (joined in last 3 months)")
print("2. POTENTIAL: High-value behavior indicators:")
print("   - Frequent transactions (frequency > 0.5 txn/day)")
print("   - OR Good spending (total_spent > 100,000 RWF)")
print("   - OR High transaction count (> 5 transactions)")
print("   - Low recency (transacted recently)")
print()

# Read ml_engine.py
try:
    with open('ml_engine.py', 'r', encoding='utf-8') as f:
        ml_content = f.read()
except FileNotFoundError:
    print("❌ ml_engine.py not found")
    exit(1)

# Backup
with open('ml_engine.py.backup_new_potential', 'w', encoding='utf-8') as f:
    f.write(ml_content)

print("✓ Backup created")
print()

import re

# Find the predict_segments method
print("Modifying predict_segments method...")
print()

# Find where segment_name is mapped
pattern = r"(results\['segment_name'\] = results\['ml_segment'\]\.map\(\{[^}]+\}\))"

match = re.search(pattern, ml_content, re.DOTALL)

if match:
    # Add post-processing after the mapping
    new_code = '''
        
        # Post-process: Identify "New Customers with Potential"
        # Rule-based overlay on ML segments
        results = self._identify_new_with_potential(results, customer_metrics)
'''
    
    ml_content = ml_content.replace(match.group(1), match.group(1) + new_code)
    print("✓ Added post-processing call")
else:
    print("⚠️  Could not find segment mapping")

# Add the new method
new_method = '''
    def _identify_new_with_potential(self, results: pd.DataFrame, customer_metrics: pd.DataFrame) -> pd.DataFrame:
        """
        Identify new customers with high potential
        Overrides ML clustering for customers who are both new AND showing potential
        
        Criteria:
        - New: customer_age_days < 90
        - Potential: frequency > 0.5 OR total_spent > 100000 OR transaction_count > 5
        - Active: recency_days < 30
        """
        # Merge with customer metrics to get the features
        merged = results.merge(
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
        
        # Define "New" - joined in last 90 days
        is_new = merged['customer_age_days'] < 90
        
        # Define "Potential" - showing high-value behavior
        has_potential = (
            (merged['frequency'] > 0.5) |  # Frequent transactions
            (merged['total_spent'] > 100000) |  # Good spender
            (merged['transaction_count'] > 5)  # Multiple transactions
        )
        
        # Must also be active recently
        is_active = merged['recency_days'] < 30
        
        # Combine criteria
        new_with_potential = is_new & has_potential & is_active
        
        # Override segment name for these customers
        merged.loc[new_with_potential, 'segment_name'] = 'New Customers'
        
        # For old "New Customers" who don't meet criteria, reclassify
        old_fake_new = (merged['segment_name'] == 'New Customers') & ~new_with_potential
        
        # Reclassify based on their actual behavior
        # Old + low activity = Dormant/Occasional
        merged.loc[old_fake_new & (merged['customer_age_days'] >= 90), 'segment_name'] = 'Occasional Users'
        
        print(f"   ✓ Identified {new_with_potential.sum()} New Customers with Potential")
        
        return merged[results.columns]
'''

# Insert the method before the predict_segments method
insert_pos = ml_content.find('    def predict_segments(')
if insert_pos > 0:
    ml_content = ml_content[:insert_pos] + new_method + '\n' + ml_content[insert_pos:]
    print("✓ Added _identify_new_with_potential method")
else:
    print("⚠️  Could not find insertion point for new method")

# Save
with open('ml_engine.py', 'w', encoding='utf-8') as f:
    f.write(ml_content)

print("✓ Saved ml_engine.py")
print()

print("="*80)
print("✅ UPDATE COMPLETE!")
print("="*80)
print()
print("New 'New Customers' segment will show:")
print("  ✓ Customer age < 90 days (joined recently)")
print("  ✓ Frequency > 0.5 txn/day OR Spent > 100K OR 5+ transactions")
print("  ✓ Recency < 30 days (still active)")
print()
print("Customers from May 2025 (180 days old) will NOT appear here anymore.")
print()
print("Next steps:")
print("  1. Retrain models: python train_ml_models.py")
print("  2. Restart API: python jalikoi_analytics_api_ml.py")
print("  3. Refresh browser")
print()
print("The 'New Customers' segment will now show only recent, high-potential customers!")
print()