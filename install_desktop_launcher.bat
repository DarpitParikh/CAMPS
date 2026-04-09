@echo off
REM install_desktop_launcher.bat
REM Copies the project launcher to the current user's Desktop (and Public Desktop if run elevated)

setlocal enabledelayedexpansion
set SRC_DIR=%~dp0
set SRC=%SRC_DIR%run_examhall.bat

if not exist "%SRC%" (
  echo ERROR: run_examhall.bat not found in %SRC_DIR%
  echo Please place this installer in the project root where run_examhall.bat exists.
  pause
  exit /b 1
)

set DEST=%USERPROFILE%\Desktop\Run Examhall.bat
echo Copying launcher to %DEST%...
copy /Y "%SRC%" "%DEST%" >nul
if %ERRORLEVEL% neq 0 (
  echo Failed to copy launcher to %DEST%
  pause
  exit /b 1
)

echo Launcher copied to your Desktop at %DEST%

REM If running as admin, also copy to Public Desktop so all users see it
whoami /groups | findstr /I "S-1-5-32-544" >nul
if %ERRORLEVEL% EQU 0 (
  if exist "%PUBLIC%" (
    set DESTALL=%PUBLIC%\Desktop\Run Examhall (All Users).bat
    echo Copying launcher to %DESTALL%...
    copy /Y "%SRC%" "%DESTALL%" >nul
    if %ERRORLEVEL% EQU 0 echo Launcher also copied to %DESTALL%
  )
)

echo Done. Double-click the desktop icon to start the project.
pause
