# 🎯 CUSTOMER SEGMENTATION CRITERIA - COMPLETE EXPLANATION

## Overview

The segments you see on the frontend are created using **K-Means Machine Learning Algorithm**. This is an **unsupervised learning** approach that automatically discovers natural groupings in your customer data.

---

## 🤖 How Segments Are Created (Technical)

### Step 1: Feature Engineering

The ML model analyzes **14 features** for each customer:

#### Primary Features (from customer data):
1. **recency_days** - Days since last transaction
2. **frequency** - Transactions per day
3. **transaction_count** - Total number of transactions
4. **total_spent** - Total money spent (RWF)
5. **avg_transaction** - Average spending per transaction
6. **std_transaction** - Spending consistency (standard deviation)
7. **total_liters** - Total fuel purchased
8. **station_diversity** - Number of different stations used
9. **failure_rate** - Failed payment percentage
10. **app_usage_rate** - Percentage of transactions via mobile app
11. **customer_age_days** - Days since first transaction

#### Derived Features (calculated):
12. **recency_frequency_ratio** - Recency / (Frequency + 0.1)
13. **value_consistency** - Std / (Avg + 1)
14. **engagement_score** - (Transactions × App Usage × 1/(Recency + 1))

### Step 2: K-Means Clustering

The algorithm:
1. **Standardizes** all features (scales them to same range)
2. **Groups customers** into 8 clusters based on similarity
3. **Assigns each customer** to the closest cluster center
4. Each cluster represents customers with **similar behavior patterns**

### Step 3: Segment Naming

After clustering, segments are labeled based on typical characteristics:

```python
Segment Mapping:
0 → 'Premium VIPs'
1 → 'Loyal Regulars'
2 → 'Growth Potential'
3 → 'At Risk'
4 → 'Occasional Users'
5 → 'New Customers'
6 → 'Dormant'
7 → 'Lost'
```

**IMPORTANT:** These names are **labels only**. The actual assignment is based on the customer's position in the 14-dimensional feature space, NOT on predefined rules.

---

## 📊 Segment Characteristics (Typical Patterns)

Based on the ML model's training, here's what each segment typically looks like:

### 1. 🌟 Premium VIPs
**Typical Characteristics:**
- ✅ **Very high** total spending
- ✅ **High** transaction frequency
- ✅ **Low** recency (recent activity)
- ✅ **High** engagement score
- ✅ **Low** failure rate
- ✅ **High** app usage

**Business Profile:**
- Your most valuable customers
- Regular, high-value transactions
- Tech-savvy (use mobile app)
- Reliable payment success

**Approximate Criteria:**
- Total spent: Top 20% of customers
- Frequency: ≥ 3 transactions per week
- Recency: < 7 days
- Avg transaction: Above average

---

### 2. 💚 Loyal Regulars
**Typical Characteristics:**
- ✅ **High** transaction count
- ✅ **Good** frequency
- ✅ **Moderate to high** spending
- ✅ **Low** recency
- ✅ **Consistent** transaction amounts

**Business Profile:**
- Backbone of your business
- Predictable behavior
- Regular but not necessarily highest spenders
- Long customer age

**Approximate Criteria:**
- Transaction count: Top 40%
- Frequency: 1-3 transactions per week
- Customer age: > 90 days
- Low std_transaction (consistent spending)

---

### 3. 📈 Growth Potential
**Typical Characteristics:**
- ✅ **Moderate** spending
- ✅ **Increasing** frequency trend
- ✅ **Good** engagement
- ✅ **Recent** activity
- ⚠️ **Variable** transaction amounts

**Business Profile:**
- New or recently activated customers
- Showing positive trends
- Opportunity for upselling
- Building habits

**Approximate Criteria:**
- Customer age: 30-90 days
- Frequency: Increasing over time
- Engagement score: Above median
- Recency: < 14 days

---

