@echo off
echo Starting Chatbot API...
echo Access via LAN: http://%COMPUTERNAME%:8000
echo Access via Localhost: http://localhost:8000
echo.

:ActivateVenv
if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo No virtual environment found, using system python...
)

python api.py
pause
