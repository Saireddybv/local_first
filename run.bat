@echo off
echo Clipboard Sync Server Starting...
echo.
echo Step 1: Installing dependencies (if needed)...
pip install -q -r requirements.txt
echo.
echo Step 2: Finding your PC IP address...
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| find "IPv4"') do set IP=%%i
echo.
echo ========================================
echo Server is running!
echo.
echo Open this URL on your phone:
echo http://%IP%:5055
echo.
echo Both devices must be on the same WiFi!
echo ========================================
echo.
python app.py
pause

