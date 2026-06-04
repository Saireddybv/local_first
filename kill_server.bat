@echo off
chcp 65001 >nul 2>&1

echo.
echo  ========================================
echo   Puppy Server - Stopping
echo  ========================================
echo.

taskkill /IM pythonw.exe /F >nul 2>&1
if %errorlevel% equ 0 (
    echo   Server stopped successfully!
) else (
    echo   Server was not running.
)

echo.
echo  ========================================
echo.
pause
exit
