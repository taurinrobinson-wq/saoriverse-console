@echo off
REM Saoriverse Console - Python 3.12 Launcher
REM This script starts Streamlit using Python 3.12

echo ========================================
echo Saoriverse Console - Python 3.12
echo ========================================
echo.

REM Check if Python 3.12 is available
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.12 is not installed or not in PATH
    echo.
    echo Please install Python 3.12 first:
    echo   winget install Python.Python.3.12
    echo.
    pause
    exit /b 1
)

echo ✓ Python 3.12 found
echo.
echo Starting Streamlit with Python 3.12...
echo Open http://localhost:8501 in your browser
echo Press Ctrl+C to stop
echo.

REM Launch Streamlit with Python 3.12
py -3.12 -m streamlit run app.py %*

pause
