#!/usr/bin/env python3
"""
Check what features the model was trained with
"""

import pickle
from pathlib import Path

model_path = Path("ml_models/ml_models.pkl")

with open(model_path, 'rb') as f:
    models = pickle.load(f)

churn_model = models.get('churn_model')

print("Model type:", type(churn_model).__name__)
print()

# Try different ways to get feature names
if hasattr(churn_model, 'feature_names_in_'):
    print("Features from feature_names_in_:")
    for i, feat in enumerate(churn_model.feature_names_in_, 1):
        print(f"   {i}. {feat}")
elif hasattr(churn_model, 'n_features_in_'):
    print(f"Number of features: {churn_model.n_features_in_}")
    print("(Feature names not stored)")
else:
    print("Cannot determine features from model")

# Check scaler too
scaler = models.get('scaler')
if scaler and hasattr(scaler, 'feature_names_in_'):
    print("\nFeatures from scaler:")
    for i, feat in enumerate(scaler.feature_names_in_, 1):
        print(f"   {i}. {feat}")
