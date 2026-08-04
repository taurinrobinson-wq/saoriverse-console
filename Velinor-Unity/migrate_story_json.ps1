# Migrate story JSON files to canonical tone structure
# Converts old format with tone indicators in text to explicit tone fields

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

function CleanPlayerLine {
    param($text)
    $cleaned = $text -replace "\(T\)\s*", "" -replace "\(O\)\s*", "" -replace "\(N\)\s*", "" -replace "\(E\)\s*", "" -replace "Choice:\s*", ""
    return $cleaned.Trim()
}

function MigrateStoryFile {
    param($filePath)
    Write-Host "Processing: $filePath"
    
    $content = Get-Content $filePath -Raw | ConvertFrom-Json
    
    foreach ($passage in $content.passages) {
        if ($passage.choices) {
            foreach ($choice in $passage.choices) {
                if (-not $choice.tone) {
                    $tone = ConvertToneIndicatorToEnum $choice.text
                    if ($tone) {
                        $choice | Add-Member -NotePropertyName "tone" -NotePropertyValue $tone -Force
                        $playerLine = CleanPlayerLine $choice.text
                        $choice | Add-Member -NotePropertyName "playerLine" -NotePropertyValue $playerLine -Force
                    }
                    
                    if ($choice.tone_effects -is [System.Collections.ArrayList] -or $choice.tone_effects -is [array]) {
                        $entries = @()
                        foreach ($effect in $choice.tone_effects) {
                            $entries += @{ key = $effect.key; value = $effect.value }
                        }
                        $choice.tone_effects = @{ entries = $entries }
                    }
                    
                    if ($choice.npc_resonance -is [System.Collections.ArrayList] -or $choice.npc_resonance -is [array]) {
                        $entries = @()
                        foreach ($effect in $choice.npc_resonance) {
                            $entries += @{ key = $effect.key; value = $effect.value }
                        }
                        $choice.npc_resonance = @{ entries = $entries }
                    }
                }
            }
        }
    }
    
    $json = $content | ConvertTo-Json -Depth 10
    Set-Content $filePath $json -Encoding UTF8
    Write-Host "Updated: $filePath"
}

Get-ChildItem "$storyDir/*.json" -File | ForEach-Object {
    try {
        MigrateStoryFile $_.FullName
    }
    catch {
        Write-Error "Error processing $($_.FullName): $_"
    }
}

Write-Host "Migration complete!"

