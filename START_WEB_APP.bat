@echo off
REM Forensic Web Application - Quick Start Script
REM This script sets up and runs the modern forensic analysis platform

echo.
echo ╔════════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                                ║
echo ║            FORENSIC ANALYSIS WEB APPLICATION - QUICK START                    ║
echo ║                      Modern Futuristic Platform                               ║
echo ║                                                                                ║
echo ╚════════════════════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✓ Python detected
echo.

REM Navigate to project directory
cd /d "D:\Forensics Application"
if errorlevel 1 (
    echo ❌ ERROR: Cannot navigate to D:\Forensics Application
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo [1/4] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

echo.
echo [2/4] Activating virtual environment...
call .venv\Scripts\Activate.bat
echo ✓ Virtual environment activated

echo.
echo [3/4] Installing dependencies...
echo (This may take 1-2 minutes on first run)
echo.
pip install -r requirements_web.txt --quiet
if errorlevel 1 (
    echo ❌ ERROR: Failed to install dependencies
    echo.
    echo If pytsk3 failed, install Microsoft C++ Build Tools:
    echo https://visualstudio.microsoft.com/downloads/
    echo.
    pause
    exit /b 1
)
echo ✓ Dependencies installed successfully

echo.
echo [4/4] Starting Forensic Web Application...
echo.
echo.
echo ════════════════════════════════════════════════════════════════════════════════
echo.
echo ✓ Web Application Starting...
echo.
echo   🌐 Frontend: http://localhost:5000
echo   📊 Backend:  Flask Server (localhost:5000)
echo   📁 Reports:  D:\Forensics Application\analysis_output\
echo.
echo   Opening browser in 3 seconds...
echo.
timeout /t 3 /nobreak

REM Open browser
start http://localhost:5000

REM Start Flask app
python forensic_web_app.py

if errorlevel 1 (
    echo.
    echo ❌ ERROR: Failed to start Flask application
    echo.
    echo Possible issues:
    echo - Port 5000 is already in use
    echo - Flask not installed correctly
    echo - Missing required files
    echo.
    pause
)
