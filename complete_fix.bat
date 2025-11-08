@echo off
echo ========================================
echo COMPLETE ML FIX - AUTOMATED
echo ========================================
echo.

cd /d A:\MD\fuel

echo Step 1: Stopping API (if running)...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *jalikoi*" 2>nul
timeout /t 2 >nul
echo   Done
echo.

echo Step 2: Retraining all ML models...
echo   This takes 5-10 minutes...
echo.
python retrain_all_models.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo ERROR: Model retraining failed!
    echo ========================================
    echo.
    echo Check the error above and fix it.
    echo Then run this script again.
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS: Models retrained!
echo ========================================
echo.

echo Step 3: Starting API...
echo.
echo API will start in a new window...
echo Don't close this window!
echo.

start "Jalikoi Analytics API" cmd /k "cd /d A:\MD\fuel && venv\Scripts\activate && python jalikoi_analytics_api_ml.py"

timeout /t 5 >nul

echo.
echo ========================================
echo COMPLETE!
echo ========================================
echo.
echo API is starting in the background.
echo Wait 10 seconds, then:
echo.
echo 1. Open browser: http://localhost:8000
echo 2. Go to Predictions tab
echo 3. Predictions should now work!
echo.
echo If still showing error:
echo   - Wait 30 seconds for API to fully load
echo   - Hard refresh browser (Ctrl+F5)
echo   - Check API window for any errors
echo.
pause
