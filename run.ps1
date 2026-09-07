Write-Host "========================================"
Write-Host "         Starting Nexus AI"
Write-Host "========================================"
Write-Host ""

Write-Host "[1/2] Starting backend..."

Set-Location "C:\Users\Orange\CLionProjects\Nexus\backend"

Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-Command", `
    "..\venv\Scripts\python.exe main.py" `
    -WindowStyle Normal

Write-Host "[2/2] Waiting for backend to become ready..."

while ($true) {
    $connection = Get-NetTCPConnection `
        -LocalPort 8000 `
        -State Listen `
        -ErrorAction SilentlyContinue

    if ($connection) {
        break
    }

    Write-Host "Backend not ready yet..."
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "Backend is ready!"
Write-Host "Starting Nexus AI frontend..."

Start-Process `
    "C:\Users\Orange\CLionProjects\Nexus\cmake-build-debug\NexusAI_Shell.exe"

exit