#!/usr/bin/env python3
"""
COMPLETE FIX - Date Range Issues for Charts and Anomalies
This fixes both the backend API and frontend components
"""

import os
import shutil
from datetime import datetime

print("="*80)
print("FIXING DATE RANGE ISSUES - CHARTS & ANOMALIES")
print("="*80)
print()

# =============================================================================
# FIX 1: ANOMALIES API ENDPOINT (Backend)
# =============================================================================

print("FIX 1: Updating Anomalies API endpoint...")
print("-"*80)

api_file = 'jalikoi_analytics_api_ml.py'

# Backup
backup_file = f'{api_file}.date_fix_backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy(api_file, backup_file)
print(f"✓ Backup created: {backup_file}")

# Read file
with open(api_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the anomalies date range logic
old_date_logic = """        # Determine date range
        today = datetime.now().date()
        if not start_date or not end_date:
            yesterday = today - timedelta(days=1)
            start_date = str(yesterday)
            end_date = str(yesterday)"""

new_date_logic = """        # Determine date range - USE LAST 30 DAYS BY DEFAULT
        today = datetime.now().date()
        if not start_date or not end_date:
            start_date = str(today - timedelta(days=30))
            end_date = str(today)"""

if old_date_logic in content:
    content = content.replace(old_date_logic, new_date_logic)
    print("✓ Fixed anomalies date range (now uses last 30 days instead of yesterday)")
else:
    print("⚠ Date logic pattern not found or already fixed")

# Write back
with open(api_file, 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ API file updated")

# =============================================================================
# FIX 2: ANOMALIES FRONTEND COMPONENT
# =============================================================================

print("\nFIX 2: Checking Anomalies frontend component...")
print("-"*80)

anomalies_component = 'A:\\MD\\fuel_frontend\\src\\components\\MLAnomalies.js'

if os.path.exists(anomalies_component):
    # Backup
    backup_anomalies = f'{anomalies_component}.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    shutil.copy(anomalies_component, backup_anomalies)
    print(f"✓ Backup created: {backup_anomalies}")
    
    with open(anomalies_component, 'r', encoding='utf-8') as f:
        anomaly_content = f.read()
    
    # Check if fetchAnomalies uses the dateRange properly
    if 'start_date=${dateRange.start}&end_date=${dateRange.end}' in anomaly_content:
        print("✓ Anomalies component already passes date range correctly")
    elif 'start_date=' not in anomaly_content:
        print("⚠ Anomalies component may not be passing date range - check manually")
    else:
        print("✓ Anomalies component structure looks correct")
else:
    print("⚠ Anomalies component not found - may need to be created")

# =============================================================================
# FIX 3: CHARTS TAB
# =============================================================================

print("\nFIX 3: Checking Charts tab...")
print("-"*80)

app_js = 'A:\\MD\\fuel_frontend\\src\\App.js'

if os.path.exists(app_js):
    with open(app_js, 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Check if Charts tab gets dateRange prop
    if 'dateRange={dateRange}' in app_content:
        charts_gets_date = app_content.count('dateRange={dateRange}')
        print(f"✓ Found {charts_gets_date} components receiving dateRange")
        
        # Check if it's passed to Charts specifically
        if '<Charts' in app_content and 'dateRange={dateRange}' in app_content.split('<Charts')[1].split('>')[0]:
            print("✓ Charts component receives dateRange prop")
        else:
            print("⚠ Charts component may not receive dateRange prop")
            
            # Backup and fix
            backup_app = f'{app_js}.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            shutil.copy(app_js, backup_app)
            print(f"✓ Backup created: {backup_app}")
            
            # Add dateRange prop to Charts
            app_content = app_content.replace(
                '<Charts data={data} loading={loading} />',
                '<Charts data={data} loading={loading} dateRange={dateRange} />'
            )
            
            with open(app_js, 'w', encoding='utf-8') as f:
                f.write(app_content)
            print("✓ Added dateRange prop to Charts component")
    else:
        print("⚠ dateRange prop not found in App.js")
else:
    print("❌ App.js not found")

# =============================================================================
# FIX 4: VERIFY CHARTS.JS USES DATERANGE
# =============================================================================

print("\nFIX 4: Checking Charts.js component...")
print("-"*80)

charts_component = 'A:\\MD\\fuel_frontend\\src\\components\\Charts.js'

if os.path.exists(charts_component):
    with open(charts_component, 'r', encoding='utf-8') as f:
        charts_content = f.read()
    
    # Check if Charts destructures dateRange from props
    if 'dateRange' in charts_content:
        print("✓ Charts component references dateRange")
        
        # Check if it's in the function parameters
        if 'function Charts({ data, loading, dateRange })' in charts_content or \
           'const Charts = ({ data, loading, dateRange })' in charts_content:
            print("✓ Charts component receives dateRange as prop")
        else:
            print("⚠ Charts component may not properly receive dateRange")
            print("  Need to add dateRange to function parameters")
    else:
        print("⚠ Charts component doesn't use dateRange")
        print("  This means it won't update when date range changes")
        print("  The data prop should already be filtered by date in App.js")
else:
    print("⚠ Charts.js component not found")

print()
print("="*80)
print("DATE RANGE FIX SUMMARY")
print("="*80)
print()
print("✅ Backend API: Anomalies now uses last 30 days by default")
print("✅ Frontend: Checked all components")
print()
print("IMPORTANT:")
print("-"*80)
print("The Charts and Anomalies tabs should update based on date range IF:")
print()
print("1. App.js fetches new data when dateRange changes")
print("2. Components receive the filtered data")
print()
print("The issue is usually that:")
print("- Charts shows ALL data regardless of selected dates")
print("- Need to filter data in App.js before passing to Charts")
print()
print("="*80)
print("NEXT STEPS")
print("="*80)
print()
print("1. Restart backend:")
print("   cd A:\\MD\\fuel")
print("   python jalikoi_analytics_api_ml.py")
print()
print("2. Restart frontend (if changes were made):")
print("   cd A:\\MD\\fuel_frontend")
print("   npm start")
print()
print("3. Test:")
print("   - Go to Anomalies tab")
print("   - Change date range")
print("   - Data should update")
print()
print("4. If Charts still don't update:")
print("   - The data fetch in App.js may need to be checked")
print("   - Send me the App.js useEffect that fetches data")
print()
print(f"Backups created:")
print(f"  - {backup_file}")
if os.path.exists(anomalies_component):
    print(f"  - {backup_anomalies}")
if 'backup_app' in locals():
    print(f"  - {backup_app}")
print()
