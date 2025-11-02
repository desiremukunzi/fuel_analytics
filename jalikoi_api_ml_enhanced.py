#!/usr/bin/env python3
"""
Jalikoi Analytics ML-Enhanced REST API
========================================
Enhanced FastAPI with Machine Learning capabilities

NEW ML Endpoints:
- GET /api/ml/predictions - ML predictions for customers
- GET /api/ml/models/status - Model training status
- GET /api/ml/anomalies - Detect anomalous transactions
- GET /api/ml/insights-enhanced - Enhanced insights with ML

Run with: python jalikoi_api_ml_enhanced.py
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np

# Import original components
try:
    from database_connector import JalikoiDatabaseConnector
    from db_config import DB_CONFIG
    DATABASE_MODE = True
except ImportError:
    DATABASE_MODE = False

# Import ML components
try:
    from ml_models import MLModelManager
    ML_ENABLED = True
except ImportError:
    ML_ENABLED = False
    print("WARNING: ML models not available. Install scikit-learn: pip install scikit-learn --break-system-packages")

# Initialize FastAPI
app = FastAPI(
    title="Jalikoi Analytics ML-Enhanced API",
    description="REST API with Machine Learning for customer analytics",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML Manager
ml_manager = MLModelManager() if ML_ENABLED else None

def convert_to_native_types(obj):
    """Convert numpy/pandas types to native Python types"""
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_native_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native_types(item) for item in obj]
    elif pd.isna(obj):
        return None
    else:
        return obj

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Jalikoi Analytics ML-Enhanced API",
        "version": "2.0.0",
        "ml_enabled": ML_ENABLED,
        "endpoints": {
            "health": "/api/health",
            "ml_insights": "/api/ml/insights-enhanced",
            "ml_predictions": "/api/ml/predictions",
            "ml_models_status": "/api/ml/models/status",
            "docs": "/docs"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "database_available": DATABASE_MODE,
        "ml_enabled": ML_ENABLED,
        "models_loaded": ml_manager.get_model_status() if ml_manager else {},
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/ml/models/status")
async def ml_models_status():
    """Get ML models status"""
    if not ML_ENABLED:
        raise HTTPException(status_code=503, detail="ML not enabled. Install scikit-learn")
    
    status = ml_manager.get_model_status()
    
    return {
        "success": True,
        "ml_enabled": True,
        "models": status,
        "recommendation": "Run: python train_ml_models.py" if not all(status.values()) else "All models trained"
    }

if __name__ == "__main__":
    import uvicorn
    print("="*80)
    print("JALIKOI ANALYTICS ML-ENHANCED API")
    print("="*80)
    print(f"\nML Enabled: {ML_ENABLED}")
    if ml_manager:
        print(f"Models: {ml_manager.get_model_status()}")
    print("\nStarting server on http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("="*80)
    
    uvicorn.run("jalikoi_api_ml_enhanced:app", host="0.0.0.0", port=8000, reload=True)
