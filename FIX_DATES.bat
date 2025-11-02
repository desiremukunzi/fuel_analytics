@echo off
echo ================================================================================
echo FIXING DATE RANGE ISSUES - COMPLETE SOLUTION
echo ================================================================================
echo.
echo This will fix both Charts and Anomalies date range issues
echo.
pause

echo.
echo Step 1: Fixing backend API...
echo ================================================================================
cd /d A:\MD\fuel
python fix_date_ranges.py

echo.
echo Step 2: Backend fixed! Now you need to:
echo ================================================================================
echo.
echo 1. Restart backend (in a new terminal):
echo    cd A:\MD\fuel
echo    python jalikoi_analytics_api_ml.py
echo.
echo 2. Check frontend files manually:
echo    - Open A:\MD\fuel_frontend\src\App.js
echo    - Find: useEffect(() =^> { fetchData(); }, [____])
echo    - Make sure [____] includes 'dateRange'
echo    - Should be: }, [dateRange])
echo.
echo 3. Restart frontend:
echo    cd A:\MD\fuel_frontend
echo    npm start
echo.
echo 4. Test by changing date ranges in browser
echo.
echo ================================================================================
echo READ: A:\MD\fuel\COMPLETE_DATE_FIX_GUIDE.md for detailed instructions
echo ================================================================================
echo.
pause
