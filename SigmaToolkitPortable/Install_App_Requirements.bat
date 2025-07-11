@echo off 
setlocal 
 
echo ================================================================================ 
echo                    Install App Requirements Helper 
echo ================================================================================ 
echo. 
echo This will scan all apps and safely install their requirements. 
echo WARNING: This will NOT downgrade existing packages to prevent conflicts. 
echo. 
 
if not exist "python\python.exe" ( 
    echo ERROR: Python not found Please run Setup_Repair.bat first. 
    pause 
    exit /b 1 
) 
 
echo Scanning apps folder... 
set "install_count=0" 
set "skip_count=0" 
set "error_count=0" 
 
for /d %%i in (apps\*) do ( 
    if exist "%%i\requirements.txt" ( 
        echo. 
        echo [%%~ni] Installing requirements... 
        echo ---------------------------------------- 
 
        REM Use --upgrade-strategy only-if-needed to prevent downgrades 
        "python\python.exe" -m pip install -r "%%i\requirements.txt" --upgrade-strategy only-if-needed --no-warn-script-location 
 
        if errorlevel 1 ( 
            echo ERROR: Failed to install requirements for %%~ni 
            set /a error_count+=1 
        ) else ( 
            echo SUCCESS: Requirements for %%~ni installed 
            set /a install_count+=1 
        ) 
    ) else ( 
        echo [%%~ni] No requirements.txt found - skipping 
        set /a skip_count+=1 
    ) 
) 
 
echo. 
echo ================================================================================ 
echo                                SUMMARY 
echo ================================================================================ 
echo Apps processed: %install_count% 
echo Apps skipped: %skip_count% 
echo Errors: %error_count% 
 
if %error_count% gtr 0 ( 
    echo WARNING: Some apps had installation errors. Check output above. 
) else ( 
    echo All app requirements processed successfully 
) 
echo ================================================================================ 
pause 
