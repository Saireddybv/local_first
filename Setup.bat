@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
 echo Python was not found. Install Python 3.11 or newer from https://www.python.org/downloads/windows/
 echo Keep "py launcher" ticked in the installer, then run Setup.bat again.
 goto failed
)
echo Creating the local Python environment...
py -3 -m venv .venv
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -c requirements-lock.txt -e ".[dev,tls]"
if errorlevel 1 goto failed
echo.
echo Setup complete. Open "Start Local First.bat".
if not defined LOCAL_FIRST_NO_PAUSE pause
exit /b 0
:failed
echo Setup failed. Review the error above.
if not defined LOCAL_FIRST_NO_PAUSE pause
exit /b 1
