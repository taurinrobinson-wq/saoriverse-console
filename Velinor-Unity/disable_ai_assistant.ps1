# Disable Unity AI Assistant - Fixes RelayService connection issues
# This script removes the problematic AI Assistant package that's blocking your workflow

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Disabling Unity AI Assistant" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Close Unity
Write-Host "[1/5] Closing Unity Editor..." -ForegroundColor Yellow
Stop-Process -Name "Unity" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Step 2: Remove AI Assistant from Packages
Write-Host "[2/5] Removing AI Assistant package files..." -ForegroundColor Yellow
$packageCachePath = "Library/PackageCache/com.unity.ai.assistant*"
Get-Item $packageCachePath -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Step 3: Clean manifest.json
Write-Host "[3/5] Cleaning manifest.json..." -ForegroundColor Yellow
$manifestPath = "Packages/manifest.json"
if (Test-Path $manifestPath) {
    $content = Get-Content $manifestPath -Raw
    
    # Remove AI Assistant reference
    $content = $content -replace '"com\.unity\.ai\.assistant":\s*"[^"]*",?\s*', ''
    
    # Clean up any double commas or formatting issues
    $content = $content -replace ',\s*,', ','
    
    Set-Content $manifestPath $content -Encoding UTF8
    Write-Host "   ✓ Manifest cleaned" -ForegroundColor Green
}

# Step 4: Clear AI Assistant settings and cache
Write-Host "[4/5] Clearing AI Assistant cache and settings..." -ForegroundColor Yellow
$cachePath1 = "$env:LOCALAPPDATA\Unity\Assistant"
$cachePath2 = "ProjectSettings/Packages/com.unity.ai.assistant"

if (Test-Path $cachePath1) {
    Remove-Item $cachePath1 -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "   ✓ Removed: $cachePath1" -ForegroundColor Green
}

if (Test-Path $cachePath2) {
    Remove-Item $cachePath2 -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "   ✓ Removed: $cachePath2" -ForegroundColor Green
}

# Step 5: Update Project Settings
Write-Host "[5/5] Updating project settings..." -ForegroundColor Yellow
$settingsPath = "ProjectSettings/ProjectSettings.asset"
if (Test-Path $settingsPath) {
    $settings = Get-Content $settingsPath
    $settings = $settings -replace 'EnableAIAssistant.*', 'EnableAIAssistant: 0'
    Set-Content $settingsPath $settings
    Write-Host "   ✓ Project settings updated" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ AI Assistant disabled successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your workflow is now unblocked." -ForegroundColor Cyan
Write-Host ""
Write-Host "To troubleshoot the connection issue later:" -ForegroundColor Yellow
Write-Host "  1. Check Windows Firewall (allow Unity.exe outbound)"
Write-Host "  2. Test DNS: nslookup services.unity.com"
Write-Host "  3. Check proxy settings if behind corporate network"
Write-Host ""
Write-Host "To re-enable AI Assistant after fixing connectivity:" -ForegroundColor Yellow
Write-Host "  1. Open Velinor-Unity project in Unity"
Write-Host "  2. Window > Package Manager"
Write-Host "  3. Search for 'AI Assistant' and reinstall"
Write-Host ""
