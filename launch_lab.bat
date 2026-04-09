@echo off
setlocal EnableExtensions

cd /d "%~dp0"
set "HOST=0.0.0.0"
set "PORT=8000"
set "LAN_IP="

echo ================================================
echo Academic Management System - Lab Launcher
echo ================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed or not available in PATH.
    echo Install Python 3.9+ and run this launcher again.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

python -c "import django, pandas, openpyxl" >nul 2>nul
if errorlevel 1 (
    echo Installing/updating dependencies in venv...
    if exist "requirements_clean.txt" (
        python -m pip install -r requirements_clean.txt
    ) else (
        python -m pip install -r requirements.txt
    )
    if errorlevel 1 (
        echo Failed to install dependencies.
        pause
        exit /b 1
    )
)

echo Applying migrations...
python manage.py migrate
if errorlevel 1 (
    echo Migration failed.
    pause
    exit /b 1
)

echo Clearing previous login sessions...
python manage.py shell -c "from django.contrib.sessions.models import Session; Session.objects.all().delete()"
if errorlevel 1 (
    echo Failed to clear previous sessions.
    pause
    exit /b 1
)

echo Starting Django server in a separate window...
start "ExamHall Server" cmd /k "cd /d ""%~dp0"" && call venv\Scripts\activate.bat && python manage.py runserver %HOST%:%PORT%"

echo Waiting for server startup...
timeout /t 3 /nobreak >nul

for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 ^| Where-Object { $_.IPAddress -notlike '127.*' -and $_.PrefixOrigin -ne 'WellKnown' } ^| Select-Object -First 1 -ExpandProperty IPAddress)"`) do set "LAN_IP=%%I"

start "" "http://127.0.0.1:%PORT%/"

echo.
echo Opened browser at http://127.0.0.1:%PORT%/
if defined LAN_IP (
    echo LAN access URL: http://%LAN_IP%:%PORT%/
    echo Open this URL from other PCs on the same network.
)
echo Keep the "ExamHall Server" window open while using the system.
exit /b 0
