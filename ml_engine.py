#!/usr/bin/env python3
"""
ML Engine for Jalikoi Analytics
================================
Scikit-learn powered machine learning models for:
- Churn prediction
- Customer segmentation
- Anomaly detection
- Revenue forecasting
- Recommendation system
"""

import pandas as pd
import numpy as np
import pickle
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_absolute_error, mean_squared_error, r2_score,
    classification_report, confusion_matrix
)
import warnings
warnings.filterwarnings('ignore')


class MLEngine:
    """Machine Learning Engine for customer analytics"""
    
    def __init__(self, model_dir: str = "ml_models"):
        """Initialize ML Engine
        
        Args:
            model_dir: Directory to save/load trained models
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        # Initialize models
        self.churn_model = None
        self.revenue_model = None
        self.segmentation_model = None
        self.anomaly_model = None
        
        # FIXED: Each model needs its own scaler!
        self.churn_scaler = StandardScaler()
        self.revenue_scaler = StandardScaler()
        self.segmentation_scaler = StandardScaler()
        self.anomaly_scaler = StandardScaler()
        
        # Model metadata
        self.metadata = {
            'churn_accuracy': None,
            'revenue_mae': None,
            'last_trained': None,
            'training_samples': None
        }
        
        # Load existing models if available
        self.load_models()
    
    def prepare_features(self, customer_metrics: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Prepare features for ML models
        
        Args:
            customer_metrics: Customer metrics dataframe
            
        Returns:
            Tuple of (features_df, feature_names)
        """
        features = customer_metrics[[
            'recency_days',
            'frequency',
            'transaction_count',
            'total_spent',
            'avg_transaction',
            'std_transaction',
            'total_liters',
            'station_diversity',
            'failure_rate',
            'app_usage_rate',
            'customer_age_days'
        ]].copy()
        
        # Handle missing values
        features = features.fillna(0)
        
        # Add derived features
        features['recency_frequency_ratio'] = features['recency_days'] / (features['frequency'] + 0.1)
        features['value_consistency'] = features['std_transaction'] / (features['avg_transaction'] + 1)
        features['engagement_score'] = (
            features['transaction_count'] * 
            features['app_usage_rate'] * 
            (1 / (features['recency_days'] + 1))
        )
        
        feature_names = features.columns.tolist()
        
        return features, feature_names
    
    def train_churn_model(self, customer_metrics: pd.DataFrame, churn_labels: pd.Series) -> Dict[str, Any]:
        """Train churn prediction model
        
        Args:
            customer_metrics: Customer metrics dataframe
            churn_labels: Binary labels (1=churned, 0=active)
            
        Returns:
            Training results and metrics
        """
        print("Training Churn Prediction Model...")
        
        # Prepare features
        X, feature_names = self.prepare_features(customer_metrics)
        y = churn_labels
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.churn_scaler.fit_transform(X_train)
        X_test_scaled = self.churn_scaler.transform(X_test)
        
        # Train Random Forest model
        self.churn_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=20,
            min_samples_leaf=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.churn_model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = self.churn_model.predict(X_test_scaled)
        y_pred_proba = self.churn_model.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_names,
            'importance': self.churn_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Cross-validation
        cv_scores = cross_val_score(self.churn_model, X_train_scaled, y_train, cv=5)
        
        # Update metadata
        self.metadata['churn_accuracy'] = accuracy
        self.metadata['last_trained'] = datetime.now().isoformat()
        self.metadata['training_samples'] = len(X_train)
        
        # Save model
        self.save_models()
        
        results = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'cv_mean': float(cv_scores.mean()),
            'cv_std': float(cv_scores.std()),
            'feature_importance': feature_importance.head(10).to_dict('records'),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        print(f"✓ Churn Model Trained - Accuracy: {accuracy:.2%}")
        
        return results
    
    def predict_churn(self, customer_metrics: pd.DataFrame) -> pd.DataFrame:
        """Predict churn probability for customers
        
        Args:
            customer_metrics: Customer metrics dataframe
            
        Returns:
            DataFrame with churn predictions and probabilities
        """
        if self.churn_model is None:
            raise ValueError("Churn model not trained. Train model first.")
        
        # Prepare features
        X, _ = self.prepare_features(customer_metrics)
        X_scaled = self.churn_scaler.transform(X)
        
        # Predict
        predictions = self.churn_model.predict(X_scaled)
        probabilities = self.churn_model.predict_proba(X_scaled)[:, 1]
        
        # Create results dataframe
        results = customer_metrics[['motorcyclist_id']].copy()
        results['churn_prediction'] = predictions
        results['churn_probability'] = probabilities
        results['risk_level'] = pd.cut(
            probabilities,
            bins=[0, 0.3, 0.7, 1.0],
            labels=['Low Risk', 'Medium Risk', 'High Risk']
        )
        
        return results
    
    def train_revenue_model(self, customer_metrics: pd.DataFrame, future_revenue: pd.Series) -> Dict[str, Any]:
        """Train revenue forecasting model
        
        Args:
            customer_metrics: Customer metrics dataframe
            future_revenue: Actual future revenue for training
            
        Returns:
            Training results and metrics
        """
        print("Training Revenue Forecasting Model...")
        
        # Prepare features
        X, feature_names = self.prepare_features(customer_metrics)
        y = future_revenue
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.revenue_scaler.fit_transform(X_train)
        X_test_scaled = self.revenue_scaler.transform(X_test)
        
        # Train Gradient Boosting model
        self.revenue_model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        
        self.revenue_model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = self.revenue_model.predict(X_test_scaled)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_names,
            'importance': self.revenue_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Update metadata
        self.metadata['revenue_mae'] = mae
        
        # Save model
        self.save_models()
        
        results = {
            'mae': float(mae),
            'rmse': float(rmse),
            'r2_score': float(r2),
            'feature_importance': feature_importance.head(10).to_dict('records'),
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        print(f"✓ Revenue Model Trained - MAE: {mae:,.2f}")
        
        return results
    
    def predict_revenue(self, customer_metrics: pd.DataFrame, months: int = 6) -> pd.DataFrame:
        """Predict future revenue for customers
        
        Args:
            customer_metrics: Customer metrics dataframe
            months: Number of months to predict
            
        Returns:
            DataFrame with revenue predictions
        """
        if self.revenue_model is None:
            raise ValueError("Revenue model not trained. Train model first.")
        
        # Prepare features
        X, _ = self.prepare_features(customer_metrics)
        X_scaled = self.revenue_scaler.transform(X)
        
        # Predict
        predictions = self.revenue_model.predict(X_scaled)
        
        # Adjust for time period
        predictions = predictions * (months / 6)  # Adjust from 6-month baseline
        
        # Create results dataframe
        results = customer_metrics[['motorcyclist_id']].copy()
        results['predicted_revenue'] = predictions
        results['confidence'] = 'high'  # Can be improved with prediction intervals
        
        return results
    
    def train_segmentation_model(self, customer_metrics: pd.DataFrame, n_clusters: int = 8) -> Dict[str, Any]:
        """Train customer segmentation model
        
        Args:
            customer_metrics: Customer metrics dataframe
            n_clusters: Number of customer segments
            
        Returns:
            Training results
        """
        print("Training Customer Segmentation Model...")
        
        # Prepare features
        X, feature_names = self.prepare_features(customer_metrics)
        
        # Scale features
        X_scaled = self.segmentation_scaler.fit_transform(X)
        
        # Train K-Means model
        self.segmentation_model = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            n_init=10
        )
        
        segments = self.segmentation_model.fit_predict(X_scaled)
        
        # Calculate segment characteristics
        segment_profiles = []
        for i in range(n_clusters):
            mask = segments == i
            segment_data = X[mask]
            
            profile = {
                'segment_id': int(i),
                'size': int(mask.sum()),
                'avg_recency': float(segment_data['recency_days'].mean()),
                'avg_frequency': float(segment_data['frequency'].mean()),
                'avg_spent': float(segment_data['total_spent'].mean()),
                'avg_transactions': float(segment_data['transaction_count'].mean())
            }
            segment_profiles.append(profile)
        
        # Save model
        self.save_models()
        
        results = {
            'n_clusters': n_clusters,
            'total_customers': len(X),
            'segment_profiles': segment_profiles,
            'inertia': float(self.segmentation_model.inertia_)
        }
        
        print(f"✓ Segmentation Model Trained - {n_clusters} Clusters")
        
        return results
    

    def _identify_new_with_potential(self, results: pd.DataFrame, customer_metrics: pd.DataFrame) -> pd.DataFrame:
        """
        Identify new customers with high potential
        Overrides ML clustering for customers who are both new AND showing potential
        
        Criteria:
        - New: customer_age_days < 90
        - Potential: frequency > 0.5 OR total_spent > 100000 OR transaction_count > 5
        - Active: recency_days < 30
        """
        # Merge with customer metrics to get the features
        merged = results.merge(
            customer_metrics[[
                'motorcyclist_id', 
                'customer_age_days', 
                'frequency', 
                'total_spent', 
                'transaction_count',
                'recency_days'
            ]], 
            on='motorcyclist_id',
            how='left'
        )
        
        # Define "New" - joined in last 90 days
        is_new = merged['customer_age_days'] < 90
        
        # Define "Potential" - showing high-value behavior
        has_potential = (
            (merged['frequency'] > 0.5) |  # Frequent transactions
            (merged['total_spent'] > 100000) |  # Good spender
            (merged['transaction_count'] > 5)  # Multiple transactions
        )
        
        # Must also be active recently
        is_active = merged['recency_days'] < 30
        
        # Combine criteria
        new_with_potential = is_new & has_potential & is_active
        
        # Override segment name for these customers
        merged.loc[new_with_potential, 'segment_name'] = 'New Customers'
        
        # For old "New Customers" who don't meet criteria, reclassify
        old_fake_new = (merged['segment_name'] == 'New Customers') & ~new_with_potential
        
        # Reclassify based on their actual behavior
        # Old + low activity = Dormant/Occasional
        merged.loc[old_fake_new & (merged['customer_age_days'] >= 90), 'segment_name'] = 'Occasional Users'
        
        print(f"   ✓ Identified {new_with_potential.sum()} New Customers with Potential")
        
        return merged[results.columns]

    def predict_segments(self, customer_metrics: pd.DataFrame) -> pd.DataFrame:
        """Predict customer segments
        
        Args:
            customer_metrics: Customer metrics dataframe
            
        Returns:
            DataFrame with segment assignments
        """
        if self.segmentation_model is None:
            raise ValueError("Segmentation model not trained. Train model first.")
        
        # Prepare features
        X, _ = self.prepare_features(customer_metrics)
        X_scaled = self.segmentation_scaler.transform(X)
        
        # Predict
        segments = self.segmentation_model.predict(X_scaled)
        
        # Create results dataframe
        results = customer_metrics[['motorcyclist_id']].copy()
        results['ml_segment'] = segments
        results['segment_name'] = results['ml_segment'].map({
            0: 'Lost',
            1: 'Dormant',
            2: 'Premium VIPs',
            3: 'At Risk',
            4: 'Occasional Users',
            5: 'Loyal Regulars',
            6: 'Growth Potential',
            7: 'New Customers'           
            # 0: 'VIP Customers',
            # 1: 'Frequent Buyers',
            # 2: 'New Customers',
            # 3: 'Dormant',
            # 4: 'Regular Customers'
        })
        
        # Post-process: Identify "New Customers with Potential"
        # Rule-based overlay on ML segments
        results = self._identify_new_with_potential(results, customer_metrics)

        return results
    
    def train_anomaly_detector(self, transaction_features: pd.DataFrame) -> Dict[str, Any]:
        """Train anomaly detection model
        
        Args:
            transaction_features: Transaction-level features
            
        Returns:
            Training results
        """
        print("Training Anomaly Detection Model...")
        
        # Select relevant features
        features = transaction_features[[
            'amount', 'liter', 'pump_price', 'hour',
            'day_of_week'
        ]].copy()
        
        # Handle missing values
        features = features.fillna(features.median())
        
        # Scale features
        features_scaled = self.anomaly_scaler.fit_transform(features)
        
        # Train Isolation Forest
        self.anomaly_model = IsolationForest(
            contamination=0.05,  # Expect 5% anomalies
            random_state=42,
            n_jobs=-1
        )
        
        predictions = self.anomaly_model.fit_predict(features_scaled)
        
        # Count anomalies
        n_anomalies = (predictions == -1).sum()
        anomaly_rate = n_anomalies / len(predictions)
        
        # Save model
        self.save_models()
        
        results = {
            'total_transactions': len(features),
            'anomalies_detected': int(n_anomalies),
            'anomaly_rate': float(anomaly_rate),
            'contamination': 0.05
        }
        
        print(f"✓ Anomaly Detector Trained - Found {n_anomalies} anomalies ({anomaly_rate:.2%})")
        
        return results
    
    def detect_anomalies(self, transaction_features: pd.DataFrame) -> pd.DataFrame:
        """Detect anomalous transactions
        
        Args:
            transaction_features: Transaction-level features
            
        Returns:
            DataFrame with anomaly predictions
        """
        if self.anomaly_model is None:
            raise ValueError("Anomaly model not trained. Train model first.")
        
        # Select and prepare features
        features = transaction_features[[
            'amount', 'liter', 'pump_price', 'hour',
            'day_of_week'
        ]].copy()
        
        features = features.fillna(features.median())
        features_scaled = self.anomaly_scaler.transform(features)
        
        # Predict
        predictions = self.anomaly_model.predict(features_scaled)
        scores = self.anomaly_model.score_samples(features_scaled)
        
        # Create results dataframe
        results = transaction_features[['id']].copy()
        results['is_anomaly'] = (predictions == -1)
        results['anomaly_score'] = scores
        results['risk_level'] = pd.cut(
            scores,
            bins=[-np.inf, -0.5, -0.2, np.inf],
            labels=['High Risk', 'Medium Risk', 'Normal']
        )
        
        return results
    
    def save_models(self):
        """Save all trained models to disk"""
        models = {
            'churn_model': self.churn_model,
            'revenue_model': self.revenue_model,
            'segmentation_model': self.segmentation_model,
            'anomaly_model': self.anomaly_model,
            'churn_scaler': self.churn_scaler,
            'revenue_scaler': self.revenue_scaler,
            'segmentation_scaler': self.segmentation_scaler,
            'anomaly_scaler': self.anomaly_scaler,
            'metadata': self.metadata
        }
        
        model_path = self.model_dir / 'ml_models.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(models, f)
        
        # Save metadata as JSON
        metadata_path = self.model_dir / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        print(f"✓ Models saved to {self.model_dir}")
    
    def load_models(self):
        """Load trained models from disk"""
        model_path = self.model_dir / 'ml_models.pkl'
        
        if model_path.exists():
            try:
                with open(model_path, 'rb') as f:
                    models = pickle.load(f)
                
                self.churn_model = models.get('churn_model')
                self.revenue_model = models.get('revenue_model')
                self.segmentation_model = models.get('segmentation_model')
                self.anomaly_model = models.get('anomaly_model')
                self.churn_scaler = models.get('churn_scaler', StandardScaler())
                self.revenue_scaler = models.get('revenue_scaler', StandardScaler())
                self.segmentation_scaler = models.get('segmentation_scaler', StandardScaler())
                self.anomaly_scaler = models.get('anomaly_scaler', StandardScaler())
                self.metadata = models.get('metadata', {})
                
                print(f"✓ Models loaded from {self.model_dir}")
            except Exception as e:
                print(f"⚠ Could not load models: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about trained models
        
        Returns:
            Dictionary with model status and metadata
        """
        return {
            'churn_model_trained': self.churn_model is not None,
            'revenue_model_trained': self.revenue_model is not None,
            'segmentation_model_trained': self.segmentation_model is not None,
            'anomaly_model_trained': self.anomaly_model is not None,
            'metadata': self.metadata
        }


if __name__ == "__main__":
    print("ML Engine Module - Ready for import")
    print("=" * 60)
    print("Available Models:")
    print("  1. Churn Prediction (RandomForest)")
    print("  2. Revenue Forecasting (GradientBoosting)")
    print("  3. Customer Segmentation (KMeans)")
    print("  4. Anomaly Detection (IsolationForest)")
    print("=" * 60)
