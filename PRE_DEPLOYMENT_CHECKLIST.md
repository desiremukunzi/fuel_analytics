# 📋 PRE-DEPLOYMENT CHECKLIST

Run this before pushing to GitHub!

## Backend Checklist

```bash
cd A:\MD\fuel

# 1. Verify .gitignore exists
type .gitignore

# 2. Check for sensitive files
git status

# ⚠️ CRITICAL: Ensure these are NOT listed:
# - db_config.py (should be ignored)
# - venv/ (should be ignored)
# - ml_models/*.pkl (should be ignored)

# 3. Verify db_config_template.py exists
type db_config_template.py

# 4. Update requirements.txt
pip freeze > requirements.txt

# 5. Test API locally
python jalikoi_analytics_api_ml.py
# Visit: http://localhost:8000/docs

# 6. Ready to commit!
git add .
git status  # Review what will be committed
```

## Frontend Checklist

```bash
cd A:\MD\fuel_frontend

# 1. Verify .gitignore exists
type .gitignore

# 2. Check for unnecessary files
git status

# ⚠️ Ensure these are NOT listed:
# - node_modules/ (should be ignored)
# - build/ (should be ignored)

# 3. Test build
npm run build

# 4. Test locally
npm start
# Visit: http://localhost:3000

# 5. Ready to commit!
git add .
git status
```

## Security Checks

### ✅ Files that SHOULD be in GitHub:
- [ ] .gitignore
- [ ] db_config_template.py
- [ ] requirements.txt
- [ ] package.json
- [ ] README.md
- [ ] All .py files (except db_config.py)
- [ ] All .js/.jsx files
- [ ] All .css files
- [ ] DEPLOYMENT_GUIDE.md

### ❌ Files that should NOT be in GitHub:
- [ ] db_config.py (NEVER!)
- [ ] venv/ or env/
- [ ] node_modules/
- [ ] ml_models/*.pkl
- [ ] __pycache__/
- [ ] *.log files
- [ ] .env files
- [ ] Backup files (*.backup*, *.bak)

## Quick Commands

### Initialize Git (Backend)
```bash
cd A:\MD\fuel
git init
git add .
git commit -m "Initial commit: Jalikoi Analytics Backend"
```

### Initialize Git (Frontend)
```bash
cd A:\MD\fuel_frontend
git init
git add .
git commit -m "Initial commit: Jalikoi Analytics Frontend"
```

### Create GitHub Repos

**On GitHub.com:**
1. Go to: https://github.com/new
2. Create two repos:
   - `jalikoi-analytics-backend` (Private recommended)
   - `jalikoi-analytics-frontend` (Can be Public if no sensitive data)

### Connect and Push (Backend)
```bash
cd A:\MD\fuel
git remote add origin https://github.com/YOUR_USERNAME/jalikoi-analytics-backend.git
git branch -M main
git push -u origin main
```

### Connect and Push (Frontend)
```bash
cd A:\MD\fuel_frontend
git remote add origin https://github.com/YOUR_USERNAME/jalikoi-analytics-frontend.git
git branch -M main
git push -u origin main
```

## Verification After Push

**Check on GitHub:**
1. Go to your repo
2. ✅ Verify `db_config_template.py` is there
3. ❌ Verify `db_config.py` is NOT there
4. ✅ Verify `requirements.txt` is there
5. ❌ Verify `venv/` is NOT there
6. ❌ Verify `ml_models/` is NOT there (or only .gitkeep)

## Common Issues

### "Still see db_config.py in git status"

```bash
# Remove from git cache
git rm --cached db_config.py

# Verify .gitignore includes it
echo db_config.py >> .gitignore

# Commit
git add .gitignore
git commit -m "Remove db_config.py from tracking"
git push
```

### "venv/ folder still showing"

```bash
# Remove from git cache
git rm -r --cached venv/

# Verify .gitignore
echo venv/ >> .gitignore

# Commit
git add .gitignore
git commit -m "Remove venv from tracking"
git push
```

### "Large files rejected"

```bash
# If ml_models were accidentally added:
git rm -r --cached ml_models/

# Update .gitignore
echo "ml_models/" >> .gitignore
echo "*.pkl" >> .gitignore

git add .gitignore
git commit -m "Remove ML models from tracking"
git push
```

## Environment Variables (Advanced)

For better security, use environment variables:

**Create .env file (will be ignored):**
```bash
# Backend .env
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database
```

**Update Python to use .env:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT')),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}
```

**Install python-dotenv:**
```bash
pip install python-dotenv
pip freeze > requirements.txt
```

---

## ✅ Ready for Deployment?

If all checks pass:
- ✅ .gitignore configured
- ✅ Sensitive files excluded
- ✅ Code pushed to GitHub
- ✅ No credentials in repo

**Proceed to:** DEPLOYMENT_GUIDE.md

---

**Remember: NEVER commit:**
- Passwords
- API keys
- Database credentials
- Private keys
- .env files

**Always use:**
- Template files
- Environment variables
- .gitignore
