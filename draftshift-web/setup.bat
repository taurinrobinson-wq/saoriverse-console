@echo off
REM Setup DraftShift Web UI for local development

echo.
echo 🚀 Setting up DraftShift Web UI...
echo.

REM Check for Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js not found. Please install Node.js 16+
    pause
    exit /b 1
)

REM Check for Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VER=%%i
for /f "tokens=*" %%i in ('python --version') do set PY_VER=%%i

echo ✓ Node.js %NODE_VER%
echo ✓ Python %PY_VER%

REM Install Node dependencies
echo.
echo 📦 Installing Node dependencies...
call npm install

if %ERRORLEVEL% NEQ 0 (
    echo ❌ npm install failed
    pause
    exit /b 1
)

REM Install Python dependencies
echo.
echo 📦 Installing Python dependencies...
pip install -r ..\requirements-backend.txt

if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  pip install had issues (may be ok if dependencies already installed)
)

echo.
echo ✅ Setup complete!
echo.
echo 📝 Next steps:
echo.
echo Terminal 1 - Start React dev server:
echo   npm run dev
echo.
echo Terminal 2 - Start FastAPI backend:
echo   python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
echo.
echo Then open browser to http://localhost:5173
echo.
pause
