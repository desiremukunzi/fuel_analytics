#!/usr/bin/env python3
"""
Patch Script: Add Liters to API Responses
==========================================
This script updates your API to include liter information in responses

Run this script to automatically patch your API files
"""

import os
import re

def backup_file(filepath):
    """Create backup of file before modifying"""
    backup_path = f"{filepath}.backup"
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Backed up {filepath} -> {backup_path}")
        return True
    return False


def add_liters_to_chatbot(filepath):
    """Add liters to Groq chatbot get_database_stats function"""
    
    if not os.path.exists(filepath):
        print(f"✗ File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to find get_database_stats function
    old_return = '''return {
        'total_revenue': float(df['amount'].sum()),
        'total_transactions': len(df),
        'total_customers': int(df['motorcyclist_id'].nunique()),
        'total_liters': float(df['liter'].sum()),
        'avg_transaction': float(df['amount'].mean()),
        'active_stations': int(df['station_id'].nunique()),
        'date_range': {'start': start_date, 'end': end_date}
    }'''
    
    new_return = '''return {
        'total_revenue': float(df['amount'].sum()),
        'total_transactions': len(df),
        'total_customers': int(df['motorcyclist_id'].nunique()),
        'total_liters': float(df['liter'].sum()),
        'avg_liters_per_transaction': float(df['liter'].mean()),
        'avg_transaction': float(df['amount'].mean()),
        'active_stations': int(df['station_id'].nunique()),
        'date_range': {'start': start_date, 'end': end_date}
    }'''
    
    if 'avg_liters_per_transaction' not in content:
        content = content.replace(old_return, new_return)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Added liters to chatbot in {filepath}")
        return True
    else:
        print(f"⊙ Liters already present in chatbot")
        return False


def add_login_to_main_api(filepath):
    """Add login endpoint to main API"""
    
    if not os.path.exists(filepath):
        print(f"✗ File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if login already exists
    if '@app.post("/api/login")' in content:
        print(f"⊙ Login endpoint already exists in {filepath}")
        return False
    
    # Add login endpoint before the root endpoint
    login_code = '''

# ============================================================================
# LOGIN ENDPOINT
# ============================================================================

@app.post("/api/login")
async def login(credentials: dict):
    """
    Login endpoint - validates credentials from .env
    """
    import secrets
    
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    username = credentials.get('username', '')
    password = credentials.get('password', '')
    
    # Constant-time comparison to prevent timing attacks
    correct_username = secrets.compare_digest(
        username.encode('utf-8'),
        ADMIN_USERNAME.encode('utf-8')
    )
    correct_password = secrets.compare_digest(
        password.encode('utf-8'),
        ADMIN_PASSWORD.encode('utf-8')
    )
    
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Generate token
    token = secrets.token_urlsafe(32)
    
    return {
        "success": True,
        "message": "Login successful",
        "token": token,
        "user": {
            "username": username,
            "role": "admin",
            "login_time": datetime.now().isoformat()
        }
    }


'''
    
    # Insert before root endpoint
    content = content.replace('# Update root endpoint\n@app.get("/")', 
                             login_code + '# Update root endpoint\n@app.get("/")')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Added login endpoint to {filepath}")
    return True


def main():
    """Main patch function"""
    print("="*70)
    print("JALIKOI ANALYTICS - API PATCHER")
    print("Adding Liters & Login to .env")
    print("="*70)
    print()
    
    # Files to patch
    main_api = "jalikoi_analytics_api_ml.py"
    
    # Create backups
    print("📦 Creating backups...")
    backup_file(main_api)
    print()
    
    # Apply patches
    print("🔧 Applying patches...")
    add_liters_to_chatbot(main_api)
    add_login_to_main_api(main_api)
    print()
    
    print("="*70)
    print("✅ PATCHING COMPLETE!")
    print("="*70)
    print()
    print("📝 Next steps:")
    print("   1. Update your .env file with:")
    print("      ADMIN_USERNAME=admin")
    print("      ADMIN_PASSWORD=YourSecurePassword123!")
    print()
    print("   2. Restart your API:")
    print("      python jalikoi_analytics_api_ml.py")
    print()
    print("   3. Test the changes:")
    print("      - Check /api/insights for liters")
    print("      - Test /api/login endpoint")
    print()
    print("💡 Backups saved with .backup extension")
    print("="*70)


if __name__ == "__main__":
    main()