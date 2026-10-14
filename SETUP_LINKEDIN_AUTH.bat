@echo off
chcp 65001 > nul
echo ========================================================
echo  🔑 LinkedIn 1-Click OAuth Setup Assistant
echo ========================================================
echo.
.venv\Scripts\python.exe setup_linkedin_auth.py
echo.
pause