### 4. ⚠️ At Risk
**Typical Characteristics:**
- ⚠️ **Increasing** recency (slowing down)
- ⚠️ **Decreasing** frequency
- ✅ **Previously active** (high historical spending)
- ⚠️ **Higher** failure rate

**Business Profile:**
- Were good customers, now declining
- Need intervention/retention efforts
- High churn probability
- May have service issues

**Approximate Criteria:**
- Recency: 14-30 days (increasing)
- Previous frequency: Was high
- Current frequency: Declining
- May have recent failed payments

---

### 5. 🔵 Occasional Users
**Typical Characteristics:**
- ℹ️ **Low** frequency
- ℹ️ **Moderate** spending per transaction
- ℹ️ **Long** customer age
- ℹ️ **Irregular** usage pattern
- ℹ️ **Multiple** weeks between transactions

**Business Profile:**
- Infrequent but recurring
- Not primary station choice
- Use when convenient
- Lower engagement

**Approximate Criteria:**
- Frequency: < 0.5 transactions per week
- Transaction count: 5-20 total
- Customer age: > 60 days
- Irregular patterns

---

### 6. 🆕 New Customers
**Typical Characteristics:**
- ✅ **Short** customer age
- ✅ **Recent** first transaction
- ℹ️ **Low** transaction count (new)
- ℹ️ **Unknown** long-term pattern

**Business Profile:**
- Just started using service
- Onboarding phase
- Building first impressions
- Critical for retention

**Approximate Criteria:**
- Customer age: < 30 days
- Transaction count: 1-5
- Recency: < 14 days
- No established pattern yet

---

### 7. 😴 Dormant
**Typical Characteristics:**
- ⚠️ **High** recency (30-60 days)
- ⚠️ **Zero** recent activity
- ✅ **Previously active** (not lost yet)
- ℹ️ **Moderate** historical spending

**Business Profile:**
- Haven't transacted recently
- Not yet lost but need re-activation
- Win-back opportunity
- May be using competitors

**Approximate Criteria:**
- Recency: 30-60 days
- Previous activity: Yes
- Frequency: Was moderate
- Engagement: Declining

---

### 8. ❌ Lost
**Typical Characteristics:**
- ❌ **Very high** recency (> 60 days)
- ❌ **No** recent activity
- ❌ **Low** engagement score
- ℹ️ **May have** historical spending

**Business Profile:**
- Effectively churned
- Extremely difficult to win back
- May have switched permanently
- Lowest priority for retention

**Approximate Criteria:**
- Recency: > 60 days
- Last transaction: > 2 months ago
- Frequency: Near zero
- Engagement: Very low

---

## 🔍 How to See Actual Segment Criteria

Since K-Means assigns segments based on **cluster centers in 14-dimensional space**, the actual criteria are complex. Here's how to understand YOUR specific segments:

### Method 1: Check Segment Statistics (API)

```bash
curl http://localhost:8000/api/ml/segments
```

This returns:
```json
{
  "segments": [
    {
      "segment_name": "Premium VIPs",
      "customer_count": 45,
      "avg_revenue_per_customer": 2500000.00,
      "avg_transactions": 25.5,
      "avg_recency_days": 3.2,
      "avg_frequency": 0.85
    },
    ...
  ]
}
```

### Method 2: Generate Segment Profile Report

Create this file: `A:\MD\fuel\analyze_segments.py`

