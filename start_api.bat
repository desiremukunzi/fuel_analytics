@echo off
REM Jalikoi Analytics API Startup Script
REM =====================================

echo ===============================================
echo JALIKOI ANALYTICS REST API
echo ===============================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found.
    echo Running with system Python...
)

echo.
echo Installing/Updating API dependencies...
pip install -r requirements_api.txt --quiet

echo.
echo ===============================================
echo Starting API Server...
echo ===============================================
echo.
echo API will be available at:
echo   - Base URL: http://localhost:8000
echo   - Documentation: http://localhost:8000/docs
echo   - Health Check: http://localhost:8000/api/health
echo.
echo Press Ctrl+C to stop the server
echo ===============================================
echo.

REM Start the API server
python -m uvicorn jalikoi_analytics_api:app --reload --host 0.0.0.0 --port 8000

pause
