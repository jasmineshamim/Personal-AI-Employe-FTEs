@echo off
REM AI Employee Orchestrator - Bronze Tier
REM Usage: run-orchestrator.bat [vault_path] [--process]

setlocal enabledelayedexpansion

REM Set default vault path if not provided
if "%~1"=="" (
    set VAULT_PATH=%~dp0..\AI_Employee_Vault
) else (
    set VAULT_PATH=%~1
)

echo ============================================
echo AI Employee - Orchestrator
echo ============================================
echo Vault: %VAULT_PATH%
echo.

cd /d "%~dp0"

REM Check if --process flag is provided
if "%~2"=="--process" (
    echo Processing pending items...
    python orchestrator.py "%VAULT_PATH%" --process
) else if "%~2"=="--continuous" (
    echo Running in continuous mode...
    python orchestrator.py "%VAULT_PATH%" --continuous
) else (
    echo Showing status...
    python orchestrator.py "%VAULT_PATH%" --status
)

echo.
echo Done.

endlocal
