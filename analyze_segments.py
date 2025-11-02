#!/usr/bin/env python3
"""
Analyze actual segment characteristics from your data
Shows the real criteria for each segment based on your customer base
"""

from datetime import datetime, timedelta
import pandas as pd
import sys

print("="*80)
print("ACTUAL SEGMENT CHARACTERISTICS ANALYZER")
print("="*80)
print()

try:
    # Import required modules
    from train_ml_models import calculate_customer_metrics
    from ml_engine import MLEngine
    from jalikoi_analytics_db import JalikoiAnalyticsVisualized
    from db_config import DB_CONFIG
    
    print("Step 1: Loading data from database...")
    print("-"*80)
    
    # Load data
    analytics = JalikoiAnalyticsVisualized(DB_CONFIG, use_database=True)
    df = analytics.df
    
    if df is None or df.empty:
        print("❌ No data found in database")
        sys.exit(1)
    
    print(f"✓ Loaded {len(df)} transactions")
    
    # Get customer metrics
    customer_metrics = analytics.customer_metrics
    print(f"✓ Calculated metrics for {len(customer_metrics)} customers")
    
    print("\nStep 2: Loading ML model and predicting segments...")
    print("-"*80)
    
    # Load ML engine and predict segments
    ml_engine = MLEngine(model_dir="ml_models")
    
    if ml_engine.segmentation_model is None:
        print("❌ Segmentation model not trained!")
        print("   Run: python train_ml_models.py")
        sys.exit(1)
    
    predictions = ml_engine.predict_segments(customer_metrics)
    print(f"✓ Segmented {len(predictions)} customers")
    
    print("\nStep 3: Analyzing segment characteristics...")
    print("-"*80)
    
    # Merge
    data = customer_metrics.merge(predictions, on='motorcyclist_id')
    
    print()
    print("="*80)
    print("SEGMENT ANALYSIS RESULTS")
    print("="*80)
    
    # Analyze each segment
    for segment_name in sorted(predictions['segment_name'].unique()):
        segment_data = data[data['segment_name'] == segment_name]
        
        if len(segment_data) == 0:
            continue
        
        print(f"\n{'='*80}")
        print(f"📊 {segment_name}")
        print(f"{'='*80}")
        print(f"Customer Count: {len(segment_data)} ({len(segment_data)/len(data)*100:.1f}% of total)")
        
        print(f"\n💰 SPENDING METRICS:")
        print(f"   Total Revenue: {segment_data['total_spent'].sum():,.0f} RWF")
        print(f"   Avg per Customer: {segment_data['total_spent'].mean():,.0f} RWF")
        print(f"   Avg per Transaction: {segment_data['avg_transaction'].mean():,.0f} RWF")
        print(f"   Spending Range: {segment_data['total_spent'].min():,.0f} - {segment_data['total_spent'].max():,.0f} RWF")
        
        print(f"\n📈 ACTIVITY METRICS:")
        print(f"   Avg Transactions: {segment_data['transaction_count'].mean():.1f}")
        print(f"   Avg Frequency: {segment_data['frequency'].mean():.3f} trans/day ({segment_data['frequency'].mean()*7:.1f}/week)")
        print(f"   Avg Recency: {segment_data['recency_days'].mean():.1f} days")
        print(f"   Avg Customer Age: {segment_data['customer_age_days'].mean():.0f} days")
        
        print(f"\n⚙️ BEHAVIOR METRICS:")
        print(f"   App Usage Rate: {segment_data['app_usage_rate'].mean():.1%}")
        print(f"   Failure Rate: {segment_data['failure_rate'].mean():.1%}")
        print(f"   Station Diversity: {segment_data['station_diversity'].mean():.1f} stations")
        print(f"   Total Liters: {segment_data['total_liters'].mean():.1f}L avg")
        
        print(f"\n📊 RANGES:")
        print(f"   Recency: {segment_data['recency_days'].min():.0f} - {segment_data['recency_days'].max():.0f} days")
        print(f"   Frequency: {segment_data['frequency'].min():.3f} - {segment_data['frequency'].max():.3f} trans/day")
        print(f"   Transactions: {segment_data['transaction_count'].min():.0f} - {segment_data['transaction_count'].max():.0f}")
        
        # Percentiles
        print(f"\n📍 KEY PERCENTILES:")
        print(f"   Spending (25th/50th/75th): {segment_data['total_spent'].quantile(0.25):,.0f} / {segment_data['total_spent'].quantile(0.5):,.0f} / {segment_data['total_spent'].quantile(0.75):,.0f} RWF")
        print(f"   Recency (25th/50th/75th): {segment_data['recency_days'].quantile(0.25):.1f} / {segment_data['recency_days'].quantile(0.5):.1f} / {segment_data['recency_days'].quantile(0.75):.1f} days")
    
    print("\n" + "="*80)
    print("SUMMARY TABLE")
    print("="*80)
    print()
    
    # Create summary table
    summary = data.groupby('segment_name').agg({
        'motorcyclist_id': 'count',
        'total_spent': ['sum', 'mean'],
        'transaction_count': 'mean',
        'recency_days': 'mean',
        'frequency': 'mean',
        'app_usage_rate': 'mean',
        'failure_rate': 'mean'
    }).round(2)
    
    summary.columns = ['Count', 'Total Revenue', 'Avg Revenue', 'Avg Trans', 'Avg Recency', 'Avg Freq', 'App %', 'Fail %']
    print(summary.to_string())
    
    print("\n" + "="*80)
    print("SEGMENT COMPARISON")
    print("="*80)
    print()
    
    # Compare segments
    print("Highest Revenue Segment:", data.groupby('segment_name')['total_spent'].sum().idxmax())
    print("Largest Segment:", data['segment_name'].value_counts().idxmax())
    print("Most Active Segment:", data.groupby('segment_name')['frequency'].mean().idxmax())
    print("Most Recent Segment:", data.groupby('segment_name')['recency_days'].mean().idxmin())
    
    print("\n" + "="*80)
    print("INSIGHTS & RECOMMENDATIONS")
    print("="*80)
    print()
    
    # Generate insights
    total_revenue = data['total_spent'].sum()
    
    for segment_name in ['Premium VIPs', 'Loyal Regulars', 'At Risk', 'Lost']:
        if segment_name in data['segment_name'].values:
            seg_data = data[data['segment_name'] == segment_name]
            revenue_pct = (seg_data['total_spent'].sum() / total_revenue) * 100
            customer_pct = (len(seg_data) / len(data)) * 100
            
            if segment_name == 'Premium VIPs':
                print(f"✨ {segment_name}:")
                print(f"   {len(seg_data)} customers ({customer_pct:.1f}%) generate {revenue_pct:.1f}% of revenue")
                print(f"   Action: VIP program, exclusive perks, personal account manager")
                
            elif segment_name == 'Loyal Regulars':
                print(f"\n💚 {segment_name}:")
                print(f"   {len(seg_data)} customers ({customer_pct:.1f}%) generate {revenue_pct:.1f}% of revenue")
                print(f"   Action: Loyalty rewards, referral bonuses, upsell to VIP")
                
            elif segment_name == 'At Risk':
                print(f"\n⚠️  {segment_name}:")
                print(f"   {len(seg_data)} customers ({customer_pct:.1f}%) at risk of churning")
                print(f"   Potential revenue loss: {seg_data['total_spent'].sum():,.0f} RWF")
                print(f"   Action: IMMEDIATE win-back campaign, investigate issues")
                
            elif segment_name == 'Lost':
                print(f"\n❌ {segment_name}:")
                print(f"   {len(seg_data)} customers ({customer_pct:.1f}%) likely churned")
                print(f"   Lost revenue: {seg_data['total_spent'].sum():,.0f} RWF")
                print(f"   Action: Final win-back attempt or archive")
    
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80)
    print()
    print("This analysis shows the ACTUAL characteristics of segments in YOUR data.")
    print("Use these insights to create targeted marketing campaigns!")
    print()

except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\nMake sure you have:")
    print("  1. Trained ML models (python train_ml_models.py)")
    print("  2. Database connection configured (db_config.py)")
    print("  3. All required modules installed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
