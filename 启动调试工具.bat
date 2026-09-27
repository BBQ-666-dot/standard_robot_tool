@echo off
rem ============================================================
rem  StandardRobot++ Tool launcher (no console window)
rem  Usage: double-click
rem         or with args, e.g.: launcher.bat --page debug --demo
rem ============================================================
setlocal
set "DIR=%~dp0"
set "PYW=C:\Users\bbq25\anaconda3\pythonw.exe"
if not exist "%PYW%" set "PYW=pythonw"

if not exist "%DIR%StandardRobotppTool.py" (
    echo [ERROR] StandardRobotppTool.py not found
    pause
    exit /b 1
)

start "" "%PYW%" "%DIR%StandardRobotppTool.py" %*
exit /b 0
