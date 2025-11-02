#!/usr/bin/env python3
"""
Machine Learning Models for Jalikoi Analytics
===============================================
Implements scikit-learn models for:
- Churn prediction
- Customer segmentation  
- Revenue forecasting
- Anomaly detection
"""

import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

class MLModelManager:
    """Manages all ML models for Jalikoi Analytics"""
    
    def __init__(self, models_dir='ml_models_trained'):
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        
        # Initialize models
        self.churn_model = None
        self.churn_scaler = None
        self.revenue_model = None
        self.revenue_scaler = None
        self.anomaly_detector = None
        self.segmentation_model = None
        self.segmentation_scaler = None
        
        # Model metadata
        self.churn_features = [
            'recency_days', 'frequency', 'total_spent', 'avg_transaction',
            'transaction_count', 'failure_rate', 'station_diversity', 'customer_age_days'
        ]
        
        self.revenue_features = [
            'recency_days', 'frequency', 'transaction_count', 'avg_transaction',
            'station_diversity', 'customer_age_days', 'failure_rate'
        ]
        
        self.segmentation_features = [
            'recency_days', 'frequency', 'total_spent', 'avg_transaction',
            'transaction_count', 'station_diversity'
        ]
        
        # Load existing models if available
        self.load_models()
    
    def prepare_churn_training_data(self, customer_metrics_df):
        """
        Prepare training data for churn prediction
        Label customers as churned if recency > 60 days
        """
        df = customer_metrics_df.copy()
        
        # Create churn label (1 = churned, 0 = active)
        df['is_churned'] = (df['recency_days'] > 60).astype(int)
        
        # Only use customers with enough history
        df = df[df['customer_age_days'] >= 30]
        
        # Extract features
        X = df[self.churn_features].fillna(0)
        y = df['is_churned']
        
        return X, y, df
    
    def train_churn_model(self, customer_metrics_df):
        """Train Random Forest model for churn prediction"""
        print("Training churn prediction model...")
        
        X, y, df = self.prepare_churn_training_data(customer_metrics_df)
        
        if len(X) < 50:
            print(f"Not enough data to train churn model (need 50+, have {len(X)})")
            return None
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        self.churn_scaler = StandardScaler()
        X_train_scaled = self.churn_scaler.fit_transform(X_train)
        X_test_scaled = self.churn_scaler.transform(X_test)
        
        # Train model
        self.churn_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.churn_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.churn_model.predict(X_test_scaled)
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1_score': f1_score(y_test, y_pred, zero_division=0),
            'n_samples': len(X),
            'churn_rate': y.mean()
        }
        
        print(f"Churn Model Trained - Accuracy: {metrics['accuracy']:.2%}, F1: {metrics['f1_score']:.2%}")
        
        # Save model
        self.save_model('churn_model', self.churn_model)
        self.save_model('churn_scaler', self.churn_scaler)
        
        return metrics
    
    def predict_churn(self, customer_metrics_df):
        """Predict churn probability for customers"""
        if self.churn_model is None or self.churn_scaler is None:
            return self.fallback_churn_prediction(customer_metrics_df)
        
        df = customer_metrics_df.copy()
        X = df[self.churn_features].fillna(0)
        X_scaled = self.churn_scaler.transform(X)
        
        # Predict probabilities
        churn_probabilities = self.churn_model.predict_proba(X_scaled)[:, 1]
        churn_predictions = self.churn_model.predict(X_scaled)
        
        df['ml_churn_probability'] = churn_probabilities
        df['ml_churn_prediction'] = churn_predictions
        
        # Categorize risk
        df['ml_churn_risk'] = pd.cut(
            df['ml_churn_probability'],
            bins=[0, 0.3, 0.7, 1.0],
            labels=['Low Risk', 'Medium Risk', 'High Risk']
        )
        
        return df
    
    def fallback_churn_prediction(self, customer_metrics_df):
        """Fallback rule-based churn prediction"""
        df = customer_metrics_df.copy()
        df['ml_churn_probability'] = np.clip(df['recency_days'] / 90, 0, 1)
        df['ml_churn_prediction'] = (df['ml_churn_probability'] > 0.5).astype(int)
        df['ml_churn_risk'] = pd.cut(
            df['ml_churn_probability'],
            bins=[0, 0.3, 0.7, 1.0],
            labels=['Low Risk', 'Medium Risk', 'High Risk']
        )
        return df
    
    def predict_revenue(self, customer_metrics_df, months_ahead=6):
        """Predict future revenue"""
        df = customer_metrics_df.copy()
        days_ahead = months_ahead * 30
        
        df['ml_predicted_revenue_6m'] = df['avg_transaction'] * df['frequency'] * days_ahead
        
        if 'ml_churn_probability' in df.columns:
            retention = 1 - df['ml_churn_probability']
            df['ml_predicted_revenue_6m_adjusted'] = df['ml_predicted_revenue_6m'] * retention
        else:
            df['ml_predicted_revenue_6m_adjusted'] = df['ml_predicted_revenue_6m']
        
        return df
    
    def train_segmentation_model(self, customer_metrics_df, n_clusters=6):
        """Train K-Means for segmentation"""
        print("Training segmentation model...")
        
        df = customer_metrics_df.copy()
        X = df[self.segmentation_features].fillna(0)
        
        if len(X) < 50:
            print(f"Not enough data (need 50+, have {len(X)})")
            return None
        
        self.segmentation_scaler = StandardScaler()
        X_scaled = self.segmentation_scaler.fit_transform(X)
        
        self.segmentation_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = self.segmentation_model.fit_predict(X_scaled)
        
        df['ml_segment'] = cluster_labels
        cluster_profiles = df.groupby('ml_segment')[self.segmentation_features].mean()
        cluster_names = self.name_clusters(cluster_profiles)
        df['ml_segment_name'] = df['ml_segment'].map(cluster_names)
        
        print(f"Segmentation Model Trained - {n_clusters} clusters")
        
        self.save_model('segmentation_model', self.segmentation_model)
        self.save_model('segmentation_scaler', self.segmentation_scaler)
        self.save_model('cluster_names', cluster_names)
        
        return {'n_clusters': n_clusters, 'cluster_names': cluster_names}
    
    def name_clusters(self, cluster_profiles):
        """Assign names to clusters"""
        names = {}
        for idx, row in cluster_profiles.iterrows():
            if row['total_spent'] > cluster_profiles['total_spent'].quantile(0.75):
                names[idx] = "VIP Active" if row['recency_days'] < cluster_profiles['recency_days'].median() else "VIP At Risk"
            elif row['frequency'] > cluster_profiles['frequency'].quantile(0.75):
                names[idx] = "Frequent Buyers"
            elif row['transaction_count'] < cluster_profiles['transaction_count'].quantile(0.25):
                names[idx] = "New Customers"
            elif row['recency_days'] > cluster_profiles['recency_days'].quantile(0.75):
                names[idx] = "Dormant"
            else:
                names[idx] = "Regular Customers"
        return names
    
    def predict_segments(self, customer_metrics_df):
        """Predict segments"""
        if self.segmentation_model is None:
            return customer_metrics_df
        
        df = customer_metrics_df.copy()
        X = df[self.segmentation_features].fillna(0)
        X_scaled = self.segmentation_scaler.transform(X)
        
        df['ml_segment'] = self.segmentation_model.predict(X_scaled)
        
        cluster_names = self.load_model('cluster_names')
        if cluster_names:
            df['ml_segment_name'] = df['ml_segment'].map(cluster_names)
        
        return df
    
    def save_model(self, name, obj):
        """Save model to disk"""
        filepath = os.path.join(self.models_dir, f'{name}.pkl')
        with open(filepath, 'wb') as f:
            pickle.dump(obj, f)
    
    def load_model(self, name):
        """Load model from disk"""
        filepath = os.path.join(self.models_dir, f'{name}.pkl')
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        return None
    
    def load_models(self):
        """Load all models"""
        models = ['churn_model', 'churn_scaler', 'revenue_model', 'revenue_scaler',
                  'anomaly_detector', 'segmentation_model', 'segmentation_scaler']
        
        for model_name in models:
            model = self.load_model(model_name)
            if model:
                setattr(self, model_name, model)
                print(f"Loaded {model_name}")
    
    def get_model_status(self):
        """Get model status"""
        return {
            'churn_model': self.churn_model is not None,
            'revenue_model': self.revenue_model is not None,
            'segmentation_model': self.segmentation_model is not None,
            'anomaly_detector': self.anomaly_detector is not None
        }
