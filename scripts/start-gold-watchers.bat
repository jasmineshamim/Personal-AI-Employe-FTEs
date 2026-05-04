@echo off
REM Start All Gold Tier Watchers
REM AI Employee - Gold Tier

echo ===============================================
echo   AI Employee - Gold Tier Watchers
echo ===============================================
echo.

set VAULT_PATH=%~1
if "%VAULT_PATH%"=="" set VAULT_PATH=AI_Employee_Vault

echo Vault: %VAULT_PATH%
echo.

REM Start File System Watcher
echo Starting File System Watcher...
start python scripts\filesystem_watcher.py %VAULT_PATH%
timeout /t 2 /nobreak >nul

REM Start Gmail Watcher
echo Starting Gmail Watcher...
start python scripts\gmail_watcher.py %VAULT_PATH%
timeout /t 2 /nobreak >nul

REM Start WhatsApp Watcher
echo Starting WhatsApp Watcher...
start python scripts\whatsapp_watcher.py %VAULT_PATH%
timeout /t 2 /nobreak >nul

REM Start Facebook Watcher
echo Starting Facebook & Instagram Watcher...
start python scripts\facebook_watcher.py %VAULT_PATH%
timeout /t 2 /nobreak >nul

REM Start Twitter Watcher
echo Starting Twitter Watcher...
start python scripts\twitter_watcher.py %VAULT_PATH%
timeout /t 2 /nobreak >nul

REM Start Odoo Watcher
echo Starting Odoo Watcher...
start python scripts\odoo_watcher.py %VAULT_PATH%
timeout /t 2 /nobreak >nul

echo.
echo ===============================================
echo   All watchers started!
echo ===============================================
echo.
echo To stop watchers, close the terminal windows.
echo.
