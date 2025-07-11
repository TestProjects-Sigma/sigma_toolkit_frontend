@echo off
setlocal enabledelayedexpansion

:: ================================================================================
:: Portable Sigma's Toolkit Launcher Builder
:: Creates a portable Python environment with all dependencies
:: ================================================================================

echo.
echo ================================================================================
echo                    Sigma's Toolkit Launcher - Portable Builder
echo ================================================================================
echo.

:: Configuration
set "PYTHON_VERSION=3.11.9"
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-embed-amd64.zip"
set "GET_PIP_URL=https://bootstrap.pypa.io/get-pip.py"
set "TOOLKIT_DIR=%~dp0SigmaToolkitPortable"
set "PYTHON_DIR=%TOOLKIT_DIR%\python"
set "SCRIPTS_DIR=%PYTHON_DIR%\Scripts"

:: Check if we're running from the correct directory
if not exist "main.py" (
    echo ERROR: main.py not found in current directory!
    echo Please run this script from the Sigma Toolkit directory.
    pause
    exit /b 1
)

echo Step 1: Creating directory structure...
if exist "%TOOLKIT_DIR%" (
    echo Removing existing portable directory...
    rmdir /s /q "%TOOLKIT_DIR%"
)
mkdir "%TOOLKIT_DIR%"
mkdir "%PYTHON_DIR%"

echo.
echo Step 2: Downloading Python %PYTHON_VERSION% (embedded version)...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%TOOLKIT_DIR%\python.zip'}"

if not exist "%TOOLKIT_DIR%\python.zip" (
    echo ERROR: Failed to download Python!
    pause
    exit /b 1
)

echo Step 3: Extracting Python...
powershell -Command "Expand-Archive -Path '%TOOLKIT_DIR%\python.zip' -DestinationPath '%PYTHON_DIR%' -Force"
del "%TOOLKIT_DIR%\python.zip"

echo.
echo Step 4: Configuring Python for pip support...
:: Enable site-packages in python311._pth
echo import site >> "%PYTHON_DIR%\python311._pth"

:: Download get-pip.py
echo Downloading pip installer...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%GET_PIP_URL%' -OutFile '%PYTHON_DIR%\get-pip.py'}"

if not exist "%PYTHON_DIR%\get-pip.py" (
    echo ERROR: Failed to download get-pip.py!
    pause
    exit /b 1
)

echo.
echo Step 5: Installing pip...
"%PYTHON_DIR%\python.exe" "%PYTHON_DIR%\get-pip.py" --no-warn-script-location

if not exist "%SCRIPTS_DIR%\pip.exe" (
    echo ERROR: pip installation failed!
    pause
    exit /b 1
)

echo.
echo Step 6: Installing PyQt5 and dependencies...
"%PYTHON_DIR%\python.exe" -m pip install PyQt5==5.15.9 --no-warn-script-location

:: Check for Python < 3.8 compatibility (though we're using 3.11)
"%PYTHON_DIR%\python.exe" -m pip install "importlib-metadata>=4.0.0" --no-warn-script-location

echo.
echo Step 7: Copying Sigma Toolkit files...
copy "main.py" "%TOOLKIT_DIR%\"
copy "README.md" "%TOOLKIT_DIR%\"
copy "requirements.txt" "%TOOLKIT_DIR%\"

:: Copy apps folder if it exists
if exist "apps" (
    echo Copying apps folder...
    xcopy "apps" "%TOOLKIT_DIR%\apps" /E /I /H /Y
) else (
    echo Creating apps folder...
    mkdir "%TOOLKIT_DIR%\apps"
    echo. > "%TOOLKIT_DIR%\apps\put here your python apps in subfolder and main.py file.txt"
)

:: Copy any existing settings
if exist "launcher_settings.json" (
    echo Copying existing settings...
    copy "launcher_settings.json" "%TOOLKIT_DIR%\"
)

if exist "requirements_cache.json" (
    echo Copying requirements cache...
    copy "requirements_cache.json" "%TOOLKIT_DIR%\"
)

echo.
echo Step 8: Creating launcher batch files...

:: Create main launcher
echo @echo off > "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo setlocal >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo. >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo :: Set the working directory to the script location >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo cd /d "%%~dp0" >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo. >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo :: Check if Python exists >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo if not exist "python\python.exe" ( >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo     echo ERROR: Python not found! Please run setup.bat first. >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo     pause >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo     exit /b 1 >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo ^) >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo. >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo :: Launch Sigma's Toolkit Launcher >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo echo Starting Sigma's Toolkit Launcher... >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo "python\python.exe" -W ignore::DeprecationWarning "main.py" 2^>nul >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo. >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo :: Keep window open if there's an error >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo if errorlevel 1 ( >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo     echo. >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo     echo An error occurred. Press any key to exit. >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo     pause ^>nul >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
echo ^) >> "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"

