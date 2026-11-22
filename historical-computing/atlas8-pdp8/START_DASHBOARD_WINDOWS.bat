@echo off
setlocal
cd /d "%~dp0"
title ATLAS-8 PDP-8 Dashboard

echo ATLAS-8 PDP-8 -- starting dedicated dashboard (default port 8878).
echo Other Project Atlas applications can keep running on their own ports.
echo.
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 pc_dashboard_server.py --mode sim --open
) else (
  python pc_dashboard_server.py --mode sim --open
)
if errorlevel 1 (
  echo.
  echo ATLAS-8 did not launch. Check the message above.
  echo Install Python 3 if needed; otherwise close the conflicting process.
  pause
)
