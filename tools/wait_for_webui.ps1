# Wait for the Automatic1111 WebUI to respond on port 7860
$max = 300  # total seconds to wait
$interval = 15
$elapsed = 0
while ($elapsed -lt $max) {
    try {
        Invoke-WebRequest -Uri 'http://127.0.0.1:7860' -UseBasicParsing -TimeoutSec 5 | Out-Null
        Write-Output 'listening'
        exit 0
    } catch {
        Write-Output "not-listening $elapsed"
        Start-Sleep -Seconds $interval
        $elapsed += $interval
    }
}
Write-Output 'timeout'
exit 1
