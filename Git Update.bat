@echo off
title HR_CMS_V2 - Auto Git Update

echo ============================================
echo      HR_CMS_V2 - Auto Git Update Script
echo ============================================
echo.

REM تغییر مسیر به پوشه اسکریپت
cd /d %~dp0

echo 🔍 Checking Git installation...
git --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Git is not installed!
    pause
    exit /b
)

echo.
echo 🔍 Checking repository status...
git status

echo.
echo ➕ Adding all changes...
git add .

echo.
set /p msg=📝 Enter commit message (default: Auto update): 
if "%msg%"=="" set msg=Auto update

echo 📝 Creating commit: "%msg%"
git commit -m "%msg%"

echo.
echo 🔄 Ensuring branch is MAIN...
git branch -M main

echo.
echo 🔗 Setting remote origin...
git remote remove origin 2>nul
git remote add origin https://github.com/SirGRasha/HR_CMS_V2.git

echo.
echo ⬇️ Pulling latest changes from GitHub...
git pull origin main --allow-unrelated-histories

echo.
echo ⬆️ Pushing updates to GitHub...
git push -u origin main

echo.
echo ============================================
echo ✅ All done! Project successfully updated.
echo ============================================
pause
