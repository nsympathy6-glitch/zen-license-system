@echo off
echo Starting Zen License System...

REM Check if .env exists
if not exist .env (
    echo Creating .env from template...
    copy .env.example .env
    echo Please edit .env with your configuration values.
    pause
)

REM Start the license server
echo Starting License Server...
start "License Server" cmd /c "cd server && python main.py"

REM Wait for server to start
timeout /t 3 /nobreak >nul

REM Start the Discord bot
echo Starting Discord Bot...
start "Discord Bot" cmd /c "cd bot && python main.py"

echo.
echo System started!
echo - License Server: http://localhost:8000
echo - Discord Bot: Running (check console for status)
echo.
echo Press any key to open the Launcher...
pause >nul

REM Start the launcher
cd launcher && python main.py
