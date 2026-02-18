@echo off
echo ========================================
echo   MoodSense AI - Quick Start
echo ========================================
echo.
echo Starting server...
echo.
echo The application will be available at:
echo   http://localhost:8000
echo.
echo Models will load on first use.
echo Press Ctrl+C to stop.
echo.
echo ========================================
echo.

uvicorn app_simple:app --host 0.0.0.0 --port 8000 --reload