:: Create setup/repair batch file
(
echo @echo off
echo setlocal enabledelayedexpansion
echo.
echo echo ================================================================================
echo echo                    Sigma's Toolkit Launcher - Setup/Repair
echo echo ================================================================================
echo echo.
echo.
echo :: Check if Python exists
echo if not exist "python\python.exe" ^(
echo     echo ERROR: Python installation missing!
echo     echo Please run the main builder script again.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo Checking and installing/updating dependencies...
echo "python\python.exe" -m pip install --upgrade pip
echo "python\python.exe" -m pip install PyQt5==5.15.9 --upgrade
echo "python\python.exe" -m pip install "importlib-metadata>=4.0.0" --upgrade
echo.
echo echo Setup complete!
echo pause
) > "%TOOLKIT_DIR%\Setup_Repair.bat"

:: Create app installer helper
echo @echo off > "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo setlocal >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo. >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo echo ================================================================================ >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo echo                    Install App Requirements Helper >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo echo ================================================================================ >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo echo. >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo echo This will scan all apps and safely install their requirements. >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo echo WARNING: This will NOT downgrade existing packages to prevent conflicts. >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo echo. >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo. >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo if not exist "python\python.exe" ( >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo     echo ERROR: Python not found! Please run Setup_Repair.bat first. >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo     pause >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo     exit /b 1 >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo ^) >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo. >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo echo Scanning apps folder... >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo set "install_count=0" >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo set "skip_count=0" >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo set "error_count=0" >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo. >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo for /d %%%%i in (apps\*) do ( >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo     if exist "%%%%i\requirements.txt" ( >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo         echo. >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo         echo [%%%%~ni] Installing requirements... >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo         echo ---------------------------------------- >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo. >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo         REM Use --upgrade-strategy only-if-needed to prevent downgrades >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo         "python\python.exe" -m pip install -r "%%%%i\requirements.txt" --upgrade-strategy only-if-needed --no-warn-script-location >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo. >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo         if errorlevel 1 ( >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo             echo ERROR: Failed to install requirements for %%%%~ni >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo             set /a error_count+=1 >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo         ^) else ( >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo             echo SUCCESS: Requirements for %%%%~ni installed >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo             set /a install_count+=1 >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo         ^) >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo     ^) else ( >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo         echo [%%%%~ni] No requirements.txt found - skipping >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo         set /a skip_count+=1 >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo     ^) >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo ^) >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo. >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo echo. >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo echo ================================================================================ >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo echo                                SUMMARY >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo echo ================================================================================ >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo echo Apps processed: %%install_count%% >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo echo Apps skipped: %%skip_count%% >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo echo Errors: %%error_count%% >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo. >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo if %%error_count%% gtr 0 ( >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo     echo WARNING: Some apps had installation errors. Check output above. >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo ^) else ( >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo     echo All app requirements processed successfully! >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo ^) >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo echo ================================================================================ >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"
echo pause >> "%TOOLKIT_DIR%\Install_App_Requirements.bat"

:: Create Python shell launcher
echo @echo off > "%TOOLKIT_DIR%\Python_Shell.bat"
echo setlocal >> "%TOOLKIT_DIR%\Python_Shell.bat"
echo. >> "%TOOLKIT_DIR%\Python_Shell.bat"
echo :: Set the working directory to the script location >> "%TOOLKIT_DIR%\Python_Shell.bat"
echo cd /d "%%~dp0" >> "%TOOLKIT_DIR%\Python_Shell.bat"
echo. >> "%TOOLKIT_DIR%\Python_Shell.bat"
echo echo ================================================================================ >> "%TOOLKIT_DIR%\Python_Shell.bat"
echo echo                    Sigma's Toolkit - Python Shell >> "%TOOLKIT_DIR%\Python_Shell.bat"
echo echo ================================================================================ >> "%TOOLKIT_DIR%\Python_Shell.bat"
echo echo. >> "%TOOLKIT_DIR%\Python_Shell.bat"
echo echo Python environment ready. Type 'exit()' to quit. >> "%TOOLKIT_DIR%\Python_Shell.bat"
echo echo. >> "%TOOLKIT_DIR%\Python_Shell.bat"
echo. >> "%TOOLKIT_DIR%\Python_Shell.bat"
echo if not exist "python\python.exe" ( >> "%TOOLKIT_DIR%\Python_Shell.bat"
echo     echo ERROR: Python not found! Please run Setup_Repair.bat first. >> "%TOOLKIT_DIR%\Python_Shell.bat"
echo     pause >> "%TOOLKIT_DIR%\Python_Shell.bat"
echo     exit /b 1 >> "%TOOLKIT_DIR%\Python_Shell.bat"
echo ^) >> "%TOOLKIT_DIR%\Python_Shell.bat"
echo. >> "%TOOLKIT_DIR%\Python_Shell.bat"
echo "python\python.exe" >> "%TOOLKIT_DIR%\Python_Shell.bat"

:: Create info file
echo ================================================================================ > "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo                    Sigma's Toolkit Launcher - Portable Version >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo ================================================================================ >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo. >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo Version: Portable Python %PYTHON_VERSION% >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo Created: %date% %time% >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo. >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo FILES: >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo ------- >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo Launch_Sigma_Toolkit.bat    - Main launcher for the toolkit >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo Setup_Repair.bat           - Fix/reinstall dependencies >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo Install_App_Requirements.bat - Install requirements for all apps >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo Python_Shell.bat           - Open Python command prompt >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo main.py                    - Main toolkit application >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo README.md                  - Documentation >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo. >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo FOLDERS: >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo -------- >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo python\                    - Portable Python installation >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo apps\                      - Your Python applications >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo. >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo USAGE: >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo ------ >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo 1. Double-click 'Launch_Sigma_Toolkit.bat' to start the toolkit >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo 2. Add your Python apps to the 'apps' folder >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo 3. Use 'Setup_Repair.bat' if you encounter issues >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo 4. Use 'Install_App_Requirements.bat' to batch-install app dependencies >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo. >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo REQUIREMENTS: >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo ------------- >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo - Windows 7 or later >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo - No system Python installation required >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo - Approximately 150MB of disk space >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo. >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo This portable version can be moved to any location or USB drive. >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo All settings and apps will be preserved. >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo. >> "%TOOLKIT_DIR%\README_PORTABLE.txt"
echo ================================================================================ >> "%TOOLKIT_DIR%\README_PORTABLE.txt"

echo.
echo Step 9: Cleaning up temporary files...
if exist "%PYTHON_DIR%\get-pip.py" del "%PYTHON_DIR%\get-pip.py"

echo.
echo Step 10: Testing installation...
echo Testing Python installation...
"%PYTHON_DIR%\python.exe" --version
if errorlevel 1 (
    echo ERROR: Python test failed!
    pause
    exit /b 1
)

echo Testing PyQt5 installation...
"%PYTHON_DIR%\python.exe" -c "import PyQt5.QtWidgets; print('PyQt5 OK')"
if errorlevel 1 (
    echo ERROR: PyQt5 test failed!
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo                               BUILD COMPLETE!
echo ================================================================================
echo.
echo Portable Sigma's Toolkit Launcher has been created successfully!
echo.
echo Location: %TOOLKIT_DIR%
echo Size: ~150MB
echo.
echo TO USE:
echo 1. Navigate to: %TOOLKIT_DIR%
echo 2. Double-click: Launch_Sigma_Toolkit.bat
echo.
echo TO MOVE TO USB/OTHER LOCATION:
echo 1. Copy the entire 'SigmaToolkitPortable' folder
echo 2. Run Launch_Sigma_Toolkit.bat from the new location
echo.
echo TROUBLESHOOTING:
echo - If apps don't work: Run Setup_Repair.bat
echo - For app requirements: Run Install_App_Requirements.bat
echo - For Python access: Run Python_Shell.bat
echo.
echo The portable version is now ready to use!
echo ================================================================================
echo.

:: Offer to launch immediately
set /p launch="Would you like to launch the portable toolkit now? (y/n): "
if /i "!launch!"=="y" (
    echo.
    echo Launching Sigma's Toolkit Launcher...
    start "" "%TOOLKIT_DIR%\Launch_Sigma_Toolkit.bat"
)

echo.
echo Builder script complete. Press any key to exit.
pause >nul