@echo off
rem ============================================================
rem  StandardRobot++ Tool launcher (with console log)
rem  INFO/WARNING/ERROR logs are printed in this window.
rem ============================================================
setlocal
set "DIR=%~dp0"
set "PY=C:\Users\bbq25\anaconda3\python.exe"
if not exist "%PY%" set "PY=python"

if not exist "%DIR%StandardRobotppTool.py" (
    echo [ERROR] StandardRobotppTool.py not found
    pause
    exit /b 1
)

"%PY%" "%DIR%StandardRobotppTool.py" %*
pause
exit /b 0
