@echo off
chcp 65001 >nul
title FORENSIC PLATFORM LAUNCHER

echo.
echo  ============================================================
echo   FORENSIC ANALYSIS PLATFORM - UNIFIED LAUNCHER
echo   Backend: Flask (WSL)  +  Frontend: Vite (Windows)
echo  ============================================================
echo.

REM ── Go to the folder where this .bat lives ───────────────────
cd /d "%~dp0"

REM ────────────────────────────────────────────────────────────
REM  STEP 1 - WSL check
REM ────────────────────────────────────────────────────────────
echo [1/4] Checking WSL...
wsl echo ok >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [FAIL] WSL not found.
    echo  Fix : Open PowerShell as Admin and run:  wsl --install
    echo  Then restart your PC and try again.
    echo.
    pause
    exit /b 1
)
echo  [OK] WSL is running.

REM Use PowerShell to write the WSL-format path to a temp file
powershell -NoProfile -Command ^
  "$p = '%~dp0'.TrimEnd('\'); $d = $p[0].ToString().ToLower(); $r = $p.Substring(2).Replace('\','/'); [IO.File]::WriteAllText('%TEMP%\__wslpath.txt', '/mnt/' + $d + $r)"
set /p PROJECT_WSL= < "%TEMP%\__wslpath.txt"
del "%TEMP%\__wslpath.txt" >nul 2>&1

echo  [OK] WSL project path: %PROJECT_WSL%
echo.

REM ────────────────────────────────────────────────────────────
REM  STEP 2 - Node.js check
REM ────────────────────────────────────────────────────────────
echo [2/4] Checking Node.js...
where node >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [FAIL] Node.js not found.
    echo  Download from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('node --version') do echo  [OK] Node.js %%v
echo.

REM ────────────────────────────────────────────────────────────
REM  STEP 3 - npm install (only if node_modules is missing)
REM ────────────────────────────────────────────────────────────
echo [3/4] Checking node_modules...
if not exist "node_modules\" (
    echo  node_modules missing - running npm install...
    npm install
    if errorlevel 1 (
        echo.
        echo  [FAIL] npm install failed. See errors above.
        echo.
        pause
        exit /b 1
    )
    echo  [OK] npm install done.
) else (
    echo  [OK] node_modules already present.
)
echo.

REM ────────────────────────────────────────────────────────────
REM  STEP 4 - Launch both services
REM ────────────────────────────────────────────────────────────
echo [4/4] Launching services...
echo.

echo  Starting Flask backend in WSL...
start "Flask Backend [WSL]" wsl bash -c "cd '%PROJECT_WSL%' && source venv_linux/bin/activate && python forensic_web_app.py; exec bash"

echo  Waiting 3 seconds before starting frontend...
timeout /t 3 /nobreak >nul

echo  Starting React/Vite frontend...
start "React Frontend [Windows]" cmd /k "npm run dev"

echo.
echo  ============================================================
echo   Both services launched:
echo     Flask backend  >>  http://localhost:5000
echo     Vite frontend  >>  http://localhost:5173
echo  ============================================================
echo.
echo  Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul
start http://localhost:5173

echo.
echo  Done! Close the Flask and Vite windows to stop the app.
echo.
pause
