@echo off
setlocal enabledelayedexpansion

echo ================================================================================
echo                    Sigma's Toolkit Launcher - Setup/Repair
echo ================================================================================
echo.

:: Check if Python exists
if not exist "python\python.exe" (
    echo ERROR: Python installation missing
    echo Please run the main builder script again.
    pause
    exit /b 1
)

echo Checking and installing/updating dependencies...
"python\python.exe" -m pip install --upgrade pip
"python\python.exe" -m pip install PyQt5==5.15.9 --upgrade
"python\python.exe" -m pip install "importlib-metadata>=4.0.0" --upgrade

echo Setup complete
pause
