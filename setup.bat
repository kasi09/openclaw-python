@echo off
REM Quick start script for OpenClaw Python Skills (Windows)

echo Welcome to OpenClaw Python Skills!
echo Setting up environment...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python 3.9 or higher.
    exit /b 1
)

echo Python found: 
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Virtual environment activated

REM Install dependencies
echo Installing dependencies...
pip install -e ".[dev]"

echo.
echo Setup complete!
echo.
echo Try these commands:
echo - Run examples:  python example.py
echo - Run tests:     pytest tests/
echo - Format code:   black src tests
echo - Lint code:     ruff check src tests
echo - Type check:    mypy src
