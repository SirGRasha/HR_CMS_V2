@echo off
echo ================================
echo   HR_CMS_V2 - Auto Git Update
echo ================================

REM تغییر مسیر به پوشه فعلی اسکریپت
cd /d %~dp0

echo.
echo 🔍 Checking Git status...
git status

echo.
echo ➕ Adding all changes...
git add .

echo.
echo 📝 Creating commit...
git commit -m "Auto update commit"

echo.
echo 🔄 Ensuring branch is MAIN...
git branch -M main

echo.
echo 🔗 Setting remote origin...
git remote remove origin 2>nul
git remote add origin https://github.com/SirGRasha/HR_CMS_V2.git

echo.
echo ⬇️ Pulling latest changes (if any)...
git pull origin main --allow-unrelated-histories

echo.
echo ⬆️ Pushing to GitHub...
git push -u origin main

echo.
echo ✅ Done! Project updated successfully.
pause
