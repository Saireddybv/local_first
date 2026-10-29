@echo off
cd /d "%~dp0"
if not defined LOCAL_FIRST_DATA if exist D:\ set "LOCAL_FIRST_DATA=D:\Local First Files"
if not exist ".venv\Scripts\python.exe" (
 echo First run: installing Local First. This takes about a minute.
 set "LOCAL_FIRST_NO_PAUSE=1"
 call Setup.bat
 if errorlevel 1 (
  pause
  exit /b 1
 )
)
".venv\Scripts\python.exe" -m local_first %*
pause
