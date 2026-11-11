Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "    SMART EXPENSE MANAGEMENT SYSTEM (FLASK + AI)  " -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$pythonPath = "C:\Users\aziza\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe"

if (Test-Path $pythonPath) {
    Write-Host "[INFO] Starting Flask Server on http://127.0.0.1:5000..." -ForegroundColor Yellow
    & $pythonPath run.py
} else {
    Write-Host "[INFO] Starting with system python..." -ForegroundColor Yellow
    python run.py
}

