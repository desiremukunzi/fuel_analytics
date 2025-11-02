#!/usr/bin/env python3
"""
Fix ml_engine.py - Give each model its own scaler
"""

print("Fixing ml_engine.py...")

# Read file
with open('ml_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
import shutil
shutil.copy('ml_engine.py', 'ml_engine.py.backup_before_scaler_fix')
print("✓ Backup created")

# Fix 1: Already done - separate scalers in __init__

# Fix 2: Churn model - use churn_scaler
content = content.replace(
    "X_train_scaled = self.scaler.fit_transform(X_train)\n        X_test_scaled = self.scaler.transform(X_test)\n        \n        # Train Random Forest model",
    "X_train_scaled = self.churn_scaler.fit_transform(X_train)\n        X_test_scaled = self.churn_scaler.transform(X_test)\n        \n        # Train Random Forest model"
)

# Fix 3: Churn prediction - use churn_scaler
content = content.replace(
    "X_scaled = self.scaler.transform(X)\n        \n        # Predict\n        predictions = self.churn_model.predict",
    "X_scaled = self.churn_scaler.transform(X)\n        \n        # Predict\n        predictions = self.churn_model.predict"
)

# Fix 4: Revenue model - use revenue_scaler  
content = content.replace(
    "X_train_scaled = self.scaler.fit_transform(X_train)\n        X_test_scaled = self.scaler.transform(X_test)\n        \n        # Train Gradient Boosting model",
    "X_train_scaled = self.revenue_scaler.fit_transform(X_train)\n        X_test_scaled = self.revenue_scaler.transform(X_test)\n        \n        # Train Gradient Boosting model"
)

# Fix 5: Revenue prediction - use revenue_scaler
content = content.replace(
    "X_scaled = self.scaler.transform(X)\n        \n        # Predict\n        predictions = self.revenue_model.predict",
    "X_scaled = self.revenue_scaler.transform(X)\n        \n        # Predict\n        predictions = self.revenue_model.predict"
)

# Fix 6: Segmentation model - use segmentation_scaler
content = content.replace(
    "X_scaled = self.scaler.fit_transform(X)\n        \n        # Train K-Means model",
    "X_scaled = self.segmentation_scaler.fit_transform(X)\n        \n        # Train K-Means model"
)

# Fix 7: Segmentation prediction - use segmentation_scaler
content = content.replace(
    "X_scaled = self.scaler.transform(X)\n        \n        # Predict\n        segments = self.segmentation_model.predict",
    "X_scaled = self.segmentation_scaler.transform(X)\n        \n        # Predict\n        segments = self.segmentation_model.predict"
)

# Fix 8: Anomaly model - use anomaly_scaler
content = content.replace(
    "features_scaled = self.scaler.fit_transform(features)\n        \n        # Train Isolation Forest",
    "features_scaled = self.anomaly_scaler.fit_transform(features)\n        \n        # Train Isolation Forest"
)

# Fix 9: Anomaly prediction - use anomaly_scaler
content = content.replace(
    "features_scaled = self.scaler.transform(features)\n        \n        # Predict\n        predictions = self.anomaly_model.predict",
    "features_scaled = self.anomaly_scaler.transform(features)\n        \n        # Predict\n        predictions = self.anomaly_model.predict"
)

# Fix 10: Save models - save all scalers
old_save = """        models = {
            'churn_model': self.churn_model,
            'revenue_model': self.revenue_model,
            'segmentation_model': self.segmentation_model,
            'anomaly_model': self.anomaly_model,
            'scaler': self.scaler,
            'metadata': self.metadata
        }"""

new_save = """        models = {
            'churn_model': self.churn_model,
            'revenue_model': self.revenue_model,
            'segmentation_model': self.segmentation_model,
            'anomaly_model': self.anomaly_model,
            'churn_scaler': self.churn_scaler,
            'revenue_scaler': self.revenue_scaler,
            'segmentation_scaler': self.segmentation_scaler,
            'anomaly_scaler': self.anomaly_scaler,
            'metadata': self.metadata
        }"""

content = content.replace(old_save, new_save)

# Fix 11: Load models - load all scalers
old_load = """                self.churn_model = models.get('churn_model')
                self.revenue_model = models.get('revenue_model')
                self.segmentation_model = models.get('segmentation_model')
                self.anomaly_model = models.get('anomaly_model')
                self.scaler = models.get('scaler', StandardScaler())
                self.metadata = models.get('metadata', {})"""

new_load = """                self.churn_model = models.get('churn_model')
                self.revenue_model = models.get('revenue_model')
                self.segmentation_model = models.get('segmentation_model')
                self.anomaly_model = models.get('anomaly_model')
                self.churn_scaler = models.get('churn_scaler', StandardScaler())
                self.revenue_scaler = models.get('revenue_scaler', StandardScaler())
                self.segmentation_scaler = models.get('segmentation_scaler', StandardScaler())
                self.anomaly_scaler = models.get('anomaly_scaler', StandardScaler())
                self.metadata = models.get('metadata', {})"""

content = content.replace(old_load, new_load)

# Write fixed file
with open('ml_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ ml_engine.py fixed!")
print("\nChanges made:")
print("  - Churn model now uses churn_scaler")
print("  - Revenue model now uses revenue_scaler")
print("  - Segmentation model now uses segmentation_scaler")
print("  - Anomaly model now uses anomaly_scaler")
print("\nBackup: ml_engine.py.backup_before_scaler_fix")
print("\nNow run: python final_reset.py")
