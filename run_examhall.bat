@echo off
REM Wrapper to double-click and run the PowerShell launcher (keeps window open)
powershell -NoProfile -ExecutionPolicy Bypass -NoExit -Command "& 'E:\examhall\run_examhall.ps1'"
exit /b 0
