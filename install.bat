@echo off
echo ========================================
echo   MoodSense AI - Installation Script
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo.
echo [2/4] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created successfully!
) else (
    echo Virtual environment already exists.
)

echo.
echo [3/4] Installing dependencies...
echo This may take several minutes...
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [4/4] Initializing database...
venv\Scripts\python.exe -c "from models.database import init_db; init_db(); print('Database initialized!')"

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo To start the application, run: start.bat
echo.
pause
