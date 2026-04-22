@echo off
REM Windows Batch Script for Running Resume Generation Tests
REM This script sets up environment and runs the tests

setlocal enabledelayedexpansion

echo.
echo ========================================================================
echo  ROLEFIT BACKEND - RESUME GENERATION TEST SUITE
echo ========================================================================
echo.

REM Get the script directory
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

echo Project Root: %PROJECT_ROOT%
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and add it to your PATH
    pause
    exit /b 1
)

echo Python is installed
echo.

REM Activate virtual environment if it exists
if exist "%PROJECT_ROOT%\env\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "%PROJECT_ROOT%\env\Scripts\activate.bat"
) else (
    echo Note: Virtual environment not found at %PROJECT_ROOT%\env
    echo You may need to create one: python -m venv env
)

echo.
echo ========================================================================
echo  INSTALLATION CHECK
echo ========================================================================
echo.

REM Check if requests is installed
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r "%SCRIPT_DIR%test_requirements.txt"
) else (
    echo Required packages are already installed
)

echo.
echo ========================================================================
echo  RUNNING HEALTH CHECK
echo ========================================================================
echo.

REM Run health check
python "%SCRIPT_DIR%health_check.py"

if errorlevel 1 (
    echo.
    echo Health check failed. Please ensure the backend server is running:
    echo.
    echo   cd %PROJECT_ROOT%
    echo   python -m uvicorn main:app --reload
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo  SELECT TEST OPTION
echo ========================================================================
echo.
echo 1. Run default tests (3 users)
echo 2. Run with custom number of users
echo 3. Run health check only
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Running test suite with default settings...
    echo.
    python "%SCRIPT_DIR%test_resume_generation.py"
) else if "%choice%"=="2" (
    echo.
    set /p num_users="Enter number of users to test (default 3): "
    if "!num_users!"=="" set num_users=3
    echo Running test suite with !num_users! users...
    echo.
    python "%SCRIPT_DIR%test_runner.py" --users !num_users!
) else if "%choice%"=="3" (
    echo.
    echo Health check already completed above
    echo.
) else (
    echo Exiting...
    exit /b 0
)

echo.
echo ========================================================================
echo  TEST COMPLETE
echo ========================================================================
echo.
pause
