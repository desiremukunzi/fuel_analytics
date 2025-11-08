#!/usr/bin/env python3
"""
Show exactly what to change in jalikoi_analytics_api_ml.py
"""

print("="*80)
print("MANUAL FIX INSTRUCTIONS FOR CHURN vs REVENUE")
print("="*80)
print()

print("PROBLEM:")
print("-"*80)
print("The apply_realistic_constraints() function is being applied to BOTH")
print("churn and revenue predictions, but it should ONLY apply to revenue.")
print()
print("Churn predictions are probabilities (0-100%) and don't need constraints.")
print("Revenue predictions need constraints (max 2x historical, etc.)")
print()

print("\nSOLUTION:")
print("-"*80)
print()

print("1. Open: jalikoi_analytics_api_ml.py")
print()

print("2. Find the CHURN endpoint (search for: @app.get(\"/api/ml/churn-predictions\")")
print()
print("   It looks like this:")
print()
print("   " + "-"*70)
print("""
   @app.get("/api/ml/churn-predictions")
   async def get_churn_predictions(...):
       ...
       predictions = ml.predict_churn(customer_metrics)
       predictions = apply_realistic_constraints(predictions, customer_metrics)  ← REMOVE THIS
       return predictions.to_dict('records')
""")
print("   " + "-"*70)
print()

print("   DELETE or COMMENT OUT the line:")
print("   predictions = apply_realistic_constraints(predictions, customer_metrics)")
print()

print("   So it becomes:")
print()
print("   " + "-"*70)
print("""
   @app.get("/api/ml/churn-predictions")
   async def get_churn_predictions(...):
       ...
       predictions = ml.predict_churn(customer_metrics)
       # predictions = apply_realistic_constraints(predictions, customer_metrics)  ← REMOVED
       return predictions.to_dict('records')
""")
print("   " + "-"*70)
print()

print("3. Find the REVENUE endpoint (search for: @app.get(\"/api/ml/revenue-forecast\")")
print()
print("   Make sure it HAS the constraint line:")
print()
print("   " + "-"*70)
print("""
   @app.get("/api/ml/revenue-forecast")
   async def get_revenue_forecast(...):
       ...
       predictions = ml.predict_revenue(customer_metrics)
       predictions = apply_realistic_constraints(predictions, customer_metrics)  ← KEEP THIS
       return predictions.to_dict('records')
""")
print("   " + "-"*70)
print()

print("4. If revenue endpoint DOESN'T have the constraint line, ADD it:")
print()
print("   " + "-"*70)
print("""
   @app.get("/api/ml/revenue-forecast")
   async def get_revenue_forecast(...):
       ...
       predictions = ml.predict_revenue(customer_metrics)
       predictions = apply_realistic_constraints(predictions, customer_metrics)  ← ADD THIS LINE
       return predictions.to_dict('records')
""")
print("   " + "-"*70)
print()

print("5. Save the file")
print()

print("6. Restart API:")
print("   python jalikoi_analytics_api_ml.py")
print()

print("7. Test in browser:")
print("   - Churn predictions: Should show accurate % (no constraints)")
print("   - Revenue predictions: Should be capped at realistic values")
print()

print("="*80)
print("QUICK SEARCH TIPS")
print("="*80)
print()
print("To find the lines quickly:")
print()
print("1. Press Ctrl+F in your editor")
print("2. Search for: \"predict_churn\"")
print("3. Find the line: predictions = ml.predict_churn(customer_metrics)")
print("4. Check if there's an apply_realistic_constraints line right after")
print("5. If yes, DELETE or COMMENT it out")
print()
print("6. Search for: \"predict_revenue\"")
print("7. Find the line: predictions = ml.predict_revenue(customer_metrics)")
print("8. Check if there's an apply_realistic_constraints line right after")
print("9. If no, ADD it")
print()

print("="*80)
print()

# Try to read the file and show what's actually there
import os
if os.path.exists('jalikoi_analytics_api_ml.py'):
    print("CURRENT STATE OF YOUR API FILE:")
    print("="*80)
    
    with open('jalikoi_analytics_api_ml.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find churn section
    import re
    churn_match = re.search(
        r'(@app\.get.*churn.*?\n.*?def.*?\n.*?(?:predictions.*?churn|churn.*?predictions).*?\n.*?\n)',
        content,
        re.DOTALL | re.IGNORECASE
    )
    
    if churn_match:
        print("\nCHURN ENDPOINT - Currently:")
        print("-"*80)
        snippet = churn_match.group(0)
        # Show next 10 lines
        start = churn_match.end()
        lines = content[start:].split('\n')[:10]
        print(snippet + '\n'.join(lines))
        print("-"*80)
        
        if 'apply_realistic_constraints' in snippet + '\n'.join(lines):
            print("⚠️  PROBLEM: Churn endpoint HAS constraints (should be removed)")
        else:
            print("✓ GOOD: Churn endpoint does NOT have constraints")
    
    # Find revenue section
    revenue_match = re.search(
        r'(@app\.get.*revenue.*?\n.*?def.*?\n.*?(?:predictions.*?revenue|revenue.*?predictions).*?\n.*?\n)',
        content,
        re.DOTALL | re.IGNORECASE
    )
    
    if revenue_match:
        print("\nREVENUE ENDPOINT - Currently:")
        print("-"*80)
        snippet = revenue_match.group(0)
        # Show next 10 lines
        start = revenue_match.end()
        lines = content[start:].split('\n')[:10]
        print(snippet + '\n'.join(lines))
        print("-"*80)
        
        if 'apply_realistic_constraints' in snippet + '\n'.join(lines):
            print("✓ GOOD: Revenue endpoint HAS constraints")
        else:
            print("⚠️  PROBLEM: Revenue endpoint does NOT have constraints (should be added)")
    
    print()
else:
    print("⚠️  Could not find jalikoi_analytics_api_ml.py in current directory")
    print("   Navigate to your project folder first:")
    print("   cd A:\\MD\\fuel")
    print()
