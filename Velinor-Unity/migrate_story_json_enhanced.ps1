# Enhanced migration to handle files without tone indicators in text
# Extracts tone from tone_effects if not found in text

$storyDir = "d:\saoriverse-console\Velinor-Unity\Assets\Resources\velinor\stories"

function ConvertToneIndicatorToEnum {
    param($text)
    if ($text -like "*(T)*" -or $text -like "*Truth*" -or $text -like "*TRUST*") {
        return "Trust"
    }
    elseif ($text -like "*(O)*" -or $text -like "*Observation*") {
        return "Observation"
    }
    elseif ($text -like "*(N)*" -or $text -like "*Narrative*") {
        return "NarrativePresence"
    }
    elseif ($text -like "*(E)*" -or $text -like "*Empathy*") {
        return "Empathy"
    }
    return $null
}

function ExtractToneFromEffects {
    param($toneEffects)
    if ($toneEffects -and $toneEffects.entries -and $toneEffects.entries.Count -gt 0) {
        $firstKey = $toneEffects.entries[0].key
        # Normalize the key value
        if ($firstKey -eq "Truth") { return "Trust" }
        if ($firstKey -eq "Observation") { return "Observation" }
        if ($firstKey -eq "NarrativePresence") { return "NarrativePresence" }
        if ($firstKey -eq "Empathy") { return "Empathy" }
        return $firstKey
    }
    return $null
}

function CleanPlayerLine {
    param($text)
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
                    if (-not $choice.tone) {
                        # Try to get tone from text first
                        $tone = ConvertToneIndicatorToEnum $choice.text
                        
                        # If not found in text, try tone_effects
                        if (-not $tone) {
                            $tone = ExtractToneFromEffects $choice.tone_effects
                        }
                        
                        if ($tone) {
                            $choice | Add-Member -NotePropertyName "tone" -NotePropertyValue $tone -Force
                            $modified = $true
                            
                            # Add playerLine if it doesn't exist
                            if (-not $choice.playerLine) {
                                $playerLine = CleanPlayerLine $choice.text
                                $choice | Add-Member -NotePropertyName "playerLine" -NotePropertyValue $playerLine -Force
                            }
                        }
                    }
                }
            }
        }
        
        if ($modified) {
            $json = $content | ConvertTo-Json -Depth 10
            Set-Content $filePath $json -Encoding UTF8
            Write-Host "Updated: $filePath"
        }
        else {
            Write-Host "Already migrated: $filePath"
        }
    }
    catch {
        Write-Error "Error processing $($filePath): $_"
    }
}

Get-ChildItem "$storyDir/*.json" -File | ForEach-Object {
    MigrateStoryFile $_.FullName
}

Write-Host "Enhanced migration complete!"
