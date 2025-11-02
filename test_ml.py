#!/usr/bin/env python3
"""
Test ML predictions directly to see the exact error
"""

import sys
from datetime import datetime, timedelta

print("="*80)
print("TESTING ML PREDICTIONS DIRECTLY")
print("="*80)
print()

try:
    from jalikoi_analytics_db import JalikoiAnalyticsEngine
    from ml_engine import MLEngine
    
    engine = JalikoiAnalyticsEngine()
    ml_engine = MLEngine(model_dir="ml_models")
    
    # Fetch data
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    df = engine.fetch_data_from_db(str(start_date), str(end_date))
    
    # Preprocess
    df = engine.preprocess_data(df)
    customer_metrics = engine.calculate_customer_metrics(df)
    
    print(f"Data loaded: {len(customer_metrics)} customers")
    print(f"Columns: {list(customer_metrics.columns)[:10]}...")
    print()
    
    # Test churn prediction
    print("Testing churn prediction...")
    try:
        predictions = ml_engine.predict_churn(customer_metrics)
        print("✓ CHURN WORKS!")
    except Exception as e:
        print(f"✗ CHURN FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test revenue prediction
    print("Testing revenue prediction...")
    try:
        predictions = ml_engine.predict_revenue(customer_metrics)
        print("✓ REVENUE WORKS!")
    except Exception as e:
        print(f"✗ REVENUE FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test segmentation
    print("Testing segmentation...")
    try:
        predictions = ml_engine.predict_segments(customer_metrics)
        print("✓ SEGMENTATION WORKS!")
    except Exception as e:
        print(f"✗ SEGMENTATION FAILED: {e}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"SETUP ERROR: {e}")
    import traceback
    traceback.print_exc()
