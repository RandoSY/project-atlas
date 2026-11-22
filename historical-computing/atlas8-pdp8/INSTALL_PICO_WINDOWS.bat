@echo off
setlocal
cd /d "%~dp0"
echo ATLAS-8 Pico deployment (defaults to Chrome dashboard mode)
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0INSTALL_PICO.ps1" %*
set "rc=%ERRORLEVEL%"
echo.
if not "%rc%"=="0" echo Installer failed; read the message above. No reboot is proof of installation.
if "%rc%"=="0" echo Installer completed. See docs\PICO_DEPLOYMENT.md for next steps.
pause
exit /b %rc%
