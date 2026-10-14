@echo off
chcp 65001 > nul
echo ========================================================
echo  🚀 LinkedIn B2B Auto-Poster Preview Generator
echo ========================================================
echo.
.venv\Scripts\python.exe main.py --dry-run
echo.
pause
