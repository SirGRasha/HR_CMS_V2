@echo off
setlocal EnableExtensions
title HR_CMS_V2 - Safe Git Update

echo.
echo ============================================================
echo          HR_CMS_V2 - SAFE GIT UPDATE
echo ============================================================
echo.

REM ============================================================
REM 1. Move to project root
REM ============================================================

cd /d "%~dp0"

echo [1/8] Project directory:
echo %CD%
echo.

REM ============================================================
REM 2. Check Git installation
REM ============================================================

echo [2/8] Checking Git installation...

git --version >nul 2>&1

if errorlevel 1 (
    echo.
    echo ERROR: Git is not installed or not available in PATH.
    echo.
    pause
    exit /b 1
)

git --version
echo.

REM ============================================================
REM 3. Check Git repository
REM ============================================================

echo [3/8] Checking Git repository...

if not exist ".git" (
    echo.
    echo ERROR: This folder is not a Git repository.
    echo.
    echo If this is the first time you are using Git here,
    echo initialize the repository manually first.
    echo.
    pause
    exit /b 1
)

echo Git repository detected.
echo.

REM ============================================================
REM 4. Ensure main branch
REM ============================================================

echo [4/8] Ensuring MAIN branch...

git branch -M main

echo Current branch:
git branch --show-current
echo.

REM ============================================================
REM 5. Configure GitHub remote
REM ============================================================

echo [5/8] Checking GitHub remote...

git remote get-url origin >nul 2>&1

if errorlevel 1 (
    echo Origin does not exist.
    echo Adding GitHub origin...
    git remote add origin https://github.com/SirGRasha/HR_CMS_V2.git
) else (
    echo Origin already exists.
    git remote set-url origin https://github.com/SirGRasha/HR_CMS_V2.git
)

echo.
echo Remote:
git remote -v
echo.

REM ============================================================
REM 6. Show current status
REM ============================================================

echo [6/8] Checking project changes...

git status --short

echo.
echo ============================================================
echo IMPORTANT:
echo The following types of files MUST NOT be uploaded:
echo.
echo   - .env
echo   - .venv
echo   - node_modules
echo   - *.sql
echo   - *.sqlite3
echo   - *.dump
echo   - *.backup
echo   - Python cache files
echo   - Frontend build files
echo   - local database files
echo ============================================================
echo.

REM ============================================================
REM 7. Add files
REM ============================================================

echo [7/8] Adding safe project files...

git add .

echo.
echo Files staged for commit:
echo ============================================================

git status --short

echo ============================================================
echo.

REM ============================================================
REM Check if there is anything to commit
REM ============================================================

git diff --cached --quiet

if not errorlevel 1 (
    echo.
    echo No new changes to commit.
    echo.
    goto PUSH
)

REM ============================================================
REM Commit
REM ============================================================

set "msg="

set /p "msg=Enter commit message (default: Update project): "

if "%msg%"=="" (
    set "msg=Update project"
)

echo.
echo Creating commit:
echo "%msg%"
echo.

git commit -m "%msg%"

if errorlevel 1 (
    echo.
    echo ERROR: Git commit failed.
    echo.
    pause
    exit /b 1
)

echo.
echo Commit created successfully.
echo.

REM ============================================================
REM 8. Pull and Push
REM ============================================================

:PUSH

echo [8/8] Synchronizing with GitHub...
echo.

echo Pulling latest changes from GitHub...
git pull --rebase origin main

if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: Git pull failed.
    echo ============================================================
    echo.
    echo No push was performed.
    echo Please check the Git conflict/status manually.
    echo.
    pause
    exit /b 1
)

echo.
echo Pushing project to GitHub...
echo.

git push -u origin main

if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: Git push failed.
    echo ============================================================
    echo.
    echo Possible causes:
    echo.
    echo 1. GitHub authentication problem
    echo 2. Internet connection problem
    echo 3. GitHub repository conflict
    echo 4. Permission problem
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo                 SUCCESS
echo ============================================================
echo.
echo HR_CMS_V2 has been successfully updated on GitHub.
echo.
echo Repository:
echo https://github.com/SirGRasha/HR_CMS_V2
echo.
echo IMPORTANT:
echo Database data / SQL files were excluded by .gitignore
echo only if they are listed there.
echo.
echo ============================================================
echo.

pause
exit /b 0