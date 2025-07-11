@echo off 
setlocal 
 
:: Set the working directory to the script location 
cd /d "%~dp0" 
 
echo ================================================================================ 
echo                    Sigma's Toolkit - Python Shell 
echo ================================================================================ 
echo. 
echo Python environment ready. Type 'exit()' to quit. 
echo. 
 
if not exist "python\python.exe" ( 
    echo ERROR: Python not found Please run Setup_Repair.bat first. 
    pause 
    exit /b 1 
) 
 
"python\python.exe" 
