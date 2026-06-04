@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

:: Auto-detect local IP address
set IP=NOT_FOUND
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /i "IPv4"') do set IP=%%i
:: Trim leading space
for /f "tokens=*" %%a in ("%IP%") do set IP=%%a

echo.
echo  ========================================
echo   Puppy Server - Starting (Hidden Mode)
echo  ========================================
echo.
echo   Your IP:  %IP%
echo   URL:      http://%IP%:5055
echo.
echo   Open this URL on your phone!
echo   Both devices must be on same WiFi.
echo.
echo   To stop:  Double-click kill_server.bat
echo  ========================================
echo.

start "" pythonw.exe app.py
timeout /t 3 >nul
exit
