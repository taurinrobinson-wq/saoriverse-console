# Start frontend in a way that prevents premature shutdown
Set-Location "d:\saoriverse-console\firstperson-web"

# Install dependencies first
Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
npm install --legacy-peer-deps 2>&1 | Out-Null

# Start frontend process
Write-Host "Starting Next.js dev server..." -ForegroundColor Cyan
$process = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -NoNewWindow -PassThru -RedirectStandardOutput "frontend_output.log" -RedirectStandardError "frontend_error.log"

Write-Host "Frontend started with PID: $($process.Id)" -ForegroundColor Green
Write-Host "Waiting 10 seconds for dev server to fully start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if process is still running
if ($process.HasExited) {
    Write-Host "ERROR: Frontend exited!" -ForegroundColor Red
    Get-Content "frontend_error.log" -ErrorAction SilentlyContinue
} else {
    Write-Host "SUCCESS: Frontend is running on http://127.0.0.1:3001" -ForegroundColor Green
    netstat -ano | Select-String "3001"
}
