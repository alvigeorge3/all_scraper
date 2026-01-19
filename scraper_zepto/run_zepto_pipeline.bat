@echo off
echo ==========================================
echo   Zepto Scraper - End to End Pipeline
echo ==========================================
echo.
echo [1/3] Starting Scraper (Parallel)...
python run_zepto_assortment_parallel.py
echo.
echo ==========================================
echo   Pipeline Completed
echo ==========================================
echo.
pause
