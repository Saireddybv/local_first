@echo off
chcp 65001 >nul 2>&1

:: Auto-detect local IP address
set IP=NOT_FOUND
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /i "IPv4"') do set IP=%%i
for /f "tokens=*" %%a in ("%IP%") do set IP=%%a

echo.
echo  ========================================
echo   Puppy Server - Status Check
echo  ========================================
echo.

tasklist /FI "IMAGENAME eq pythonw.exe" 2>nul | find /I "pythonw.exe" >nul
if %errorlevel% equ 0 (
    echo   Server is RUNNING
    echo.
    echo   Your IP:  %IP%
    echo   URL:      http://%IP%:5055
    echo.
    echo   Open this URL on your phone!
) else (
    echo   Server is NOT running.
    echo.
    echo   Start it with: run_silent.bat
)

echo.
echo  ========================================
echo.
pause
exit
