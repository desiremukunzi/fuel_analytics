@echo off
echo ========================================
echo GITHUB PUSH - QUICK START
echo ========================================
echo.

cd /d A:\MD\fuel

echo Step 1: Checking .gitignore...
if exist .gitignore (
    echo   [OK] .gitignore exists
) else (
    echo   [ERROR] .gitignore missing!
    pause
    exit /b 1
)

echo Step 2: Checking db_config_template.py...
if exist db_config_template.py (
    echo   [OK] db_config_template.py exists
) else (
    echo   [ERROR] db_config_template.py missing!
    pause
    exit /b 1
)

echo Step 3: Checking if git is initialized...
if exist .git (
    echo   [OK] Git already initialized
) else (
    echo   Initializing git...
    git init
    echo   [OK] Git initialized
)

echo.
echo Step 4: Checking git status...
git status

echo.
echo ========================================
echo READY TO PUSH!
echo ========================================
echo.
echo IMPORTANT: Before pushing, verify:
echo   [  ] db_config.py is NOT listed above
echo   [  ] venv/ is NOT listed above
echo   [  ] ml_models/ is NOT listed above
echo.
echo If any of these are listed, STOP and fix .gitignore first!
echo.
set /p confirm="Continue with push? (y/n): "

if /i not "%confirm%"=="y" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo Step 5: Adding files...
git add .

echo.
echo Step 6: Committing...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" (
    set commit_msg=Initial commit: Jalikoi Analytics Platform
)
git commit -m "%commit_msg%"

echo.
echo Step 7: Setting up remote...
echo.
echo Go to GitHub and create a new repository named:
echo   jalikoi-analytics-backend
echo.
echo Then paste the repository URL below:
echo (Example: https://github.com/YOUR_USERNAME/jalikoi-analytics-backend.git)
echo.
set /p repo_url="Repository URL: "

if "%repo_url%"=="" (
    echo Error: Repository URL required
    pause
    exit /b 1
)

git remote remove origin 2>nul
git remote add origin %repo_url%

echo.
echo Step 8: Pushing to GitHub...
git branch -M main
git push -u origin main

echo.
echo ========================================
echo SUCCESS! Code pushed to GitHub
echo ========================================
echo.
echo Repository: %repo_url%
echo Branch: main
echo.
echo Next steps:
echo 1. Verify on GitHub that db_config.py is NOT there
echo 2. Follow DEPLOYMENT_GUIDE.md to deploy to server
echo.
pause
