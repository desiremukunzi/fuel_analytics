#!/usr/bin/env python3
"""
Login API for Jalikoi Analytics
Credentials stored in .env file for security
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import secrets

# Load environment variables
load_dotenv()

app = FastAPI(title="Jalikoi Login API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get credentials from .env
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

print(f"✓ Loaded credentials from .env")
print(f"  Username: {ADMIN_USERNAME}")
print(f"  Password: {'*' * len(ADMIN_PASSWORD)}")


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[dict] = None


@app.post("/api/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Login endpoint
    
    Validates username and password from .env file
    Returns authentication token on success
    """
    # Constant-time comparison to prevent timing attacks
    correct_username = secrets.compare_digest(
        credentials.username.encode('utf-8'),
        ADMIN_USERNAME.encode('utf-8')
    )
    correct_password = secrets.compare_digest(
        credentials.password.encode('utf-8'),
        ADMIN_PASSWORD.encode('utf-8')
    )
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    # Generate authentication token
    token = secrets.token_urlsafe(32)
    
    return LoginResponse(
        success=True,
        message="Login successful",
        token=token,
        user={
            "username": credentials.username,
            "role": "admin",
            "login_time": datetime.now().isoformat()
        }
    )


@app.get("/api/verify-token")
async def verify_token(token: str):
    """
    Verify authentication token
    
    In production, implement proper JWT verification
    """
    if not token or len(token) < 10:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {
        "success": True,
        "valid": True,
        "message": "Token is valid"
    }


@app.post("/api/logout")
async def logout():
    """Logout endpoint"""
    return {
        "success": True,
        "message": "Logged out successfully"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Jalikoi Analytics Login API",
        "version": "1.0.0",
        "endpoints": {
            "login": "/api/login",
            "verify": "/api/verify-token",
            "logout": "/api/logout"
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("="*70)
    print("JALIKOI ANALYTICS - LOGIN API")
    print("="*70)
    print(f"\n📋 Configuration:")
    print(f"   Admin Username: {ADMIN_USERNAME}")
    print(f"   Admin Password: {'*' * len(ADMIN_PASSWORD)}")
    print(f"\n🔐 Credentials loaded from .env file")
    print("\n🌐 Starting server...")
    print("   Login API: http://localhost:8001")
    print("   API Docs: http://localhost:8001/docs")
    print("="*70)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8001)