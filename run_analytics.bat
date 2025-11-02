@echo off
echo ================================================================================
echo                    JALIKOI CUSTOMER ANALYTICS
echo                       Currency: RWF (Rwandan Francs)
echo ================================================================================
echo.

cd /d A:\MD\fuel
python jalikoi_analytics_db.py

echo.
echo ================================================================================
echo Press any key to exit...
pause >nul
