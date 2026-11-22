@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 pc_dashboard_server.py --mode sim --open
) else (
  python pc_dashboard_server.py --mode sim --open
)
if errorlevel 1 (
  echo.
  echo Dashboard could not start. Install Python 3 from python.org and try again.
  pause
)
