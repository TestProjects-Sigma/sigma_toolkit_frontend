@echo off 
setlocal 
 
:: Set the working directory to the script location 
cd /d "%~dp0" 
 
:: Check if Python exists 
if not exist "python\python.exe" ( 
    echo ERROR: Python not found Please run setup.bat first. 
    pause 
    exit /b 1 
) 
 
:: Launch Sigma's Toolkit Launcher 
echo Starting Sigma's Toolkit Launcher... 
"python\python.exe" -W ignore::DeprecationWarning "main.py" 2>nul 
 
:: Keep window open if there's an error 
if errorlevel 1 ( 
    echo. 
    echo An error occurred. Press any key to exit. 
    pause >nul 
) 
