# Saoriverse Console - Python 3.12 Launcher (PowerShell)
# This script starts Streamlit using Python 3.12

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Saoriverse Console - Python 3.12" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python 3.12 is available
try {
    $pythonVersion = py -3.12 --version 2>&1
    Write-Host "✓ Python 3.12 found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python 3.12 is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.12 first:" -ForegroundColor Yellow
    Write-Host "  winget install Python.Python.3.12" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Starting Streamlit with Python 3.12..." -ForegroundColor Green
Write-Host "Open http://localhost:8501 in your browser" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Launch Streamlit with Python 3.12
py -3.12 -m streamlit run app.py @args
