@echo off
REM Start File System Watcher - Bronze Tier
REM Usage: start-watcher.bat [vault_path]

setlocal enabledelayedexpansion

REM Set default vault path if not provided
if "%~1"=="" (
    set VAULT_PATH=%~dp0..\AI_Employee_Vault
) else (
    set VAULT_PATH=%~1
)

echo ============================================
echo AI Employee - File System Watcher
echo ============================================
echo Vault: %VAULT_PATH%
echo.
echo Watching for new files in /Inbox folder...
echo Press Ctrl+C to stop
echo.

cd /d "%~dp0"
python filesystem_watcher.py "%VAULT_PATH%"

endlocal
