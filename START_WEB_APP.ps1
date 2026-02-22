# Forensic Web Application - PowerShell Startup Script
# This script sets up and runs the modern forensic analysis platform

Write-Host "`n╔════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                                ║" -ForegroundColor Cyan
Write-Host "║            FORENSIC ANALYSIS WEB APPLICATION - QUICK START                    ║" -ForegroundColor Cyan
Write-Host "║                      Modern Futuristic Platform                               ║" -ForegroundColor Cyan
Write-Host "║                                                                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "`nPlease install Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation`n" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Navigate to project directory
$projectPath = "D:\Forensics Application"
if (-not (Test-Path $projectPath)) {
    Write-Host "❌ ERROR: Cannot find directory: $projectPath" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Set-Location $projectPath
Write-Host "✓ Changed to project directory: $projectPath" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
$venvPath = Join-Path $projectPath ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "[1/4] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERROR: Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/4] Activating virtual environment..." -ForegroundColor Yellow
& "$venvPath\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

Write-Host ""
Write-Host "[3/4] Installing dependencies..." -ForegroundColor Yellow
Write-Host "(This may take 1-2 minutes on first run)" -ForegroundColor Cyan
Write-Host ""
pip install -r requirements_web.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERROR: Failed to install dependencies" -ForegroundColor Red
    Write-Host "`nIf pytsk3 failed, install Microsoft C++ Build Tools:" -ForegroundColor Yellow
    Write-Host "https://visualstudio.microsoft.com/downloads/`n" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green

Write-Host ""
Write-Host "[4/4] Starting Forensic Web Application..." -ForegroundColor Yellow
Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "✓ Web Application Starting..." -ForegroundColor Green
Write-Host ""
Write-Host "   🌐 Frontend: http://localhost:5000" -ForegroundColor Cyan
Write-Host "   📊 Backend:  Flask Server (localhost:5000)" -ForegroundColor Cyan
Write-Host "   📁 Reports:  D:\Forensics Application\analysis_output\" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Opening browser in 3 seconds..." -ForegroundColor Yellow
Write-Host ""

# Open browser
Start-Sleep -Seconds 3
Start-Process "http://localhost:5000"

# Start Flask app
Write-Host "════════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
python forensic_web_app.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ ERROR: Failed to start Flask application" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "- Port 5000 is already in use" -ForegroundColor Yellow
    Write-Host "- Flask not installed correctly" -ForegroundColor Yellow
    Write-Host "- Missing required files" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
}
