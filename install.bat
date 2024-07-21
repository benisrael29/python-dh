@echo off
setlocal

:: Variables
set PYTHON_VERSION=3.10.6
set PYTHON_INSTALLER=python-%PYTHON_VERSION%-amd64.exe
set DOWNLOAD_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/%PYTHON_INSTALLER%
set REQUIREMENTS_FILE=requirements.txt
set MAIN_SCRIPT=main.py

:: Download Python installer
echo Downloading Python %PYTHON_VERSION% installer...
powershell -Command "Invoke-WebRequest -Uri %DOWNLOAD_URL% -OutFile %PYTHON_INSTALLER%"

:: Install Python silently
echo Installing Python %PYTHON_VERSION%...
%PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1

:: Verify installation
echo Verifying Python installation...
python --version
if errorlevel 1 (
    echo Python installation failed.
    exit /b 1
)
pip --version
if errorlevel 1 (
    echo pip installation failed.
    exit /b 1
)

:: Install packages from requirements.txt
if exist %REQUIREMENTS_FILE% (
    echo Installing Python packages from %REQUIREMENTS_FILE%...
    pip install -r %REQUIREMENTS_FILE%
    if errorlevel 1 (
        echo Failed to install one or more packages from %REQUIREMENTS_FILE%.
        exit /b 1
    )
) else (
    echo %REQUIREMENTS_FILE% not found.
    exit /b 1
)

:: Run the main script
if exist %MAIN_SCRIPT% (
    echo Running the main script %MAIN_SCRIPT%...
    python %MAIN_SCRIPT%
    if errorlevel 1 (
        echo Failed to run %MAIN_SCRIPT%.
        exit /b 1
    )
) else (
    echo %MAIN_SCRIPT% not found.
    exit /b 1
)

:: Clean up
del %PYTHON_INSTALLER%

echo Installation complete.
endlocal
pause
