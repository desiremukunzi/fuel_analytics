@echo off
echo ================================================================================
echo           Installing Required Packages for Jalikoi Analytics
echo ================================================================================
echo.

cd /d A:\MD\fuel

echo Installing core packages...
pip install pandas numpy scikit-learn matplotlib seaborn openpyxl

echo.
echo ================================================================================
echo Installation complete!
echo.
echo To install database support (optional), run:
echo    pip install mysql-connector-python pymysql sqlalchemy
echo.
echo To run analytics, execute: run_analytics.bat
echo ================================================================================
pause
