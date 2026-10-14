@echo off
chcp 65001 > nul
echo ========================================================
echo  🚀 LinkedIn B2B Auto-Poster Preview Generator
echo ========================================================
echo.
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py --dry-run
) else (
    python main.py --dry-run
)
echo.
pause
