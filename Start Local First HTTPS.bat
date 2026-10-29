@echo off
cd /d "%~dp0"
if not defined LOCAL_FIRST_DATA if exist D:\ set "LOCAL_FIRST_DATA=D:\Local First Files"
if not exist ".certs\server.pem" (
 echo HTTPS certificates are missing. See docs\https.md.
 pause
 exit /b 1
)
".venv\Scripts\python.exe" -m local_first --port 8001 --cert .certs/server.pem --key .certs/server-key.pem %*
pause
