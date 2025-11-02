#!/usr/bin/env python3
"""
API Test Script
================
Quick test to verify the API is working correctly
Run this after starting the API server
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30  # seconds

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def test_endpoint(name, url, params=None):
    """Test an API endpoint"""
    print(f"\n🔍 Testing: {name}")
    print(f"   URL: {url}")
    if params:
        print(f"   Params: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)
        
        if response.status_code == 200:
            print(f"   ✅ Status: {response.status_code} OK")
            data = response.json()
            
            # Print key information based on endpoint
            if '/health' in url:
                print(f"   Status: {data.get('status')}")
                print(f"   Database: {'Available' if data.get('database_available') else 'Unavailable'}")
            
            elif '/insights' in url:
                if data.get('success'):
                    overview = data['data']['overview']
                    print(f"   Revenue: {overview['total_revenue']:,.0f} {overview['currency']}")
                    print(f"   Transactions: {overview['total_transactions']:,}")
                    print(f"   Success Rate: {overview['success_rate']:.1f}%")
                    print(f"   Customers: {data['data']['customers']['total_customers']:,}")
                    
                    if 'comparison' in data:
                        changes = data['comparison']['changes']
                        print(f"   Revenue Change: {changes.get('revenue_change', 'N/A')}%")
            
            elif '/visualizations' in url:
                if data.get('success'):
                    charts = data['charts']
                    print(f"   Charts Available: {len(charts)}")
                    for chart_name in charts.keys():
                        print(f"      - {chart_name}")
            
            return True
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection Error: API server not running?")
        print(f"   💡 Start the API with: python jalikoi_analytics_api.py")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout: Request took longer than {TIMEOUT} seconds")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print_header("JALIKOI ANALYTICS API - TEST SUITE")
    print(f"\nBase URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health Check
    print_header("TEST 1: Health Check")
    tests_total += 1
    if test_endpoint("Health Check", f"{BASE_URL}/api/health"):
        tests_passed += 1
    
    # Test 2: API Root
    print_header("TEST 2: API Root")
    tests_total += 1
    if test_endpoint("API Root", f"{BASE_URL}/"):
        tests_passed += 1
    
    # Test 3: Default Insights (Yesterday)
    print_header("TEST 3: Yesterday's Insights (Default)")
    tests_total += 1
    if test_endpoint("Default Insights", f"{BASE_URL}/api/insights"):
        tests_passed += 1
    
    # Test 4: Last Week
    print_header("TEST 4: Last Week Insights")
    tests_total += 1
    if test_endpoint("Last Week", f"{BASE_URL}/api/insights", {"period": "week"}):
        tests_passed += 1
    
    # Test 5: Custom Date Range
    print_header("TEST 5: Custom Date Range")
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    tests_total += 1
    if test_endpoint(
        "Custom Range", 
        f"{BASE_URL}/api/insights",
        {"start_date": yesterday, "end_date": yesterday}
    ):
        tests_passed += 1
    
    # Test 6: Comparison
    print_header("TEST 6: Insights with Comparison")
    tests_total += 1
    if test_endpoint(
        "With Comparison",
        f"{BASE_URL}/api/insights",
        {"period": "week", "compare": "true"}
    ):
        tests_passed += 1
    
    # Test 7: Visualizations
    print_header("TEST 7: Visualization Data")
    tests_total += 1
    if test_endpoint("Visualizations", f"{BASE_URL}/api/visualizations"):
        tests_passed += 1
    
    # Summary
    print_header("TEST SUMMARY")
    print(f"\n  Tests Passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("\n  ✅ ALL TESTS PASSED!")
        print("\n  Your API is working perfectly!")
        print("\n  Next steps:")
        print("    1. Import Postman collection: Jalikoi_Analytics_API.postman_collection.json")
        print("    2. Start building your dashboard")
        print("    3. Check API_DOCUMENTATION.md for more details")
    else:
        print(f"\n  ⚠️  {tests_total - tests_passed} test(s) failed")
        print("\n  Troubleshooting:")
        print("    1. Make sure API is running: python jalikoi_analytics_api.py")
        print("    2. Check database connection in db_config.py")
        print("    3. Verify you have data in the database")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
