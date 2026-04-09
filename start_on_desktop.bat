@echo off
REM Shortcut wrapper to run the elevated LAN starter script
cd /d %~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_for_lan.ps1"
pause
