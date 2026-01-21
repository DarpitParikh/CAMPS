@echo off
REM Quick Start Guide for Academic Management System (Windows)

echo ===================================================
echo LDRP Academic Management System - Quick Start
echo ===================================================
echo.

REM Check Python version
echo Checking Python installation...
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install django pandas openpyxl reportlab

REM Run migrations
echo Running migrations...
python manage.py migrate

REM Create superuser if database is fresh
echo.
echo ===================================================
echo SETUP COMPLETE!
echo ===================================================
echo.
echo To create admin account (superuser):
echo python manage.py createsuperuser
echo.
echo To start development server:
echo python manage.py runserver
echo.
echo Then visit: http://127.0.0.1:8000/
echo Admin:    http://127.0.0.1:8000/admin/
echo.
pause
