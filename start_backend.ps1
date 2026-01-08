# Start backend in a way that prevents premature shutdown
Set-Location "d:\saoriverse-console"

# Start backend process without inheriting stdin from parent
$process = Start-Process -FilePath "python" -ArgumentList "firstperson_backend.py" -NoNewWindow -PassThru -RedirectStandardOutput "backend_output.log" -RedirectStandardError "backend_error.log"

Write-Host "Backend started with PID: $($process.Id)"
Write-Host "Logs: backend_output.log and backend_error.log"
Start-Sleep -Seconds 5

# Check if process is still running
if ($process.HasExited) {
    Write-Host "ERROR: Backend exited immediately!"
    Get-Content "backend_error.log" -ErrorAction SilentlyContinue
} else {
    Write-Host "SUCCESS: Backend is running!"
    netstat -ano | Select-String "8000"
}
