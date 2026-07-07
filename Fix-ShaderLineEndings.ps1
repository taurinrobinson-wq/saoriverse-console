$ProjectPath = "d:\saoriverse-console\Velinor-Unity"
$shaderPath = Join-Path $ProjectPath "Assets\BillemotdonggulLavaTubePack\Shaders"

Write-Host "Fixing shader line endings" -ForegroundColor Green
Write-Host "Path: $shaderPath" -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path $shaderPath)) {
    Write-Host "ERROR: Path not found" -ForegroundColor Red
    exit 1
}

$shaders = Get-ChildItem -Path $shaderPath -Include "*.shader", "*.cginc" -Recurse -ErrorAction SilentlyContinue
$totalCount = @($shaders).Count

Write-Host "Found $totalCount shader files" -ForegroundColor Yellow
Write-Host ""

$fixed = 0

foreach ($shader in $shaders) {
    $content = [System.IO.File]::ReadAllText($shader.FullName)
    $normalized = $content -replace "`r`n", "`n"
    $normalized = $normalized -replace "`r", "`n"
    $normalized = $normalized -replace "`n", "`r`n"
    [System.IO.File]::WriteAllText($shader.FullName, $normalized)
    $fixed++
}

Write-Host "Processed: $fixed files" -ForegroundColor Green
Write-Host ""
Write-Host "Next: Reimport all assets in Unity" -ForegroundColor Yellow
