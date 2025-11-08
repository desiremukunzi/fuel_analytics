#!/usr/bin/env python3
"""
Complete ML Model Fix - Retrain all models with correct features
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import pickle
from pathlib import Path

print("="*80)
print("COMPLETE ML MODEL FIX")
print("="*80)
print()

# Import required modules
try:
    from database_connector import JalikoiDatabaseConnector
    from db_config import DB_CONFIG
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.cluster import KMeans
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                                 f1_score, mean_absolute_error, mean_squared_error, 
                                 r2_score, silhouette_score)
except ImportError as e:
    print(f"Error importing: {e}")
    sys.exit(1)

print("Step 1: Fetching transaction data...")
print("-"*80)

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
            print("No data found!")
            sys.exit(1)
        print(f"✓ Fetched {len(df):,} transactions")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

print("\nStep 2: Preprocessing data...")
print("-"*80)

df['created_at'] = pd.to_datetime(df['created_at'])
df['date'] = df['created_at'].dt.date
df['hour'] = df['created_at'].dt.hour
df['day_of_week'] = df['created_at'].dt.dayofweek

print("✓ Data preprocessed")

print("\nStep 3: Calculating customer metrics...")
print("-"*80)

df_success = df[df['payment_status'] == 200].copy()
reference_date = df['created_at'].max()

customer_metrics = df_success.groupby('motorcyclist_id').agg({
    'id': 'count',
    'amount': ['sum', 'mean', 'std', 'min', 'max'],
    'liter': ['sum', 'mean'],
    'station_id': lambda x: x.nunique(),
    'created_at': ['min', 'max'],
    'payment_method_id': 'first',
    'source': lambda x: (x == 'APP').sum() / len(x)
}).reset_index()

customer_metrics.columns = [
    'motorcyclist_id', 'transaction_count', 'total_spent', 'avg_transaction',
    'std_transaction', 'min_transaction', 'max_transaction',
    'total_liters', 'avg_liters', 'station_diversity', 
    'first_transaction', 'last_transaction', 'payment_method', 'app_usage_rate'
]

# Calculate time-based metrics
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

# Calculate failure rate
failure_rates = df.groupby('motorcyclist_id').agg({
    'payment_status': lambda x: (x == 500).sum() / len(x)
}).reset_index()
failure_rates.columns = ['motorcyclist_id', 'failure_rate']
customer_metrics = customer_metrics.merge(failure_rates, on='motorcyclist_id', how='left')
customer_metrics['failure_rate'] = customer_metrics['failure_rate'].fillna(0)

# Calculate engagement score
customer_metrics['engagement_score'] = (
    (1 / (customer_metrics['recency_days'] + 1)) * 
    customer_metrics['frequency'] * 
    np.log1p(customer_metrics['transaction_count'])
)

# Fill NaN in std_transaction
customer_metrics['std_transaction'] = customer_metrics['std_transaction'].fillna(
    customer_metrics['avg_transaction'] * 0.1
)

print(f"✓ Calculated metrics for {len(customer_metrics):,} customers")

# Define feature columns that will be used for ALL models
FEATURE_COLUMNS = [
    'recency_days', 'frequency', 'transaction_count', 'total_spent',
    'avg_transaction', 'std_transaction', 'total_liters', 'station_diversity',
    'failure_rate', 'app_usage_rate', 'customer_age_days', 'engagement_score'
]

print(f"\nFeatures to use: {FEATURE_COLUMNS}")

# ============================================================================
# TRAIN CHURN MODEL
# ============================================================================

print("\n" + "="*80)
print("TRAINING CHURN MODEL")
print("="*80)

# Create churn labels (30 days inactivity = churned)
churn_labels = (customer_metrics['recency_days'] > 30).astype(int)
print(f"Churned: {churn_labels.sum()} ({churn_labels.mean()*100:.1f}%)")
print(f"Active: {len(churn_labels) - churn_labels.sum()} ({(1-churn_labels.mean())*100:.1f}%)")

# Prepare features
X_churn = customer_metrics[FEATURE_COLUMNS].copy().fillna(0)
X_churn = X_churn.replace([np.inf, -np.inf], 0)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X_churn, churn_labels, test_size=0.2, random_state=42, stratify=churn_labels
)

# Scale
churn_scaler = StandardScaler()
X_train_scaled = churn_scaler.fit_transform(X_train)
X_test_scaled = churn_scaler.transform(X_test)

# Train
churn_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=20,
    class_weight='balanced',
    random_state=42
)
churn_model.fit(X_train_scaled, y_train)

# Evaluate
y_pred = churn_model.predict(X_test_scaled)
churn_accuracy = accuracy_score(y_test, y_pred)
churn_precision = precision_score(y_test, y_pred, zero_division=0)
churn_recall = recall_score(y_test, y_pred, zero_division=0)
churn_f1 = f1_score(y_test, y_pred, zero_division=0)

print(f"\n✓ Churn Model Trained")
print(f"  Accuracy: {churn_accuracy:.2%}")
print(f"  Precision: {churn_precision:.2%}")
print(f"  Recall: {churn_recall:.2%}")
print(f"  F1 Score: {churn_f1:.2%}")

# ============================================================================
# TRAIN REVENUE MODEL
# ============================================================================

print("\n" + "="*80)
print("TRAINING REVENUE MODEL")
print("="*80)

# Create realistic revenue labels
def calculate_realistic_revenue(row):
    """Calculate realistic 6-month revenue forecast with constraints"""
    
    # Base forecast
    base_forecast = row['avg_transaction'] * row['frequency'] * 180
    
    # Constraints
    max_reasonable = row['total_spent'] * 3  # Max 3x historical
    
    if row['customer_age_days'] < 30:
        max_reasonable = row['total_spent'] * 2  # New customers: 2x
    
    if row['recency_days'] > 30:
        decline_factor = max(0.1, 1 - (row['recency_days'] / 180))
        base_forecast *= decline_factor
    
    if row['transaction_count'] < 5:
        base_forecast *= 0.5  # Uncertain for new customers
    
    forecast = np.clip(base_forecast, 0, max_reasonable)
    forecast *= np.random.uniform(0.9, 1.1)  # Small noise
    
    return max(0, forecast)

revenue_labels = customer_metrics.apply(calculate_realistic_revenue, axis=1)

print(f"Revenue labels - Min: {revenue_labels.min():,.0f}, Max: {revenue_labels.max():,.0f}, Mean: {revenue_labels.mean():,.0f}")

# Prepare features (same as churn!)
X_revenue = customer_metrics[FEATURE_COLUMNS].copy().fillna(0)
X_revenue = X_revenue.replace([np.inf, -np.inf], 0)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X_revenue, revenue_labels, test_size=0.2, random_state=42
)

# Scale
revenue_scaler = StandardScaler()
X_train_scaled = revenue_scaler.fit_transform(X_train)
X_test_scaled = revenue_scaler.transform(X_test)

# Train
revenue_model = GradientBoostingRegressor(
    n_estimators=100,
    learning_rate=0.05,
    max_depth=4,
    min_samples_split=20,
    min_samples_leaf=10,
    loss='huber',
    random_state=42
)
revenue_model.fit(X_train_scaled, y_train)

# Evaluate
y_pred = revenue_model.predict(X_test_scaled)
y_pred = np.maximum(0, y_pred)  # Non-negative

revenue_mae = mean_absolute_error(y_test, y_pred)
revenue_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
revenue_r2 = r2_score(y_test, y_pred)

print(f"\n✓ Revenue Model Trained")
print(f"  MAE: {revenue_mae:,.2f} RWF")
print(f"  RMSE: {revenue_rmse:,.2f} RWF")
print(f"  R² Score: {revenue_r2:.4f}")

# ============================================================================
# TRAIN SEGMENTATION MODEL
# ============================================================================

print("\n" + "="*80)
print("TRAINING SEGMENTATION MODEL")
print("="*80)

# Prepare features (same as others!)
X_segment = customer_metrics[FEATURE_COLUMNS].copy().fillna(0)
X_segment = X_segment.replace([np.inf, -np.inf], 0)

# Scale
segmentation_scaler = StandardScaler()
X_scaled = segmentation_scaler.fit_transform(X_segment)

# Train K-Means
segmentation_model = KMeans(n_clusters=8, random_state=42, n_init=10)
clusters = segmentation_model.fit_predict(X_scaled)

# Evaluate
silhouette = silhouette_score(X_scaled, clusters)

print(f"\n✓ Segmentation Model Trained")
print(f"  Clusters: 8")
print(f"  Silhouette Score: {silhouette:.4f}")
print(f"  Customers per cluster:")
unique, counts = np.unique(clusters, return_counts=True)
for cluster_id, count in zip(unique, counts):
    print(f"    Cluster {cluster_id}: {count} customers")

# ============================================================================
# TRAIN ANOMALY DETECTOR
# ============================================================================

print("\n" + "="*80)
print("TRAINING ANOMALY DETECTOR")
print("="*80)

# Use transaction-level features for anomaly detection
anomaly_features = df[['amount', 'liter', 'pump_price', 'hour', 'day_of_week']].copy()
anomaly_features = anomaly_features.fillna(0)
anomaly_features = anomaly_features.replace([np.inf, -np.inf], 0)

# Scale
anomaly_scaler = StandardScaler()
features_scaled = anomaly_scaler.fit_transform(anomaly_features)

# Train
anomaly_model = IsolationForest(
    contamination=0.05,
    random_state=42,
    n_estimators=100
)
anomaly_model.fit(features_scaled)

# Evaluate
predictions = anomaly_model.predict(features_scaled)
n_anomalies = (predictions == -1).sum()

print(f"\n✓ Anomaly Detector Trained")
print(f"  Anomalies detected: {n_anomalies:,} ({n_anomalies/len(df)*100:.2f}%)")

# ============================================================================
# SAVE ALL MODELS
# ============================================================================

print("\n" + "="*80)
print("SAVING MODELS")
print("="*80)

model_dir = Path("ml_models")
model_dir.mkdir(exist_ok=True)
model_file = model_dir / "ml_models.pkl"

models = {
    'churn_model': churn_model,
    'revenue_model': revenue_model,
    'segmentation_model': segmentation_model,
    'anomaly_model': anomaly_model,
    'churn_scaler': churn_scaler,
    'revenue_scaler': revenue_scaler,
    'segmentation_scaler': segmentation_scaler,
    'anomaly_scaler': anomaly_scaler,
    'feature_columns': FEATURE_COLUMNS,  # Save feature list!
    'metadata': {
        'churn_accuracy': float(churn_accuracy),
        'churn_precision': float(churn_precision),
        'churn_recall': float(churn_recall),
        'churn_f1': float(churn_f1),
        'revenue_mae': float(revenue_mae),
        'revenue_rmse': float(revenue_rmse),
        'revenue_r2': float(revenue_r2),
        'segmentation_silhouette': float(silhouette),
        'anomaly_contamination': 0.05,
        'last_trained': datetime.now().isoformat(),
        'training_samples': len(customer_metrics),
        'n_features': len(FEATURE_COLUMNS)
    }
}

with open(model_file, 'wb') as f:
    pickle.dump(models, f)

print(f"✓ Models saved to {model_file}")

# Test predictions
print("\n" + "="*80)
print("TESTING PREDICTIONS")
print("="*80)

# Test revenue predictions
test_predictions = revenue_model.predict(revenue_scaler.transform(X_revenue))
test_predictions = np.maximum(0, test_predictions)

print(f"\nRevenue Predictions:")
print(f"  Min: {test_predictions.min():,.2f} RWF")
print(f"  Max: {test_predictions.max():,.2f} RWF")
print(f"  Mean: {test_predictions.mean():,.2f} RWF")
print(f"  Median: {np.median(test_predictions):,.2f} RWF")

# Check for issues
if test_predictions.min() < 0:
    print("  ⚠️  WARNING: Negative predictions found!")
if test_predictions.max() > 100_000_000:
    print("  ⚠️  WARNING: Very high predictions (>100M) found!")
else:
    print("  ✓ All predictions reasonable")

print("\n" + "="*80)
print("✅ ALL MODELS RETRAINED SUCCESSFULLY!")
print("="*80)
print()
print("Model Performance Summary:")
print(f"  • Churn Prediction: {churn_accuracy:.2%} accuracy")
print(f"  • Revenue Forecast: MAE {revenue_mae:,.0f} RWF")
print(f"  • Customer Segments: 8 clusters, {silhouette:.3f} silhouette")
print(f"  • Anomaly Detection: {n_anomalies/len(df)*100:.1f}% flagged")
print()
print("Next steps:")
print("  1. Restart API: python jalikoi_analytics_api_ml.py")
print("  2. Or on server: sudo systemctl restart jalikoi-api")
print("  3. Test in browser")
print()
