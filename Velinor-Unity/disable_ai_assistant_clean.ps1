Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Disabling Unity AI Assistant" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Closing Unity Editor..." -ForegroundColor Yellow
Stop-Process -Name "Unity" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "[2/4] Removing AI Assistant package files..." -ForegroundColor Yellow
Get-Item "Library/PackageCache/com.unity.ai.assistant*" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "[3/4] Cleaning manifest.json..." -ForegroundColor Yellow
$manifestPath = "Packages/manifest.json"
if (Test-Path $manifestPath) {
    $content = Get-Content $manifestPath -Raw
    $content = $content -replace '"com\.unity\.ai\.assistant":\s*"[^"]*",?\s*', ''
    $content = $content -replace ',\s*,', ','
    Set-Content $manifestPath $content -Encoding UTF8
    Write-Host "   Success" -ForegroundColor Green
}

Write-Host "[4/4] Clearing cache..." -ForegroundColor Yellow
if (Test-Path "$env:LOCALAPPDATA\Unity\Assistant") {
    Remove-Item "$env:LOCALAPPDATA\Unity\Assistant" -Recurse -Force -ErrorAction SilentlyContinue
}
if (Test-Path "ProjectSettings/Packages/com.unity.ai.assistant") {
    Remove-Item "ProjectSettings/Packages/com.unity.ai.assistant" -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "AI Assistant disabled successfully" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your workflow is now unblocked." -ForegroundColor Cyan
Write-Host ""
