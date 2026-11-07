@echo off
chcp 65001 > nul
echo ========================================================
echo [Launch] Pushing Latest International Updates to GitHub
echo ========================================================
echo.
git push origin main
echo.
if %ERRORLEVEL% equ 0 (
    echo Successfully pushed to GitHub!
) else (
    echo [X] Push failed. Please check your internet or git credentials.
)
echo.
pause
