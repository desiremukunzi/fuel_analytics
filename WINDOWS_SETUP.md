# 🪟 Windows Quick Start Guide
## Jalikoi Analytics Setup for A:\MD\fuel

---

## ⚡ 5-Minute Setup (CSV Mode)

### **Step 1: Verify Python**
Open Command Prompt (cmd) and run:
```cmd
python --version
```

**Should show:** Python 3.8 or higher

**If not installed:**
- Download from: https://www.python.org/downloads/
- During installation, check "Add Python to PATH"

---

### **Step 2: Navigate to Your Project**
```cmd
cd A:\MD\fuel
```

---

### **Step 3: Install Required Packages**
```cmd
pip install pandas numpy scikit-learn matplotlib seaborn openpyxl
```

**Wait 1-2 minutes for installation**

---

### **Step 4: Run Your First Analysis**
```cmd
python jalikoi_analytics_db.py
```

**Expected output:**
```
================================================================================
JALIKOI ANALYTICS - COMPLETE ANALYSIS
Currency: RWF (Rwandan Francs)
================================================================================

✅ Using CSV file data
📊 KEY METRICS:
   Total Revenue: 1,549,970 RWF
   Projected 6M: 872,314,985 RWF

✓ Revenue Dashboard created
✓ Customer Segmentation created
✓ CLV Analysis created
✓ Churn Analysis created

✅ Excel report saved: outputs/jalikoi_insights_rwf.xlsx

ANALYSIS COMPLETE!
```

---

### **Step 5: View Your Results**

Open File Explorer and navigate to:
```
A:\MD\fuel\outputs\
```

