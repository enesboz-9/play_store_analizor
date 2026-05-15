@echo off
title GitHub Push (Git LFS)

cd /d "%~dp0"

:: ── Git LFS kurulu mu kontrol et ──────────────────────────────────────────
git lfs version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [HATA] Git LFS yuklu degil!
    echo Asagidaki adresten indirin ve yukleyin:
    echo   https://git-lfs.com
    echo Kurduktan sonra bu scripti tekrar calistirin.
    echo.
    pause
    exit /b 1
)

:: ── Repo baslat / remote ayarla ───────────────────────────────────────────
if not exist ".git" (
    git init
    git remote add origin https://github.com/enesboz-9/play_store_analizor.git
) else (
    git remote set-url origin https://github.com/enesboz-9/play_store_analizor.git
)

:: ── Git LFS'i etkinlestir ─────────────────────────────────────────────────
git lfs install

:: ── Buyuk dosyalari LFS ile takip et ─────────────────────────────────────
git lfs track "*.csv"
git lfs track "*.parquet"
git lfs track "*.zip"

:: ── .gitattributes'u sahneye al ───────────────────────────────────────────
git add .gitattributes

:: ── .gitignore ─────────────────────────────────────────────────────────────
if not exist ".gitignore" (
    echo __pycache__/ > .gitignore
    echo *.pyc >> .gitignore
    echo .env >> .gitignore
    echo venv/ >> .gitignore
)

:: ── Kalan dosyalari ekle ve push et ───────────────────────────────────────
git add .
git commit -m "update: yeni veri seti (Git LFS)"
git branch -M main
git push -u origin main

if %ERRORLEVEL% == 0 (
    echo.
    echo SUCCESS: https://github.com/enesboz-9/play_store_analizor
    echo.
    echo NOT: Depoyu klonlayacak kisiler icin:
    echo   git lfs install
    echo   git clone https://github.com/enesboz-9/play_store_analizor.git
) else (
    echo.
    echo FAILED - Asagidaki adimlari kontrol edin:
    echo   1. GitHub token gecerli mi?
    echo      github.com - Settings - Developer settings - Personal access tokens
    echo   2. GitHub hesabinda Git LFS etkin mi?
    echo      github.com - Settings - Billing - Git LFS
    echo   3. git lfs install komutunu calistirdiniz mi?
)

pause
