#!/usr/bin/env python3
"""
Check if apply_realistic_constraints function exists and what it does
"""

print("="*80)
print("CHECKING apply_realistic_constraints FUNCTION")
print("="*80)
print()

# Read API file
with open('jalikoi_analytics_api_ml.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the function definition
import re
func_match = re.search(
    r'(def apply_realistic_constraints.*?)(?=\ndef |$)',
    content,
    re.DOTALL
)

if func_match:
    print("FOUND THE FUNCTION:")
    print("-"*80)
    print(func_match.group(1))
    print("-"*80)
    print()
    
    # Check if it handles churn_probability
    func_code = func_match.group(1)
    if 'churn' in func_code.lower():
        print("⚠️ WARNING: Function mentions 'churn' - it may be affecting churn predictions!")
    else:
        print("✓ Function does NOT mention churn - good!")
    
    if 'predicted_revenue' in func_code:
        print("✓ Function handles 'predicted_revenue' - correct!")
    
else:
    print("❌ apply_realistic_constraints function NOT FOUND in API file!")
    print()
    print("This means the function was never added.")
    print("The constraints aren't being applied at all.")
    print()
    print("Run: python add_api_constraints.py")

print()
print("="*80)
print("ANALYSIS")
print("="*80)
print()

# Check where it's called
calls = re.findall(r'.*apply_realistic_constraints.*', content)
if calls:
    print(f"Function is called {len(calls)} time(s):")
    for i, call in enumerate(calls, 1):
        print(f"{i}. {call.strip()}")
    print()
    
    if len(calls) > 1:
        print("⚠️ Function is called MULTIPLE times!")
        print("   It should only be called in revenue endpoint.")
else:
    print("Function is never called (even though it may be defined)")

print()
