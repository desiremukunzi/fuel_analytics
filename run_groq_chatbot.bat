@echo off
echo ========================================
echo GROQ CHATBOT SETUP
echo ========================================
echo.

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found!
    echo.
    echo Creating .env from template...
    copy .env.example .env
    echo.
    echo Please edit .env file and add your Groq API key:
    echo 1. Go to: https://console.groq.com
    echo 2. Sign up (no credit card required)
    echo 3. Create API key
    echo 4. Open .env file and replace 'your_groq_api_key_here' with your key
    echo.
    pause
    notepad .env
    echo.
    echo After saving .env, run this script again.
    pause
    exit /b 1
)

REM Check if groq is installed
python -c "import groq" 2>nul
if errorlevel 1 (
    echo Step 1: Installing Groq library...
    pip install groq
    echo.
) else (
    echo Step 1: Groq library already installed ✓
    echo.
)

REM Check if python-dotenv is installed
python -c "import dotenv" 2>nul
if errorlevel 1 (
    echo Step 2: Installing python-dotenv...
    pip install python-dotenv
    echo.
) else (
    echo Step 2: python-dotenv already installed ✓
    echo.
)

echo Step 3: Running Groq Chatbot...
echo.
python chatbot_groq_free.py

pause
