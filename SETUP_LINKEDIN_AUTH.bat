@echo off
chcp 65001 > nul
echo ========================================================
echo  🔑 LinkedIn 1-Click OAuth Setup Assistant
echo ========================================================
echo.
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" setup_linkedin_auth.py
) else (
    python setup_linkedin_auth.py
)
echo.
pause