```python
#!/usr/bin/env python3
"""
Analyze actual segment characteristics from your data
"""

from datetime import datetime, timedelta
from train_ml_models import calculate_customer_metrics
from ml_engine import MLEngine
from jalikoi_analytics_db import JalikoiAnalyticsVisualized
from db_config import DB_CONFIG

# Load data
analytics = JalikoiAnalyticsVisualized(DB_CONFIG, use_database=True)
df = analytics.df
customer_metrics = analytics.customer_metrics

# Load ML engine and predict segments
ml_engine = MLEngine(model_dir="ml_models")
predictions = ml_engine.predict_segments(customer_metrics)

# Merge
data = customer_metrics.merge(predictions, on='motorcyclist_id')

# Analyze each segment
print("="*80)
print("ACTUAL SEGMENT CHARACTERISTICS")
print("="*80)
print()

for segment_name in predictions['segment_name'].unique():
    segment_data = data[data['segment_name'] == segment_name]
    
    print(f"\n{segment_name}")
    print("-"*80)
    print(f"Count: {len(segment_data)} customers")
    print(f"\nKey Metrics:")
    print(f"  Avg Recency: {segment_data['recency_days'].mean():.1f} days")
    print(f"  Avg Frequency: {segment_data['frequency'].mean():.2f} trans/day")
    print(f"  Avg Transactions: {segment_data['transaction_count'].mean():.1f}")
    print(f"  Avg Spent: {segment_data['total_spent'].mean():,.0f} RWF")
    print(f"  Avg per Trans: {segment_data['avg_transaction'].mean():,.0f} RWF")
    print(f"  Avg Customer Age: {segment_data['customer_age_days'].mean():.0f} days")
    print(f"  App Usage Rate: {segment_data['app_usage_rate'].mean():.1%}")
    print(f"  Failure Rate: {segment_data['failure_rate'].mean():.1%}")
    
    print(f"\nRanges:")
    print(f"  Recency: {segment_data['recency_days'].min():.0f} - {segment_data['recency_days'].max():.0f} days")
    print(f"  Spending: {segment_data['total_spent'].min():,.0f} - {segment_data['total_spent'].max():,.0f} RWF")

print("\n" + "="*80)
```

Run:
```bash
cd A:\MD\fuel
python analyze_segments.py
```

---

## 📈 Segment Movement

Customers can move between segments as their behavior changes:

**Example Flow:**
```
New Customers (Week 1)
    ↓
Growth Potential (Month 1-3)
    ↓
Loyal Regulars (Month 3-12)
    ↓ (if behavior declines)
At Risk (Month 12-13)
    ↓ (if no action taken)
Dormant (Month 13-15)
    ↓
Lost (Month 15+)
```

**Or upward:**
```
Occasional Users
    ↓ (increased activity)
Growth Potential
    ↓
Loyal Regulars
    ↓
Premium VIPs
```

---

## 🎯 Key Takeaways

1. **Dynamic Assignment**: Segments are assigned by ML algorithm, not fixed rules
2. **Multi-dimensional**: Based on 14 features, not just one metric
3. **Data-Driven**: Reflects actual patterns in YOUR customer base
4. **Evolving**: Customers move between segments as behavior changes
5. **Relative**: "High" and "Low" are relative to your customer population

---

## 🔧 How to Get Exact Criteria

Run these commands to see the exact characteristics:

```bash
# See segment statistics
curl http://localhost:8000/api/ml/segments

# Generate detailed report
cd A:\MD\fuel
python analyze_segments.py
```

This will show you the **actual** thresholds and characteristics for YOUR data!

---

## 💡 Using Segments for Business Actions

**Premium VIPs:**
- Action: VIP program, exclusive offers
- Goal: Retain at all costs

**Loyal Regulars:**
- Action: Loyalty rewards, referral incentives
- Goal: Upsell to VIP tier

**Growth Potential:**
- Action: Personalized campaigns, education
- Goal: Convert to Loyal

**At Risk:**
- Action: Immediate intervention, win-back offers
- Goal: Prevent churn

**Occasional Users:**
- Action: Frequency campaigns, convenience features
- Goal: Increase usage

**New Customers:**
- Action: Onboarding, first-purchase discounts
- Goal: Drive second purchase

**Dormant:**
- Action: Re-activation campaigns
- Goal: Win back

**Lost:**
- Action: Archive or final win-back attempt
- Goal: Learn from churn

---

**The segment names are descriptive labels, but the actual assignment is based on sophisticated ML pattern recognition across 14 customer behavior dimensions!**
