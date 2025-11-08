#!/usr/bin/env python3
"""
Direct fix for segment mapping
"""

import os
import sys

print("="*80)
print("SEGMENT MAPPING FIX")
print("="*80)
print()

# Check if ml_engine.py exists
if not os.path.exists('ml_engine.py'):
    print("❌ ERROR: ml_engine.py not found in current directory!")
    print()
    print("Please run this script from: A:\\MD\\fuel")
    print("Current directory:", os.getcwd())
    sys.exit(1)

print("✓ Found ml_engine.py")
print()

# Read the file
with open('ml_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the segment mapping
found_line = None
for i, line in enumerate(lines):
    if "segment_name'] = results['ml_segment'].map" in line:
        found_line = i
        break

if found_line is None:
    print("❌ Could not find segment mapping in ml_engine.py")
    print()
    print("Please search for: segment_name'] = results['ml_segment'].map")
    print("And manually update the mapping.")
    sys.exit(1)

print(f"✓ Found segment mapping at line {found_line + 1}")
print()
print("CURRENT MAPPING:")
print("-"*80)

# Show current mapping (next 10 lines)
for i in range(found_line, min(found_line + 11, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')

print()
print()
print("="*80)
print("What are the CURRENT labels for each cluster?")
print("="*80)
print()

# Try to extract current mapping
import re
current_mapping = {}
for i in range(found_line, min(found_line + 15, len(lines))):
    match = re.search(r"(\d+):\s*'([^']+)'", lines[i])
    if match:
        cluster_id = int(match.group(1))
        label = match.group(2)
        current_mapping[cluster_id] = label
        print(f"Cluster {cluster_id} → '{label}'")

print()
print("="*80)
print("CORRECT MAPPING SHOULD BE:")
print("="*80)
print()

correct_mapping = {
    0: 'Lost',
    1: 'Dormant',
    2: 'Premium VIPs',
    3: 'At Risk',
    4: 'Occasional Users',
    5: 'Loyal Regulars',  # ← FIX: Currently shows old customers as "New"
    6: 'Growth Potential',
    7: 'New Customers'
}

for cluster_id, label in correct_mapping.items():
    current = current_mapping.get(cluster_id, "???")
    status = "✓" if current == label else "✗ WRONG"
    print(f"Cluster {cluster_id} → '{label}' {status}")
    if current != label:
        print(f"           (currently: '{current}')")

print()
print("="*80)
print("CREATING FIXED VERSION...")
print("="*80)
print()

# Create the new mapping text
new_mapping_lines = """        results['segment_name'] = results['ml_segment'].map({
            0: 'Lost',
            1: 'Dormant',
            2: 'Premium VIPs',
            3: 'At Risk',
            4: 'Occasional Users',
            5: 'Loyal Regulars',
            6: 'Growth Potential',
            7: 'New Customers'
        })
"""

# Find start and end of the mapping block
start_line = found_line
end_line = found_line
brace_count = 0
started = False

for i in range(found_line, min(found_line + 20, len(lines))):
    if '{' in lines[i]:
        brace_count += lines[i].count('{')
        started = True
    if '}' in lines[i]:
        brace_count -= lines[i].count('}')
    if started and brace_count == 0:
        end_line = i
        break

print(f"Mapping spans lines {start_line + 1} to {end_line + 1}")

# Create new content
new_lines = lines[:start_line] + [new_mapping_lines] + lines[end_line + 1:]

# Backup
backup_file = 'ml_engine.py.backup_' + str(int(os.path.getmtime('ml_engine.py')))
with open(backup_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"✓ Backup created: {backup_file}")

# Write new version
with open('ml_engine.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✓ Updated ml_engine.py with correct mapping")
print()
print("="*80)
print("✅ FIX COMPLETE!")
print("="*80)
print()
print("Next steps:")
print("  1. Restart API: python jalikoi_analytics_api_ml.py")
print("  2. Refresh browser: Ctrl+Shift+R")
print("  3. Check 'Loyal Regulars' segment - should now show high-value customers")
print()
print("If something goes wrong, restore from backup:")
print(f"  copy {backup_file} ml_engine.py")
print()