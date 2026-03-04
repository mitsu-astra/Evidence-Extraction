@echo off
setlocal enabledelayedexpansion

REM ─────────────────────────────────────────────────────────────────────────────
REM  FORENSIC PLATFORM — ONE-TIME INSTALLER
REM  Run this ONCE on a fresh machine. It installs everything automatically:
REM    • WSL (Windows Subsystem for Linux)
REM    • Node.js (LTS)
REM    • Python 3.11 inside WSL
REM    • All Python packages (Flask, pytsk3, pyewf, etc.)
REM    • All npm packages
REM ─────────────────────────────────────────────────────────────────────────────

title FORENSIC PLATFORM — ONE-TIME INSTALLER

echo.
echo ╔════════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                                ║
echo ║             FORENSIC ANALYSIS PLATFORM — ONE-TIME INSTALLER                   ║
echo ║         This will install all required tools and dependencies.                ║
echo ║                                                                                ║
echo ╚════════════════════════════════════════════════════════════════════════════════╝
echo.

REM ── Auto-elevate to Administrator ────────────────────────────────────────────────
net session >nul 2>&1
if errorlevel 1 (
    echo  [INFO] Requesting Administrator privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

echo  [OK] Running as Administrator.
echo.

REM ── Resolve project directory ─────────────────────────────────────────────────────
cd /d "%~dp0"
set "PROJECT_WIN=%~dp0"
if "%PROJECT_WIN:~-1%"=="\" set "PROJECT_WIN=%PROJECT_WIN:~0,-1%"

REM ─────────────────────────────────────────────────────────────────────────────────
REM  STEP 1 — WSL
REM ─────────────────────────────────────────────────────────────────────────────────
echo ════════════════════════════════════════════════════════════════════════════════
echo  [1/4]  WSL (Windows Subsystem for Linux)
echo ════════════════════════════════════════════════════════════════════════════════
echo.

wsl echo ok >nul 2>&1
if errorlevel 1 (
    echo  WSL not found — installing now...
    echo  NOTE: Your PC will need to RESTART after WSL installs.
    echo  After restart, double-click INSTALL.bat again to continue.
    echo.
    wsl --install
    echo.
    echo ════════════════════════════════════════════════════════════════════════════════
    echo  WSL installation triggered. PLEASE RESTART YOUR PC.
    echo  After restart, run INSTALL.bat again.
    echo ════════════════════════════════════════════════════════════════════════════════
    pause
    exit /b 0
) else (
    echo  [OK] WSL is already installed and running.
)
echo.

REM Convert Windows path to WSL path
for /f "delims=" %%i in ('wsl wslpath "%PROJECT_WIN%"') do set "PROJECT_WSL=%%i"
echo  [OK] Project WSL path: %PROJECT_WSL%
echo.

REM ─────────────────────────────────────────────────────────────────────────────────
REM  STEP 2 — Node.js
REM ─────────────────────────────────────────────────────────────────────────────────
echo ════════════════════════════════════════════════════════════════════════════════
echo  [2/4]  Node.js (LTS)
echo ════════════════════════════════════════════════════════════════════════════════
echo.

where node >nul 2>&1
if errorlevel 1 (
    echo  Node.js not found — installing via winget...
    winget install --id OpenJS.NodeJS.LTS --silent --accept-source-agreements --accept-package-agreements
    if errorlevel 1 (
        echo.
        echo  [WARN] winget install failed. Please install Node.js manually:
        echo  https://nodejs.org/
        echo.
    ) else (
        echo  [OK] Node.js installed successfully.
        echo  NOTE: You may need to close and reopen this window for node to be in PATH.
    )
) else (
    for /f "tokens=*" %%v in ('node --version') do echo  [OK] Node.js %%v already installed.
)
echo.

REM ─────────────────────────────────────────────────────────────────────────────────
REM  STEP 3 — Linux / WSL environment (Python + pip packages)
REM ─────────────────────────────────────────────────────────────────────────────────
echo ════════════════════════════════════════════════════════════════════════════════
echo  [3/4]  Linux environment (Python 3.11 + Flask + pytsk3 + pyewf)
echo ════════════════════════════════════════════════════════════════════════════════
echo.
echo  Running setup_linux.sh inside WSL...
echo  This may take 3-5 minutes on first run.
echo.

REM Convert line endings and run the shell script inside WSL
wsl bash -c "cd '%PROJECT_WSL%' && sed -i 's/\r//' setup_linux.sh && chmod +x setup_linux.sh && bash setup_linux.sh"

if errorlevel 1 (
    echo.
    echo  [FAIL] Linux setup encountered an error.
    echo  Check the output above for details.
    echo.
    pause
    exit /b 1
)
echo.

REM ─────────────────────────────────────────────────────────────────────────────────
REM  STEP 4 — npm install (frontend packages)
REM ─────────────────────────────────────────────────────────────────────────────────
echo ════════════════════════════════════════════════════════════════════════════════
echo  [4/4]  Frontend packages (npm install)
echo ════════════════════════════════════════════════════════════════════════════════
echo.

if not exist "%PROJECT_WIN%\node_modules" (
    echo  Installing npm packages...
    npm install
    if errorlevel 1 (
        echo.
        echo  [FAIL] npm install failed.
        echo.
        pause
        exit /b 1
    )
    echo  [OK] npm packages installed.
) else (
    echo  [OK] node_modules already present — skipping.
)
echo.

REM ─────────────────────────────────────────────────────────────────────────────────
REM  ALL DONE
REM ─────────────────────────────────────────────────────────────────────────────────
echo.
echo ╔════════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                                ║
echo ║                     INSTALLATION COMPLETE!                                    ║
echo ║                                                                                ║
echo ║    Everything is installed. To start the app:                                 ║
echo ║                                                                                ║
echo ║       Double-click  START_WEB_APP.bat                                         ║
echo ║                                                                                ║
echo ╚════════════════════════════════════════════════════════════════════════════════╝
echo.
pause
