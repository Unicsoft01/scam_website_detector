@echo off

title Scam Website Detector

cd /d "%~dp0"

echo ==========================================
echo SCAM WEBSITE DETECTOR
echo Okoroafor Stella
echo ==========================================
echo.

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.

echo Starting Scam Website Detector...

uvicorn app.main:app --reload


pause