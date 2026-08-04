# Final comprehensive migration - ensures ALL choices have tone fields
# Handles all variation cases

$storyDir = "d:\saoriverse-console\Velinor-Unity\Assets\Resources\velinor\stories"

function ExtractToneFromEffects {
    param($toneEffects)
    if ($toneEffects) {
        if ($toneEffects -is [System.Collections.Hashtable]) {
            # Handle direct hashtable format like {"Empathy": 0.001, "Observation": -0.0005}
            $keys = $toneEffects.Keys
            if ($keys) {
                $key = $keys[0]
                if ($key -eq "Truth") { return "Trust" }
                if ($key -eq "Observation") { return "Observation" }
                if ($key -eq "NarrativePresence") { return "NarrativePresence" }
                if ($key -eq "Empathy") { return "Empathy" }
                return $null
            }
        }
        elseif ($toneEffects.entries) {
            # Handle entries array format
            if ($toneEffects.entries[0]) {
                $key = $toneEffects.entries[0].key
                if ($key -eq "Truth") { return "Trust" }
                if ($key -eq "Observation") { return "Observation" }
                if ($key -eq "NarrativePresence") { return "NarrativePresence" }
                if ($key -eq "Empathy") { return "Empathy" }
                return $null
            }
        }
    }
    return $null
}

function CleanPlayerLine {
    param($text)
    if ([string]::IsNullOrEmpty($text)) { return "" }
    $cleaned = $text -replace "\(T\)\s*", "" -replace "\(O\)\s*", "" -replace "\(N\)\s*", "" -replace "\(E\)\s*", "" -replace "Choice:\s*", ""
    return $cleaned.Trim()
}

function MigrateStoryFile {
    param($filePath)
    Write-Host "Processing: $filePath"
    
    try {
        $content = Get-Content $filePath -Raw | ConvertFrom-Json
        $modified = $false
        
        foreach ($passage in $content.passages) {
            if ($passage.choices) {
                foreach ($choice in $passage.choices) {
                    # Ensure tone field exists
                    if (-not $choice.tone) {
                        $tone = ExtractToneFromEffects $choice.tone_effects
                        if ($tone) {
                            $choice | Add-Member -NotePropertyName "tone" -NotePropertyValue $tone -Force
                            $modified = $true
                        }
                    }
                    
                    # Ensure playerLine exists
                    if ([string]::IsNullOrEmpty($choice.playerLine) -and $choice.text) {
                        $playerLine = CleanPlayerLine $choice.text
                        $choice | Add-Member -NotePropertyName "playerLine" -NotePropertyValue $playerLine -Force
                        $modified = $true
                    }
                    
                    # Normalize tone_effects format if it's a hashtable
                    if ($choice.tone_effects -is [System.Collections.Hashtable]) {
                        $entries = @()
                        foreach ($key in $choice.tone_effects.Keys) {
                            $entries += @{ key = $key; value = $choice.tone_effects[$key] }
                        }
                        $choice.tone_effects = @{ entries = $entries }
                        $modified = $true
                    }
                }
            }
        }
        
        if ($modified) {
            $json = $content | ConvertTo-Json -Depth 10
            Set-Content $filePath $json -Encoding UTF8
            Write-Host "✓ Updated: $filePath"
        }
        else {
            Write-Host "✓ Already complete: $filePath"
        }
    }
    catch {
        Write-Error "Error processing $($filePath): $_"
    }
}

Get-ChildItem "$storyDir/*.json" -File | ForEach-Object {
    MigrateStoryFile $_.FullName
}

Write-Host "`nFinal migration complete!"
