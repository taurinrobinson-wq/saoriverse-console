$storyDir = "d:\saoriverse-console\Velinor-Unity\Assets\Resources\velinor\stories"

function GuessTargetTone {
    param($text)
    if ([string]::IsNullOrEmpty($text)) { return $null }
    
    $lower = $text.ToLower()
    if ($lower.Contains("observe") -or $lower.Contains("watch") -or $lower.Contains("study")) { return "Observation" }
    if ($lower.Contains("narrative") -or $lower.Contains("story") -or $lower.Contains("scroll")) { return "NarrativePresence" }
    if ($lower.Contains("empathy") -or $lower.Contains("feel") -or $lower.Contains("accept")) { return "Empathy" }
    if ($lower.Contains("truth") -or $lower.Contains("honest") -or $lower.Contains("ask")) { return "Trust" }
    return $null
}

function InferToneFromPid {
    param($pid, $index)
    $pidLower = $pid.ToLower()
    if ($pidLower.Contains("empathy")) { return "Empathy" }
    if ($pidLower.Contains("observe")) { return "Observation" }
    if ($pidLower.Contains("narrative")) { return "NarrativePresence" }
    if ($pidLower.Contains("truth")) { return "Trust" }
    
    return @("Trust", "Observation", "NarrativePresence", "Empathy")[$index % 4]
}

Get-ChildItem "$storyDir/*.json" | ForEach-Object {
    Write-Host "Processing: $($_.Name)"
    $json = Get-Content $_.FullName -Raw | ConvertFrom-Json
    $modified = $false
    
    foreach ($passage in $json.passages) {
        if ($passage.choices) {
            for ($i = 0; $i -lt $passage.choices.Count; $i++) {
                $choice = $passage.choices[$i]
                
                if (-not $choice.tone) {
                    $tone = GuessTargetTone $choice.text
                    if (-not $tone) { $tone = GuessTargetTone $choice.playerLine }
                    if (-not $tone) { $tone = InferToneFromPid $passage.pid $i }
                    
                    if ($tone) {
                        Add-Member -InputObject $choice -NotePropertyName "tone" -NotePropertyValue $tone -Force
                        $modified = $true
                    }
                }
                
                if ([string]::IsNullOrEmpty($choice.playerLine) -and $choice.text) {
                    $cleaned = ($choice.text -replace '\[.*?\]', '' -replace '\(.*?\)', '').Trim()
                    Add-Member -InputObject $choice -NotePropertyName "playerLine" -NotePropertyValue $cleaned -Force
                    $modified = $true
                }
            }
        }
    }
    
    if ($modified) {
        $output = $json | ConvertTo-Json -Depth 10
        Set-Content $_.FullName $output -Encoding UTF8
        Write-Host "  ✓ Updated"
    }
}

Write-Host "Done!"

