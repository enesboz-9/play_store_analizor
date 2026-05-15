@echo off
title GitHub Push

cd /d "%~dp0"

if not exist ".git" (
    git init
    git remote add origin https://github.com/enesboz-9/play_store_analizor.git
) else (
    git remote set-url origin https://github.com/enesboz-9/play_store_analizor.git
)

if not exist ".gitignore" (
    echo __pycache__/ > .gitignore
    echo *.pyc >> .gitignore
    echo .env >> .gitignore
    echo venv/ >> .gitignore
)

if not exist "README.md" (
    echo # AppVentures > README.md
    echo Streamlit dashboard for Google Play Store analysis. >> README.md
)

git add .
git commit -m "update"
git branch -M main
git push -u origin main

if %ERRORLEVEL% == 0 (
    echo.
    echo SUCCESS: https://github.com/enesboz-9/play_store_analizor
) else (
    echo.
    echo FAILED - Check your token.
    echo Get token: github.com - Settings - Developer settings - Personal access tokens
)

pause
