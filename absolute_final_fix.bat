@echo off
echo ========================================
echo ABSOLUTE FINAL FIX - FORCE CLEAN RELOAD
echo ========================================
echo.

cd /d A:\MD\fuel

echo Step 1: KILL ALL Python processes...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM pythonw.exe /T 2>nul
timeout /t 3 >nul
echo   Done
echo.

echo Step 2: Delete Python cache...
rmdir /s /q __pycache__ 2>nul
del /s /q *.pyc 2>nul
echo   Done
echo.

echo Step 3: Delete ALL old ML models...
rmdir /s /q ml_models 2>nul
mkdir ml_models
echo   Done
echo.

echo Step 4: Retrain ALL models from scratch...
echo   (Takes 5-10 minutes - DO NOT interrupt!)
echo.
python retrain_all_models.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo ERROR during retraining!
    echo ========================================
    pause
    exit /b 1
)

echo.
echo Step 5: Apply strict revenue constraints...
python fix_revenue_strict.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo ERROR during revenue fix!
    echo ========================================
    pause
    exit /b 1
)

echo.
echo Step 6: Verify models work...
python quick_test.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo ERROR: Models still broken!
    echo ========================================
    echo.
    echo Something is fundamentally wrong.
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo ALL MODELS VERIFIED WORKING!
echo ========================================
echo.

echo Step 7: Starting fresh API instance...
echo.
start "Jalikoi Analytics API - FRESH" cmd /k "cd /d A:\MD\fuel && venv\Scripts\activate && python jalikoi_analytics_api_ml.py"

timeout /t 10 >nul

echo.
echo ========================================
echo COMPLETE! API RUNNING WITH NEW MODELS
echo ========================================
echo.
echo IMPORTANT: 
echo   1. Wait 30 seconds for API to fully start
echo   2. Open browser in INCOGNITO/PRIVATE mode
echo   3. Go to: http://localhost:8000
echo   4. Test Predictions and Segments tabs
echo.
echo If still showing error, there may be an issue
echo with how the API loads models. Check the API
echo console window for errors.
echo.
pause
