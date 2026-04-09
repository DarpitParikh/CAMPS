@echo off
echo ========================================
echo Exam Hall Management - First Time Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from python.org
    pause
    exit /b 1
)

echo Python found!
python --version
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
    echo.
) else (
    echo Virtual environment already exists.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo Installing dependencies...
echo This may take a few minutes...
echo.

if exist "requirements_clean.txt" (
    echo Installing from requirements_clean.txt (recommended)...
    pip install -r requirements_clean.txt
) else (
    echo Installing from requirements.txt...
    pip install -r requirements.txt
)

echo.
echo ========================================
echo Checking Django installation...
python manage.py check
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the server:
echo   1. For localhost only:    python manage.py runserver
echo   2. For LAN access:        launch_lab.bat
echo.
echo Database file (db.sqlite3) is already included.
echo.
pause