You'll find:
- **charts/** folder with 4 PNG visualizations
- **jalikoi_insights_rwf.xlsx** Excel report

**Double-click to open!**

---

## 🗄️ Database Setup (Optional - 10 Minutes)

### **Step 1: Install Database Packages**
```cmd
cd A:\MD\fuel
pip install mysql-connector-python pymysql sqlalchemy
```

---

### **Step 2: Create Configuration File**

In File Explorer:
1. Navigate to `A:\MD\fuel`
2. **Copy** `db_config_template.py`
3. **Paste** and rename to `db_config.py`

---

### **Step 3: Edit Configuration**

Right-click `db_config.py` → **Open with Notepad** (or VS Code)

Change these lines:
```python
DB_CONFIG = {
    'host': 'your-database-host.com',     # CHANGE THIS
    'port': 3306,
    'database': 'your_database_name',     # CHANGE THIS
    'user': 'your_username',              # CHANGE THIS
    'password': 'your_password',          # CHANGE THIS
    'charset': 'utf8mb4',
    'connect_timeout': 10,
    'use_ssl': False,
}

PAYMENTS_TABLE = 'payments'  # CHANGE if needed
```

**Example (Local MySQL):**
```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'jalikoi',
    'user': 'root',
    'password': 'mypassword',
    'charset': 'utf8mb4',
    'connect_timeout': 10,
    'use_ssl': False,
}

PAYMENTS_TABLE = 'payments'
```

**Save the file** (Ctrl+S)

---

### **Step 4: Test Database Connection**
```cmd
python database_connector.py
```

**If successful:**
```
✅ Connected to MySQL Server version 8.0.33
✅ Connected to database: jalikoi
✅ ALL TESTS PASSED!
```

**If failed:**
- Check host/username/password
- Verify MySQL is running
- Check firewall settings

---

### **Step 5: Run Analytics with Database**
```cmd
python jalikoi_analytics_db.py
```

**Now using live database data!**

---

## 📁 Your Folder Structure

```
A:\MD\fuel\
├── jalikoi_analytics_db.py          ← Main script
├── database_connector.py             ← Database module
├── db_config_template.py             ← Template
├── db_config.py                      ← YOUR credentials (create this)
├── payments.csv                      ← Sample data
├── outputs\
│   ├── charts\
│   │   ├── 01_revenue_dashboard.png
│   │   ├── 02_customer_segmentation.png
│   │   ├── 03_clv_analysis.png
│   │   └── 04_churn_analysis.png
│   └── jalikoi_insights_rwf.xlsx
└── README.md
```

---

## 🎯 Daily Workflow

### **Morning Routine (5 minutes):**

1. Open Command Prompt
2. Navigate to project:
   ```cmd
   cd A:\MD\fuel
   ```
3. Run analysis:
   ```cmd
   python jalikoi_analytics_db.py
   ```
4. Check `outputs\charts\` for insights
5. Open Excel report for details
6. Take action on high-risk customers!

---

## 🔧 Common Windows Issues

### **Issue 1: "Python is not recognized"**

**Solution:**
1. Find Python installation folder (usually `C:\Python39\`)
2. Add to PATH:
   - Right-click **This PC** → **Properties**
   - **Advanced system settings**
   - **Environment Variables**
   - Edit **Path** variable
   - Add: `C:\Python39\` and `C:\Python39\Scripts\`
   - Click **OK**
   - Restart Command Prompt

---

### **Issue 2: "pip is not recognized"**

**Solution:**
```cmd
python -m pip install pandas numpy
```

---

### **Issue 3: "Permission denied"**

**Solution:**
Run Command Prompt as **Administrator**:
- Right-click **Command Prompt**
- Select **Run as administrator**

---

### **Issue 4: Charts not appearing**

**Solution:**
```cmd
# Ensure matplotlib backend works
pip uninstall matplotlib
pip install matplotlib
```

---

### **Issue 5: "Module not found"**

**Solution:**
```cmd
# Install all packages at once
pip install pandas numpy scikit-learn matplotlib seaborn openpyxl mysql-connector-python pymysql sqlalchemy
```

---

## 🚀 Automation (Windows Task Scheduler)

### **Run Analytics Automatically Every Day:**

1. Open **Task Scheduler** (search in Start menu)
2. Click **Create Basic Task**
3. Name: "Jalikoi Daily Analytics"
4. Trigger: **Daily** at 8:00 AM
5. Action: **Start a program**
6. Program: `python`
7. Arguments: `jalikoi_analytics_db.py`
8. Start in: `A:\MD\fuel`
9. Click **Finish**

**Now analytics run automatically every morning!**

---

## 💡 Tips for Windows Users

### **Tip 1: Use PowerShell**
PowerShell is more powerful than CMD:
```powershell
# Right-click folder → "Open PowerShell here"
python jalikoi_analytics_db.py
```

### **Tip 2: Create Batch File**
Create `run_analytics.bat`:
```batch
@echo off
cd A:\MD\fuel
python jalikoi_analytics_db.py
pause
```

Double-click to run!

### **Tip 3: Desktop Shortcut**
1. Right-click `run_analytics.bat`
2. **Send to** → **Desktop (create shortcut)**
3. Click shortcut to run analytics anytime!

### **Tip 4: View Charts Quickly**
Create `view_results.bat`:
```batch
@echo off
cd A:\MD\fuel\outputs\charts
start 01_revenue_dashboard.png
start 02_customer_segmentation.png
start 03_clv_analysis.png
start 04_churn_analysis.png
```

---

## 📊 Opening Results

### **Excel Report:**
```cmd
cd A:\MD\fuel\outputs
start jalikoi_insights_rwf.xlsx
```

### **All Charts at Once:**
```cmd
cd A:\MD\fuel\outputs\charts
start .
```

(Opens folder, then double-click any PNG)

---

## ✅ Verification Checklist

```
□ Python 3.8+ installed and in PATH
□ Can navigate to A:\MD\fuel in CMD
□ Packages installed successfully
□ payments.csv exists in folder
□ Can run: python jalikoi_analytics_db.py
□ Charts appear in outputs\charts\
□ Excel file opens correctly
□ Understand the insights
```

---

## 🎓 Learning Resources

### **Command Prompt Basics:**
- `cd` = Change directory
- `dir` = List files
- `python script.py` = Run Python script
- `pip install package` = Install package

### **Useful Commands:**
```cmd
# Check Python version
python --version

# List installed packages
pip list

# Update pip
python -m pip install --upgrade pip

# Check if package installed
pip show pandas
```

---

## 📞 Quick Help

### **Test Everything Works:**
```cmd
cd A:\MD\fuel
python --version
python -c "import pandas; print('Pandas OK')"
python -c "import numpy; print('NumPy OK')"
python -c "import sklearn; print('Sklearn OK')"
python -c "import matplotlib; print('Matplotlib OK')"
python jalikoi_analytics_db.py
```

If all commands succeed, you're good to go! ✅

---

## 🎉 You're Ready!

Your Windows setup is complete!

**Next steps:**
1. Run your first analysis
2. Review the visualizations
3. Check the Excel report
4. Take action on insights
5. Set up daily automation

**Start now:**
```cmd
cd A:\MD\fuel
python jalikoi_analytics_db.py
```

---

**Platform:** Windows 10/11
**Location:** A:\MD\fuel
**Currency:** Rwandan Francs (RWF)
**Status:** Ready to Use ✅
