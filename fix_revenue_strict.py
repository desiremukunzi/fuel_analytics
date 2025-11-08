#!/usr/bin/env python3
"""
FIX REVENUE MODEL - Apply strict constraints to prevent unrealistic predictions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import pickle
from pathlib import Path

print("="*80)
print("FIXING REVENUE MODEL WITH STRICT CONSTRAINTS")
print("="*80)
print()

# Import modules
try:
    from database_connector import JalikoiDatabaseConnector
    from db_config import DB_CONFIG
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
except ImportError as e:
    print(f"Error: {e}")
    sys.exit(1)

# Fetch data
print("Fetching data...")
end_date = datetime.now().date()
start_date = end_date - timedelta(days=90)

query = f"""
    SELECT 
        id, station_id, motorcyclist_id, source, payer_phone,
        fuel_type, liter, pump_price, amount, motari_code,
        cashback_wallet_enabled, sp_txn_id, payment_status,
        payment_method_id, created_at, updated_at
    FROM DailyTransactionPayments
    WHERE payment_status IN (200, 500)
    AND DATE(created_at) >= '{start_date}'
    AND DATE(created_at) <= '{end_date}'
    ORDER BY created_at DESC
"""

try:
    with JalikoiDatabaseConnector(DB_CONFIG) as db:
        df = db.fetch_data(query)
        if df is None or df.empty:
            print("No data!")
            sys.exit(1)
        print(f"✓ Fetched {len(df):,} transactions")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

# Preprocess
print("Processing...")
df['created_at'] = pd.to_datetime(df['created_at'])
df_success = df[df['payment_status'] == 200].copy()
reference_date = df['created_at'].max()

# Calculate customer metrics
customer_metrics = df_success.groupby('motorcyclist_id').agg({
    'id': 'count',
    'amount': ['sum', 'mean', 'std'],
    'liter': ['sum', 'mean'],
    'station_id': lambda x: x.nunique(),
    'created_at': ['min', 'max'],
    'source': lambda x: (x == 'APP').sum() / len(x)
}).reset_index()

customer_metrics.columns = [
    'motorcyclist_id', 'transaction_count', 'total_spent', 'avg_transaction',
    'std_transaction', 'total_liters', 'avg_liters', 'station_diversity', 
    'first_transaction', 'last_transaction', 'app_usage_rate'
]

customer_metrics['recency_days'] = (
    reference_date - customer_metrics['last_transaction']
).dt.total_seconds() / (24 * 3600)

customer_metrics['customer_age_days'] = (
    customer_metrics['last_transaction'] - customer_metrics['first_transaction']
).dt.total_seconds() / (24 * 3600)
customer_metrics['customer_age_days'] = customer_metrics['customer_age_days'].replace(0, 0.1)

customer_metrics['frequency'] = (
    customer_metrics['transaction_count'] / customer_metrics['customer_age_days']
)

# Failure rate
failure_rates = df.groupby('motorcyclist_id').agg({
    'payment_status': lambda x: (x == 500).sum() / len(x)
}).reset_index()
failure_rates.columns = ['motorcyclist_id', 'failure_rate']
customer_metrics = customer_metrics.merge(failure_rates, on='motorcyclist_id', how='left')
customer_metrics['failure_rate'] = customer_metrics['failure_rate'].fillna(0)

# Engagement score
customer_metrics['engagement_score'] = (
    (1 / (customer_metrics['recency_days'] + 1)) * 
    customer_metrics['frequency'] * 
    np.log1p(customer_metrics['transaction_count'])
)

customer_metrics['std_transaction'] = customer_metrics['std_transaction'].fillna(
    customer_metrics['avg_transaction'] * 0.1
)

print(f"✓ Processed {len(customer_metrics):,} customers")

# CRITICAL: Create REALISTIC revenue labels with STRICT constraints
print("\nCreating realistic revenue labels with STRICT CONSTRAINTS...")

def calculate_super_realistic_revenue(row):
    """Calculate revenue with VERY STRICT constraints"""
    
    # Base: simple daily rate * 180 days
    daily_spend = row['total_spent'] / max(row['customer_age_days'], 1)
    base_forecast = daily_spend * 180
    
    # STRICT CONSTRAINTS:
    
    # 1. ABSOLUTE MAX: 2x their historical total (very conservative)
    absolute_max = row['total_spent'] * 2
    
    # 2. For new customers (< 30 days): Only 1.5x what they've done
    if row['customer_age_days'] < 30:
        absolute_max = row['total_spent'] * 1.5
    
    # 3. For inactive customers (> 30 days): Heavily penalize
    if row['recency_days'] > 30:
        inactivity_penalty = max(0.05, 1 - (row['recency_days'] / 180))
        base_forecast *= inactivity_penalty
    
    # 4. For very new customers (< 10 transactions): Be very cautious
    if row['transaction_count'] < 10:
        base_forecast *= 0.3  # Only 30% of projection
    
    # 5. Low frequency customers: reduce forecast
    if row['frequency'] < 0.1:  # Less than once per 10 days
        base_forecast *= 0.5
    
    # Apply absolute cap
    forecast = min(base_forecast, absolute_max)
    
    # 6. HARD CEILING: No prediction over 50M RWF
    forecast = min(forecast, 50_000_000)
    
    # 7. Ensure non-negative
    forecast = max(0, forecast)
    
    return forecast

revenue_labels = customer_metrics.apply(calculate_super_realistic_revenue, axis=1)

print(f"\nRevenue Label Statistics:")
print(f"  Min: {revenue_labels.min():,.2f} RWF")
print(f"  Max: {revenue_labels.max():,.2f} RWF")
print(f"  Mean: {revenue_labels.mean():,.2f} RWF")
print(f"  Median: {revenue_labels.median():,.2f} RWF")

# Check ratios
ratios = revenue_labels / customer_metrics['total_spent']
print(f"\nForecast/Historical Ratios:")
print(f"  Min: {ratios.min():.2f}x")
print(f"  Max: {ratios.max():.2f}x")
print(f"  Mean: {ratios.mean():.2f}x")
print(f"  Median: {ratios.median():.2f}x")

if ratios.max() > 5:
    print("⚠️  WARNING: Some ratios still > 5x! Applying additional cap...")
    revenue_labels = np.minimum(revenue_labels, customer_metrics['total_spent'] * 2)
    print("✓ Ratios capped at 2x historical")

# Features
FEATURE_COLUMNS = [
    'recency_days', 'frequency', 'transaction_count', 'total_spent',
    'avg_transaction', 'std_transaction', 'total_liters', 'station_diversity',
    'failure_rate', 'app_usage_rate', 'customer_age_days', 'engagement_score'
]

X = customer_metrics[FEATURE_COLUMNS].copy().fillna(0)
X = X.replace([np.inf, -np.inf], 0)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, revenue_labels, test_size=0.2, random_state=42
)

# Scale
revenue_scaler = StandardScaler()
X_train_scaled = revenue_scaler.fit_transform(X_train)
X_test_scaled = revenue_scaler.transform(X_test)

# Train with CONSERVATIVE settings
print("\nTraining model with CONSERVATIVE settings...")
revenue_model = GradientBoostingRegressor(
    n_estimators=50,  # Fewer trees
    learning_rate=0.01,  # Very slow learning
    max_depth=3,  # Shallow trees
    min_samples_split=50,  # More samples needed
    min_samples_leaf=20,  # Bigger leaves
    loss='huber',
    alpha=0.9,  # Robust to outliers
    random_state=42
)

revenue_model.fit(X_train_scaled, y_train)

# Evaluate
y_pred = revenue_model.predict(X_test_scaled)

# POST-PREDICTION CONSTRAINTS (critical!)
y_pred = np.maximum(0, y_pred)  # Non-negative
y_pred = np.minimum(y_pred, 50_000_000)  # Max 50M

# Also cap at 2x historical for test set
test_customers = customer_metrics.iloc[X_test.index]
max_allowed = test_customers['total_spent'].values * 2
y_pred = np.minimum(y_pred, max_allowed)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"\n✓ Model trained!")
print(f"  MAE: {mae:,.2f} RWF")
print(f"  RMSE: {rmse:,.2f} RWF")
print(f"  R² Score: {r2:.4f}")

# Test on full dataset
print("\nTesting on full dataset...")
X_full_scaled = revenue_scaler.transform(X)
predictions_full = revenue_model.predict(X_full_scaled)

# Apply same constraints
predictions_full = np.maximum(0, predictions_full)
predictions_full = np.minimum(predictions_full, 50_000_000)
max_allowed_full = customer_metrics['total_spent'].values * 2
predictions_full = np.minimum(predictions_full, max_allowed_full)

print(f"  Min prediction: {predictions_full.min():,.2f} RWF")
print(f"  Max prediction: {predictions_full.max():,.2f} RWF")
print(f"  Mean prediction: {predictions_full.mean():,.2f} RWF")

# Check ratios
final_ratios = predictions_full / customer_metrics['total_spent'].replace(0, 1)
print(f"\n  Final ratios:")
print(f"    Max: {final_ratios.max():.2f}x")
print(f"    Mean: {final_ratios.mean():.2f}x")

if predictions_full.max() > 50_000_000:
    print("⚠️  ERROR: Still have predictions > 50M!")
else:
    print("✓ All predictions within bounds")

# Load existing models and update revenue model only
print("\nUpdating revenue model...")
model_file = Path("ml_models/ml_models.pkl")

if model_file.exists():
    with open(model_file, 'rb') as f:
        models = pickle.load(f)
else:
    models = {}

models['revenue_model'] = revenue_model
models['revenue_scaler'] = revenue_scaler
models['metadata'] = models.get('metadata', {})
models['metadata']['revenue_mae'] = float(mae)
models['metadata']['revenue_rmse'] = float(rmse)
models['metadata']['revenue_r2'] = float(r2)
models['metadata']['last_revenue_retrain'] = datetime.now().isoformat()

with open(model_file, 'wb') as f:
    pickle.dump(models, f)

print(f"✓ Revenue model updated!")

print("\n" + "="*80)
print("✅ REVENUE MODEL FIXED WITH STRICT CONSTRAINTS!")
print("="*80)
print()
print("Constraints applied:")
print("  • Max prediction: 2x historical spending")
print("  • Absolute ceiling: 50M RWF")
print("  • New customers: Max 1.5x")
print("  • Inactive customers: Heavily penalized")
print("  • Low transaction customers: Only 30% of projection")
print()
print("Next: Restart API and test!")
print("  sudo systemctl restart jalikoi-api")
print()
