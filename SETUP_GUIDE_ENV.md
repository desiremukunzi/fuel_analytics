# 🚀 Complete Setup Guide - Groq AI Chatbot

## ✅ What You Have

I've created these files for you:
- ✅ `.env` - Your environment variables file
- ✅ `.env.example` - Template for others
- ✅ `chatbot_groq_free.py` - Updated to load from .env
- ✅ `run_groq_chatbot.bat` - Easy runner

---

## 🎯 Quick Setup (3 Steps)

### Step 1: Install Required Packages (2 minutes)

```bash
pip install groq python-dotenv
```

**What these are:**
- `groq` - Groq API client (FREE AI)
- `python-dotenv` - Loads .env files automatically

---

### Step 2: Get FREE Groq API Key (2 minutes)

1. **Go to:** https://console.groq.com
2. **Click:** "Sign Up" (just email, no credit card!)
3. **Verify:** Check your email
4. **Create Key:** Click "API Keys" → "Create API Key"
5. **Copy:** Your key (starts with `gsk_`)

---

### Step 3: Add Key to .env File (1 minute)

**Open:** `A:\MD\fuel\.env`

**Replace this line:**
```
GROQ_API_KEY=your_groq_api_key_here
```

**With your actual key:**
```
GROQ_API_KEY=gsk_abc123xyz789...
```

**Save the file.**

---

## 🎉 Run the Chatbot!

### Option A: Use Batch File (Easy)
```cmd
run_groq_chatbot.bat
```

### Option B: Run Directly
```cmd
python chatbot_groq_free.py
```

---

## ✅ Expected Output

```
✓ Loaded environment variables from .env file
==================================================
🤖 GROQ AI CHATBOT - 100% FREE!
==================================================

Powered by Llama 3.1 70B (Meta's latest AI)
I can help you understand your Jalikoi Analytics data!

Try asking:
  • What's our total revenue?
  • Who are our top customers?
  • Show me station performance
  • What's the revenue trend?

Type 'exit' to quit

💬 You: _
```

---

## 💬 Example Usage

```
💬 You: What's our total revenue?

🤖 Thinking...
🔧 Calling: get_database_stats({'start_date': '2025-10-09', 'end_date': '2025-11-08'})

🤖 Assistant: Based on the last 30 days of data:

Your total revenue is 15,234,567 RWF from 3,456 transactions.

Key Metrics:
• Average Transaction: 4,405 RWF
• Active Customers: 1,234
• Active Stations: 8
• Total Fuel Sold: 45,678 liters

Would you like me to analyze trends or identify top customers?

💬 You: Yes, show me trends

🤖 Thinking...
🔧 Calling: get_revenue_trend({'days': 30})

🤖 Assistant: Here's your revenue trend analysis:

📈 Growth Pattern:
Your revenue has been trending upward over the past 30 days!
Average daily revenue: 507,819 RWF

Highlights:
• Best day: Nov 5th with 678,900 RWF
• Steady growth of ~2.1% per week
• Weekend sales are 15% higher than weekdays

This is a healthy growth trajectory! 🎯
```

---

## 📁 File Structure

```
A:\MD\fuel\
├── .env                    ← Your API key here
├── .env.example            ← Template for others
├── chatbot_groq_free.py    ← Main chatbot script
├── run_groq_chatbot.bat    ← Easy runner
└── SETUP_GUIDE_ENV.md      ← This file
```

---

## 🔒 Security Notes

### ⚠️ IMPORTANT: Protect Your .env File!

**DO:**
- ✅ Keep `.env` file private
- ✅ Add `.env` to `.gitignore`
- ✅ Never share your API key
- ✅ Use `.env.example` for templates

**DON'T:**
- ❌ Commit `.env` to Git
- ❌ Share `.env` file
- ❌ Put keys in code directly
- ❌ Upload `.env` anywhere

---

## 🔍 Verify Setup

### Check if .env is loaded:
```python
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Key found!' if os.getenv('GROQ_API_KEY') else 'Key not found')"
```

### Check if Groq works:
```python
python -c "from groq import Groq; import os; from dotenv import load_dotenv; load_dotenv(); print('✓ Groq connected!' if Groq(api_key=os.getenv('GROQ_API_KEY')) else '✗ Failed')"
```

---

## ❓ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'dotenv'"

**Solution:**
```bash
pip install python-dotenv
```

---

### Issue: "ModuleNotFoundError: No module named 'groq'"

**Solution:**
```bash
pip install groq
```

---

### Issue: "Set GROQ_API_KEY environment variable"

**Solutions:**

**A. Check .env file exists:**
```bash
dir .env
```

**B. Check .env has your key:**
```bash
type .env
```

Should show:
```
GROQ_API_KEY=gsk_your_actual_key_here
```

**C. Make sure key is correct:**
- Should start with `gsk_`
- No spaces around the `=`
- No quotes around the key

**D. Reinstall python-dotenv:**
```bash
pip install --upgrade python-dotenv
```

---

### Issue: ".env file not loading"

**Solution:**

**Option 1: Use system environment variable instead:**
```cmd
set GROQ_API_KEY=gsk_your_key_here
python chatbot_groq_free.py
```

**Option 2: Check file location:**
Make sure `.env` is in the same folder as `chatbot_groq_free.py`:
```
A:\MD\fuel\.env
A:\MD\fuel\chatbot_groq_free.py
```

---

### Issue: "Invalid API key"

**Solution:**
1. Go to https://console.groq.com
2. Check your API key
3. Create a new one if needed
4. Update `.env` file
5. Try again

---

## 🎓 How .env Works

### Before (Manual):
```cmd
set GROQ_API_KEY=gsk_abc123...
set DB_HOST=localhost
set DB_PORT=3306
python chatbot_groq_free.py
```

### After (Automatic with .env):
```cmd
python chatbot_groq_free.py
```

The script automatically:
1. Looks for `.env` file
2. Loads all variables
3. Makes them available to the script

**Much easier!** 🎉

---

## 📝 Example .env File

```bash
# Groq API Key (required)
GROQ_API_KEY=gsk_abc123xyz789example

# Database (optional - already in db_config.py)
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=mypassword
DB_NAME=jalikoi

# API Settings (optional)
API_PORT=8000
API_HOST=0.0.0.0
```

---

## 🚀 Next Steps

1. ✅ Install packages: `pip install groq python-dotenv`
2. ✅ Get API key: https://console.groq.com
3. ✅ Edit `.env` file with your key
4. ✅ Run: `python chatbot_groq_free.py`
5. ✅ Ask questions and enjoy!

---

## 💡 Tips

### Save API Key Permanently (Windows)

**For current session:**
```cmd
set GROQ_API_KEY=gsk_your_key
```

**Permanently (System):**
1. Press `Win + X` → System
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables" → Click "New"
5. Variable name: `GROQ_API_KEY`
6. Variable value: `gsk_your_key_here`
7. Click OK

**After this, you can run the chatbot anytime without setting the key!**

---

## 🎉 You're All Set!

Your chatbot is ready to use. Just:

1. Edit `.env` with your Groq API key
2. Run `python chatbot_groq_free.py`
3. Start chatting!

**Get your FREE key at: https://console.groq.com** 🚀

---

**Questions? Check the troubleshooting section above!**
