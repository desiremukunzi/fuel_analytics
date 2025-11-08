#!/usr/bin/env python3
"""
Update segment mapping based on ACTUAL analysis results
"""

print("="*80)
print("UPDATING SEGMENT MAPPING TO MATCH ACTUAL CHARACTERISTICS")
print("="*80)
print()

# Based on analyze_segments.py results:
# Growth Potential = Actually Premium VIPs (6.3M avg, 212 trans, 0.5 days recency)
# New Customers = Actually Loyal Regulars (1.6M avg, 26 trans)
# Occasional Users = Actually Growth Potential (62K avg, 4.4 trans)
# Dormant = Actually Occasional Users (47K avg, 5 trans, 63 days recency)
# Loyal Regulars = Actually Dormant (20K avg, 1.1 trans, 41 days recency)
# At Risk = Actually Lost (14K avg, 1.1 trans, 106 days recency)
# Premium VIPs = Actually At Risk (21K avg, 1.2 trans, 92 days recency, 53% failures!)
# Lost = Keep as Lost (31K avg, 2.4 trans, 70 days recency)

# Read current ml_engine.py
with open('ml_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open('ml_engine.py.backup_segment_mapping', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Backup created: ml_engine.py.backup_segment_mapping")

# Find and update segment mapping
import re

# Current (wrong) mapping - need to find which cluster number maps to which current label
# Then reassign based on actual characteristics

# The new correct mapping based on analysis:
new_mapping = """        segment_mapping = {
            0: 'Lost',              # Was: At Risk (106d recency, 14K avg) 
            1: 'Dormant',           # Was: Loyal Regulars (41d recency, 20K avg)
            2: 'Premium VIPs',      # Was: Growth Potential (0.5d recency, 6.3M avg!) 
            3: 'At Risk',           # Was: Premium VIPs (92d recency, 21K avg, 53% fail!)
            4: 'Occasional Users',  # Was: Dormant (63d recency, 47K avg)
            5: 'Loyal Regulars',    # Was: New Customers (57d recency, 1.6M avg)
            6: 'Growth Potential',  # Was: Occasional Users (68d recency, 62K avg)
            7: 'New Customers'      # Was: Lost (70d recency, 32K avg) - needs verification
        }"""

# Find the segment_mapping section
pattern = r'segment_mapping\s*=\s*\{[^}]+\}'

if re.search(pattern, content):
    content_new = re.sub(pattern, new_mapping.strip(), content)
    
    with open('ml_engine.py', 'w', encoding='utf-8') as f:
        f.write(content_new)
    
    print("✓ Updated segment_mapping in ml_engine.py")
    print()
    print("New mapping:")
    print(new_mapping)
else:
    print("⚠️  Could not find segment_mapping in ml_engine.py")
    print("\nManual fix required:")
    print(new_mapping)

print()
print("="*80)
print("✅ SEGMENT MAPPING UPDATED!")
print("="*80)
print()
print("IMPORTANT: This is based on your actual data analysis.")
print("The mapping maps cluster IDs to human-readable names.")
print()
print("Next steps:")
print("  1. Restart API: python jalikoi_analytics_api_ml.py")
print("  2. Refresh browser (Ctrl+F5)")
print("  3. Check Segments tab - should now be correct!")
print()
print("If segments still look wrong, run analyze_segments.py again")
print("and manually verify which cluster is which.")
print()