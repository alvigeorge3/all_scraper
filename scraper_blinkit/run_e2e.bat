@echo off
echo ===================================================
echo   Blinkit End-to-End Scraper Pipeline
echo ===================================================
echo.
echo Starting process...

REM Check if python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    pause
    exit /b
)

REM Run the pipeline
python run_pipeline.py

echo.
echo ===================================================
if %errorlevel% equ 0 (
    echo   Process Completed Successfully
) else (
    echo   Process Failed
)
echo ===================================================
pause
