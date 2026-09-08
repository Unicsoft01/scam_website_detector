@echo off
setlocal EnableExtensions EnableDelayedExpansion
title  Scam Website Detector Setup

cd /d "%~dp0"

echo ============================================================
echo   SCAM WEBSITE DETECTOR INSTALLATION
echo   AUTOMATIC SETUP CHECK
echo ============================================================
echo.

if not exist "setup_check.py" (
    echo [ERROR] setup_check.py was not found.
    echo.
    echo Place this file in the project root beside app.py.
    echo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Project virtual environment was not found.
    echo.
    echo Double-click setup_windows.bat first.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%V in ('".venv\Scripts\python.exe" --version 2^>^&1') do set "VENVVER=%%V"

echo [INFO] Project virtual environment found.
echo [INFO] Virtual environment Python: !VENVVER!
echo.

echo !VENVVER! | findstr /b "3.11." >nul 2>&1
if errorlevel 1 (
    echo ============================================================
    echo   SETUP CHECK CANNOT CONTINUE
    echo ============================================================
    echo.
    echo [ERROR] The current .venv uses Python !VENVVER!.
    echo This project requires Python 3.11.x.
    echo.
    echo FIX:
    echo 1. Ensure Python 3.11 is installed.
    echo 2. Double-click setup_windows.bat.
    echo    It will replace the incompatible .venv automatically.
    echo.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" "setup_check.py"
set "CHECK_RESULT=!ERRORLEVEL!"

echo.
echo ============================================================

if "!CHECK_RESULT!"=="0" (
    echo   SETUP CHECK PASSED
    echo ============================================================
    echo.
    echo SYSTEM STATUS: READY
    echo The application is ready to run.
    echo.
    echo Next:
    echo Double-click run_system.bat
) else (
    echo   SETUP CHECK FAILED
    echo ============================================================
    echo.
    echo SYSTEM STATUS: NOT READY
    echo One or more critical setup problems were detected.
    echo Review every [FAIL] message above and correct the problem.
)

echo.
echo Press any key to close this window.
pause >nul
exit /b !CHECK_RESULT!
