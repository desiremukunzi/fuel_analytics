@echo off
echo ========================================
echo COMPLETE FIX - ALL MODELS + CONSTRAINTS
echo ========================================
echo.

cd /d A:\MD\fuel

echo Step 1: Stopping API...
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul

echo Step 2: Deleting ALL old models...
rmdir /s /q ml_models 2>nul
mkdir ml_models
echo   Done
echo.

echo Step 3: Retraining ALL models with matching features...
echo   (This takes 5-10 minutes)
echo.
python retrain_all_models.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Retraining failed!
    pause
    exit /b 1
)

echo.
echo Step 4: Applying STRICT revenue constraints...
python fix_revenue_strict.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Revenue fix failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS!
echo ========================================
echo.
echo Now starting API...
start "Jalikoi API" cmd /k "cd /d A:\MD\fuel && venv\Scripts\activate && python jalikoi_analytics_api_ml.py"

timeout /t 5 >nul

echo.
echo API is starting...
echo Wait 30 seconds, then:
echo   1. Open browser
echo   2. Go to Predictions tab
echo   3. Hard refresh (Ctrl+F5)
echo.
pause
