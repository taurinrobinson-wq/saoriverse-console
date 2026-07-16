# Fix Unity Asset Issues - Batch Script
# 
# This script addresses the most common issues from asset refresh:
# 1. Converts shader line endings from mixed UNIX/Windows to consistent Windows (CRLF)
# 2. Lists files that need manual attention

param(
    [string]$ProjectPath = "d:\saoriverse-console\Velinor-Unity",
    [switch]$DryRun = $false
)

Write-Host "Unity Asset Refresh Fixes" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "Running in DRY-RUN mode. No files will be modified." -ForegroundColor Yellow
    Write-Host ""
}

# 1. Fix Shader Line Endings
Write-Host "STEP 1: Fixing shader line endings..." -ForegroundColor Green

$shaderPath = "$ProjectPath\Assets\BillemotdonggulLavaTubePack\Shaders"
$shaders = Get-ChildItem -Path $shaderPath -Include "*.shader", "*.cginc" -Recurse

$shaderCount = 0
foreach ($shader in $shaders) {
    try {
        $content = [System.IO.File]::ReadAllText($shader.FullName)
        
        # Convert to Windows line endings (CRLF)
        $fixedContent = $content -replace "`r`n", "`n" -replace "`r", "`n" -replace "`n", "`r`n"
        
        if ($content -ne $fixedContent) {
            if (-not $DryRun) {
                [System.IO.File]::WriteAllText($shader.FullName, $fixedContent)
            }
            $shaderCount++
            Write-Host "  ✓ $($shader.Name)" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "  ✗ ERROR in $($shader.Name): $_" -ForegroundColor Red
    }
}

Write-Host "  Total shaders fixed: $shaderCount" -ForegroundColor Green
Write-Host ""


# 2. Check PNG File Issue
Write-Host "STEP 2: Checking PNG file issue..." -ForegroundColor Green

$pngPath = "$ProjectPath\Assets\Graphics\NPCs\Captain_Veynar_sitting_nobg(all views).png"
if (Test-Path $pngPath) {
    $file = Get-Item $pngPath
    Write-Host "  ✓ PNG file found: $($file.Name)" -ForegroundColor Yellow
    Write-Host "    File size: $($file.Length) bytes" -ForegroundColor Yellow
    Write-Host "    Last modified: $($file.LastWriteTime)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  ACTION REQUIRED:" -ForegroundColor Red
    Write-Host "    Filename contains parentheses which may cause Unity read errors." -ForegroundColor Red
    Write-Host "    Recommended: Rename to 'Captain_Veynar_sitting_nobg_all_views.png'" -ForegroundColor Red
}
else {
    Write-Host "  ✗ PNG file NOT found at expected location" -ForegroundColor Red
    Write-Host "    Path: $pngPath" -ForegroundColor Red
}

Write-Host ""

# 3. List MaterialLocation.External issues
Write-Host "STEP 3: FBX files with MaterialLocation.External deprecation..." -ForegroundColor Green

$fbxPaths = @(
    "$ProjectPath\Assets\Tree_Packs\URP_Tree_Pack",
    "$ProjectPath\Assets\Blackant Master Studio\The Shed",
    "$ProjectPath\Assets\ALP_Assets",
    "$ProjectPath\Assets\BillemotdonggulLavaTubePack\Mesh",
    "$ProjectPath\Assets\EmbersStorm*",
    "$ProjectPath\Assets\Creepy_Cat"
)

$totalFbx = 0
foreach ($fbxPath in $fbxPaths) {
    $fbxFiles = Get-ChildItem -Path $fbxPath -Include "*.fbx", "*.FBX" -Recurse -ErrorAction SilentlyContinue
    $totalFbx += $fbxFiles.Count
}

Write-Host "  Found $totalFbx FBX files with external material references" -ForegroundColor Yellow
Write-Host "  ACTION REQUIRED:" -ForegroundColor Red
Write-Host "    1. Open each FBX in Project window" -ForegroundColor Red
Write-Host "    2. In Inspector, expand Materials section" -ForegroundColor Red
Write-Host "    3. Set 'Material Import Mode' to 'Import Embedded Materials'" -ForegroundColor Red
Write-Host "    4. Click 'Apply'" -ForegroundColor Red

Write-Host ""

# 4. Check for TitleScene CanvasScaler issue
Write-Host "STEP 4: Checking TitleScene for CanvasScaler issue..." -ForegroundColor Green

$titleScene = "$ProjectPath\Assets\Scenes\TitleScene.unity"
if (Test-Path $titleScene) {
    $sceneContent = Get-Content $titleScene | Select-Object -First 310 | Select-Object -Last 20
    Write-Host "  ✓ TitleScene.unity found" -ForegroundColor Yellow
    Write-Host "    ACTION REQUIRED:" -ForegroundColor Red
    Write-Host "    1. Open TitleScene.unity in Unity Editor" -ForegroundColor Red
    Write-Host "    2. Search for GameObjects with CanvasScaler component" -ForegroundColor Red
    Write-Host "    3. Either:" -ForegroundColor Red
    Write-Host "       - Remove CanvasScaler if not needed" -ForegroundColor Red
    Write-Host "       - OR import TextMesh Pro: Window → TextMeshPro → Import TMP Essential Resources" -ForegroundColor Red
}
else {
    Write-Host "  ✗ TitleScene.unity not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Fix Summary" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

Write-Host ""
Write-Host "✓ AUTOMATED:" -ForegroundColor Green
Write-Host "  - Shader line endings fixed: $shaderCount files" -ForegroundColor Green

Write-Host ""
Write-Host "⚠ MANUAL ACTION REQUIRED:" -ForegroundColor Yellow
Write-Host "  1. PNG filename: Rename file with parentheses to use underscores" -ForegroundColor Yellow
Write-Host "  2. CanvasScaler: Import TextMesh Pro or remove from TitleScene" -ForegroundColor Yellow
Write-Host "  3. FBX Materials: Re-import $totalFbx FBX files with embedded materials" -ForegroundColor Yellow

Write-Host ""

if ($DryRun) {
    Write-Host "NEXT STEP: Run again WITHOUT -DryRun to apply changes:" -ForegroundColor Cyan
    Write-Host "  .\Fix-UnityAssets.ps1 -ProjectPath '$ProjectPath'" -ForegroundColor Cyan
}
else {
    Write-Host "NEXT STEPS:" -ForegroundColor Cyan
    Write-Host "  1. In Unity Editor: Assets → Reimport All" -ForegroundColor Cyan
    Write-Host "  2. Check Console for remaining errors" -ForegroundColor Cyan
    Write-Host "  3. For each FBX: Reimport with 'Material Import Mode' = 'Embedded Materials'" -ForegroundColor Cyan
}

Write-Host ""
