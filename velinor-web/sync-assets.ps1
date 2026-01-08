# Link Velinor game assets to web public folder for Next.js to serve

$velinorRoot = "../velinor"
$publicAssets = "./public/assets"

Write-Host "Syncing Velinor assets to web public folder..."

# Ensure directories exist
@(
    "$publicAssets/backgrounds",
    "$publicAssets/npcs",
    "$publicAssets/overlays"
) | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
        Write-Host "Created: $_"
    }
}

# Copy backgrounds
Write-Host "`nCopying backgrounds..."
@(
    "Velhara_background_title(blur).png",
    "Velhara_background_title.png",
    "velinor_title_eyes_closed.png"
) | ForEach-Object {
    $src = "$velinorRoot/backgrounds/$_"
    $dst = "$publicAssets/backgrounds/$_"
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $dst -Force
        Write-Host "  ✓ $_"
    }
}

# Copy NPCs
Write-Host "`nCopying NPCs..."
@(
    "velinor_eyesclosed2.png",
    "velinor_eyesclosed.png",
    "velinor_eyesopen.png"
) | ForEach-Object {
    $src = "$velinorRoot/npcs/$_"
    $dst = "$publicAssets/npcs/$_"
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $dst -Force
        Write-Host "  ✓ $_"
    }
}

# Copy overlays
Write-Host "`nCopying overlays..."
@(
    "velinor_title_transparent2.png",
    "velinor_title_transparent.png"
) | ForEach-Object {
    $src = "$velinorRoot/overlays/$_"
    $dst = "$publicAssets/overlays/$_"
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $dst -Force
        Write-Host "  ✓ $_"
    }
}

Write-Host "`n Asset sync complete!"
Write-Host ""
Write-Host "Velinor assets are now available at:"
Write-Host "  - /assets/backgrounds/Velhara_background_title(blur).png"
Write-Host "  - /assets/npcs/velinor_eyesclosed2.png"
Write-Host "  - /assets/overlays/velinor_title_transparent2.png"
