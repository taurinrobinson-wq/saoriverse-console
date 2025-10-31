# Install Supabase CLI on Windows - PowerShell Script

# Get the latest release info
$release = Invoke-RestMethod -Uri "https://api.github.com/repos/supabase/cli/releases/latest"

# Find the Windows binary
$windowsAsset = $release.assets | Where-Object { $_.name -like "*windows*" -and $_.name -like "*amd64*" }

if ($windowsAsset) {
    Write-Host "Found Supabase CLI: $($windowsAsset.name)"
    Write-Host "Download URL: $($windowsAsset.browser_download_url)"
    
    # Download the binary
    $downloadPath = "supabase-cli.zip"
    Invoke-WebRequest -Uri $windowsAsset.browser_download_url -OutFile $downloadPath
    
    Write-Host "Downloaded to: $downloadPath"
    
    # Extract the binary
    Expand-Archive -Path $downloadPath -DestinationPath "supabase-cli" -Force
    
    # Find the supabase.exe file
    $supabaseExe = Get-ChildItem -Path "supabase-cli" -Recurse -Name "supabase.exe" | Select-Object -First 1
    
    if ($supabaseExe) {
        $fullPath = Join-Path "supabase-cli" $supabaseExe
        Write-Host "Supabase CLI extracted to: $fullPath"
        Write-Host "Testing installation..."
        & $fullPath --version
    } else {
        Write-Host "Could not find supabase.exe in extracted files"
        Get-ChildItem -Path "supabase-cli" -Recurse
    }
} else {
    Write-Host "Available assets:"
    $release.assets | Select-Object name, browser_download_url | Format-Table
}