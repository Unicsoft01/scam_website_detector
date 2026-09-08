@echo off
setlocal EnableExtensions EnableDelayedExpansion

title Scam Website Detector Setup

cd /d "%~dp0"

echo ==================================================
echo SCAM WEBSITE DETECTOR INSTALLATION
echo ==================================================
echo.


REM ==================================================
REM 1. FIND PYTHON 3.11
REM ==================================================

set "PY311="

where py >nul 2>&1

if not errorlevel 1 (
    py -3.11 --version >nul 2>&1

    if not errorlevel 1 (
        set "PY311=py -3.11"
    )
)


if not defined PY311 (

    where python >nul 2>&1

    if not errorlevel 1 (

        for /f "tokens=2" %%V in ('python --version 2^>^&1') do (
            set "PYVER=%%V"
        )

        echo !PYVER! | findstr /b "3.11." >nul 2>&1

        if not errorlevel 1 (
            set "PY311=python"
        )
    )
)


if not defined PY311 (

    echo [ERROR] Python 3.11 was not found.
    echo.
    echo This project requires Python 3.11.x.
    echo Install Python 3.11 and run this setup again.
    echo.

    pause
    exit /b 1
)


echo [PASS] Python 3.11 detected.

%PY311% --version

echo.



REM ==================================================
REM 2. CREATE / VERIFY VIRTUAL ENVIRONMENT
REM ==================================================

if exist ".venv\Scripts\python.exe" (

    for /f "tokens=2" %%V in (
        '".venv\Scripts\python.exe" --version 2^>^&1'
    ) do (
        set "VENVVER=%%V"
    )

    echo [INFO] Existing virtual environment: Python !VENVVER!

    echo !VENVVER! | findstr /b "3.11." >nul 2>&1

    if errorlevel 1 (

        echo [WARN] Existing .venv uses the wrong Python version.
        echo [INFO] Removing incompatible .venv...

        rmdir /s /q ".venv"

        if exist ".venv" (

            echo [ERROR] Could not remove the old .venv folder.
            echo Close VS Code terminals or Python processes using it.
            echo Then run this setup again.

            pause
            exit /b 1
        )
    )
    else (

        echo [PASS] Existing .venv uses Python 3.11.
    )
)


if not exist ".venv\Scripts\python.exe" (

    echo.
    echo [INFO] Creating Python 3.11 virtual environment...

    %PY311% -m venv ".venv"

    if errorlevel 1 (

        echo [ERROR] Virtual environment creation failed.
        echo.

        pause
        exit /b 1
    )

    echo [PASS] Virtual environment created.
)


for /f "tokens=2" %%V in (
    '".venv\Scripts\python.exe" --version 2^>^&1'
) do (
    set "VENVVER=%%V"
)


echo !VENVVER! | findstr /b "3.11." >nul 2>&1

if errorlevel 1 (

    echo [ERROR] .venv is using Python !VENVVER!
    echo Python 3.11 is required.

    pause
    exit /b 1
)


echo [PASS] Virtual environment verified: Python !VENVVER!

echo.



REM ==================================================
REM 3. CHECK REQUIREMENTS FILE
REM ==================================================

if not exist "requirements.txt" (

    echo [ERROR] requirements.txt was not found.
    echo.

    pause
    exit /b 1
)


REM ==================================================
REM 4. UPGRADE PACKAGING TOOLS
REM ==================================================

echo [INFO] Upgrading pip, setuptools and wheel...

".venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel

if errorlevel 1 (

    echo [ERROR] Could not upgrade Python packaging tools.
    echo Check the internet connection and try again.

    pause
    exit /b 1
)


echo.



REM ==================================================
REM 5. INSTALL PROJECT DEPENDENCIES
REM ==================================================

echo [INFO] Installing project dependencies...

".venv\Scripts\python.exe" -m pip install --no-cache-dir -r "requirements.txt"

if errorlevel 1 (

    echo.
    echo [ERROR] Dependency installation failed.
    echo Review the error above.

    pause
    exit /b 1
)


echo.
echo [PASS] Project dependencies installed.


REM ==================================================
REM 6. VERIFY CRITICAL PYTHON PACKAGES
REM ==================================================

echo.
echo [INFO] Verifying critical Python packages...

".venv\Scripts\python.exe" -c "import pydantic_settings, sqlalchemy, pymysql, playwright; print('[PASS] Core Python packages available.')"

if errorlevel 1 (

    echo.
    echo [ERROR] One or more critical packages are unavailable.
    echo.

    pause
    exit /b 1
)


REM ==================================================
REM 7. INSTALL PLAYWRIGHT CHROMIUM
REM ==================================================

echo.
echo [INFO] Installing Playwright Chromium...

".venv\Scripts\python.exe" -m playwright install chromium

if errorlevel 1 (

    echo.
    echo [ERROR] Playwright Chromium installation failed.
    echo Check your internet connection and try again.

    pause
    exit /b 1
)


echo.
echo [PASS] Playwright Chromium installed.


REM ==================================================
REM 8. RUN SYSTEM HEALTH CHECK
REM ==================================================

echo.
echo [INFO] Running system health check...

".venv\Scripts\python.exe" setup_check.py

if errorlevel 1 (

    echo.
    echo [ERROR] System health check failed.
    echo Review the failed checks above.

    pause
    exit /b 1
)


REM ==================================================
REM 9. SUCCESS
REM ==================================================

echo.
echo ==================================================
echo INSTALLATION COMPLETED SUCCESSFULLY
echo ==================================================
echo.
echo The Scam Website Detector is ready to use.
echo.
echo To start the application:
echo double-click run_application.bat
echo.

pause

endlocal