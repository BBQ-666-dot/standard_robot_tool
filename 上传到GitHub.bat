@echo off
rem ============================================================
rem  Upload this tool to your GitHub
rem  Step 1: create an EMPTY repo at https://github.com/new
rem          (name suggestion: standard_robot_tool, do NOT add README)
rem  Step 2: double-click this script and type the repo name
rem          (first time: a GitHub sign-in window will pop up)
rem ============================================================
setlocal
cd /d "%~dp0"
set "REPO=standard_robot_tool"
set /p INPUT=GitHub repo name [%REPO%]: 
if not "%INPUT%"=="" set "REPO=%INPUT%"
git remote remove github 2>nul
git remote add github "https://github.com/BBQ-666-dot/%REPO%.git"
git push -u github main
echo.
echo Done. Check: https://github.com/BBQ-666-dot/%REPO%
pause
