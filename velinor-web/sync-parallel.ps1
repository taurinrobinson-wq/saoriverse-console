# Sync parallel folders: velinor (Python engine) ↔ velinor-web (Next.js frontend)
# Usage: cd velinor-web; powershell -ExecutionPolicy Bypass -File sync-parallel.ps1

$ErrorActionPreference = "Stop"

$velinorRoot = "../velinor"
$webRoot = "."

Write-Host "`n=== PARALLEL FOLDER SYNCHRONIZATION ===" -ForegroundColor Cyan
Write-Host "Source (Engine):  $velinorRoot" -ForegroundColor Gray
Write-Host "Target (Web):     $webRoot" -ForegroundColor Gray
Write-Host ""

# Verify both folders exist
if (-not (Test-Path $velinorRoot)) {
    Write-Host "ERROR: velinor folder not found at $velinorRoot" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $webRoot)) {
    Write-Host "ERROR: velinor-web folder not found at $webRoot" -ForegroundColor Red
    exit 1
}

# Track stats
$stats = @{
    files_synced = 0
    files_skipped = 0
    errors = 0
}

# ============================================================================
# PART 1: Sync Data Files (JSON)
# ============================================================================

Write-Host "PART 1: Syncing Data Files (JSON)" -ForegroundColor Yellow
Write-Host "-" * 50

$dataFiles = @(
    @{ src = "npc_profiles.json"; dest = "npc_profiles.json" },
    @{ src = "influence_map.json"; dest = "influence_map.json" }
)

foreach ($file in $dataFiles) {
    $srcPath = "$velinorRoot/data/$($file.src)"
    $dstPath = "$webRoot/src/data/$($file.dest)"

    if (Test-Path $srcPath) {
        $srcHash = (Get-FileHash $srcPath -Algorithm MD5).Hash
        $dstHash = if (Test-Path $dstPath) { (Get-FileHash $dstPath -Algorithm MD5).Hash } else { "" }

        if ($srcHash -ne $dstHash) {
            Copy-Item -Path $srcPath -Destination $dstPath -Force
            Write-Host "  [SYNC] $($file.src)" -ForegroundColor Green
            $stats.files_synced += 1
        } else {
            Write-Host "  [SKIP] $($file.src) (no changes)" -ForegroundColor Gray
            $stats.files_skipped += 1
        }
    } else {
        Write-Host "  [WARN] Source not found: $srcPath" -ForegroundColor Yellow
        $stats.errors += 1
    }
}

# ============================================================================
# PART 2: Sync Image Assets (Backgrounds, NPCs, Overlays)
# ============================================================================

Write-Host "`nPART 2: Syncing Image Assets" -ForegroundColor Yellow
Write-Host "-" * 50

# Helper function to sync directory
function Sync-AssetDirectory {
    param(
        [string]$SourceDir,
        [string]$DestDir,
        [string]$Label
    )

    if (-not (Test-Path $SourceDir)) {
        Write-Host "  [WARN] Source directory not found: $SourceDir" -ForegroundColor Yellow
        return
    }

    # Create destination if needed
    if (-not (Test-Path $DestDir)) {
        New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
        Write-Host "  [NEW] Created directory: $DestDir" -ForegroundColor Cyan
    }

    # Get all image files
    $sourceFiles = Get-ChildItem -Path $SourceDir -Filter "*.png" -ErrorAction SilentlyContinue
    $sourceCount = ($sourceFiles | Measure-Object).Count

    if ($sourceCount -eq 0) {
        Write-Host "  [SKIP] $Label - no PNG files found" -ForegroundColor Gray
        return
    }

    $syncCount = 0
    foreach ($file in $sourceFiles) {
        $destPath = "$DestDir/$($file.Name)"

        if (Test-Path $destPath) {
            $srcHash = (Get-FileHash $file.FullName -Algorithm MD5).Hash
            $dstHash = (Get-FileHash $destPath -Algorithm MD5).Hash

            if ($srcHash -eq $dstHash) {
                # File unchanged
                continue
            }
        }

        Copy-Item -Path $file.FullName -Destination $destPath -Force
        $syncCount += 1
    }

    if ($syncCount -gt 0) {
        Write-Host "  [SYNC] $Label ($syncCount/$sourceCount files)" -ForegroundColor Green
        $stats.files_synced += $syncCount
    } else {
        Write-Host "  [SKIP] $Label (all current)" -ForegroundColor Gray
        $stats.files_skipped += $sourceCount
    }
}

# Sync each asset type
Sync-AssetDirectory "$velinorRoot/backgrounds" "$webRoot/public/assets/backgrounds" "Backgrounds"
Sync-AssetDirectory "$velinorRoot/npcs" "$webRoot/public/assets/npcs" "NPCs"
Sync-AssetDirectory "$velinorRoot/overlays" "$webRoot/public/assets/overlays" "Overlays"

# ============================================================================
# PART 3: Verification
# ============================================================================

Write-Host "`nPART 3: Verification" -ForegroundColor Yellow
Write-Host "-" * 50

$verifyOk = $true

# Check JSON files
$jsonFiles = @(
    @{ path = "src/data/npc_profiles.json"; label = "NPC Profiles" },
    @{ path = "src/data/influence_map.json"; label = "Influence Map" }
)

foreach ($file in $jsonFiles) {
    if (Test-Path "$webRoot/$($file.path)") {
        Write-Host "  [OK] $($file.label) exists" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] $($file.label) missing" -ForegroundColor Red
        $verifyOk = $false
    }
}

# Check asset directories
$assetDirs = @(
    @{ path = "public/assets/backgrounds"; label = "Backgrounds" },
    @{ path = "public/assets/npcs"; label = "NPCs" },
    @{ path = "public/assets/overlays"; label = "Overlays" }
)

foreach ($dir in $assetDirs) {
    if (Test-Path "$webRoot/$($dir.path)") {
        $fileCount = (Get-ChildItem "$webRoot/$($dir.path)" -Filter "*.png" | Measure-Object).Count
        if ($fileCount -gt 0) {
            Write-Host "  [OK] $($dir.label) ($fileCount files)" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] $($dir.label) empty" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [ERROR] $($dir.label) directory missing" -ForegroundColor Red
        $verifyOk = $false
    }
}

# ============================================================================
# SUMMARY
# ============================================================================

Write-Host "`n=== SYNC SUMMARY ===" -ForegroundColor Cyan
Write-Host "Files synced:  $($stats.files_synced)" -ForegroundColor Green
Write-Host "Files skipped: $($stats.files_skipped)" -ForegroundColor Gray
Write-Host "Errors:        $($stats.errors)" -ForegroundColor $(if ($stats.errors -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($verifyOk) {
    Write-Host "Status: READY - All folders properly synced!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  - Run: npm run dev"
    Write-Host "  - Visit: http://localhost:3000"
    Write-Host "  - Verify all assets load correctly"
    Write-Host ""
} else {
    Write-Host "Status: WARNING - Some files may be missing" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Cyan
    Write-Host "  - Check both folders exist"
    Write-Host "  - Verify file permissions"
    Write-Host "  - Re-run sync script"
    Write-Host ""
    exit 1
}

Write-Host "Sync completed at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
