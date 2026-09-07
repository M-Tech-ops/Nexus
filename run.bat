@echo off
setlocal

echo ========================================
echo          Starting Nexus AI
echo ========================================

echo.
echo [1/2] Starting backend...

cd /d C:\Users\Orange\CLionProjects\Nexus\backend

start "Nexus AI Backend" cmd /k ..\venv\Scripts\python.exe main.py

echo [2/2] Waiting for backend to become ready...

:WAIT_FOR_SERVER

powershell -NoProfile -Command "$c = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue; if ($c) { exit 0 } else { exit 1 }"

if %errorlevel% neq 0 (
    echo Backend not ready yet...
    timeout /t 1 /nobreak >nul
    goto WAIT_FOR_SERVER
)

echo.
echo Backend is ready!
echo Starting Nexus AI frontend...

start "" "C:\Users\Orange\CLionProjects\Nexus\cmake-build-debug\NexusAI_Shell.exe"

exit