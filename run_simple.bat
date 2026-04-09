@echo off
cd /d "%~dp0"
if exist "%~dp0venv\Scripts\python.exe" (
	"%~dp0venv\Scripts\python.exe" manage.py runserver 0.0.0.0:8000
) else if exist "%~dp0.venv\Scripts\python.exe" (
	"%~dp0.venv\Scripts\python.exe" manage.py runserver 0.0.0.0:8000
) else (
	echo No virtual environment found. Run launch_lab.bat first.
)
pause
