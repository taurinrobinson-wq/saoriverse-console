# Convert all beats-based JSON files to passages-based format
# This eliminates runtime conversion and makes data loading deterministic

param(
    [string]$StoriesPath = "C:\saoriverse-console\Velinor-Unity\Assets\Resources\velinor\stories"
)

$ErrorActionPreference = "Stop"

function Convert-BeatsToPassages {
    param([string]$JsonFilePath)
    
    Write-Host "Processing: $(Split-Path -Leaf $JsonFilePath)" -ForegroundColor Cyan
    
    # Read JSON
    $content = Get-Content -Path $JsonFilePath -Raw
    $data = $content | ConvertFrom-Json
    
    # Check if it's already in beats format
    if (-not $data.beats) {
        Write-Host "  ✓ Already in passages format, skipping" -ForegroundColor Green
        return
    }
    
    Write-Host "  Converting beats format to passages..." -ForegroundColor Yellow
    
    # Extract metadata
    $sceneName = $data.scene_id
    $requiredFlags = $data.required_flags
    $beats = $data.beats
    
    # Create passages array
    $passages = @()
    
    foreach ($beat in $beats) {
        # Create base passage
        $passage = [PSCustomObject]@{
            pid = "beat_$($beat.id)"
            conversationId = $sceneName
            beat_type = $beat.type
            active_speaker = $beat.active_speaker
            text = $beat.prompt
            choices = @()
            required_flags = $null
            name = $null
            scene_context = $beat.setting_description
            npc_responses = $null
            shared_beat = $null
            system_trigger = $null
            data_hook = $null
            system_triggers_list = $null
            is_shared_beat = $false
        }
        
        # Determine next beat ID (target for choices)
        $nextBeatId = if ($beat.next_beat_id -gt 0) { "beat_$($beat.next_beat_id)" } else { "DIALOGUE_END" }
        
        # Handle shared dialogue
        if ($beat.type -eq "npc_shared" -and $beat.shared_dialogue) {
            # For shared dialogue, create a passage for each speaker
            $sharedDialogues = @()
            for ($i = 0; $i -lt $beat.shared_dialogue.Count; $i++) {
                $speaker = $beat.shared_dialogue[$i]
                $nextTarget = if ($i -lt $beat.shared_dialogue.Count - 1) {
                    "beat_$($beat.id)_shared_$($i + 1)"
                } else {
                    $nextBeatId
                }
                
                $sharedPassage = [PSCustomObject]@{
                    pid = "beat_$($beat.id)_shared_$i"
                    conversationId = $sceneName
                    beat_type = "npc_shared"
                    active_speaker = $speaker.speaker
                    text = $speaker.text
                    choices = @(
                        [PSCustomObject]@{
                            tone = "T"
                            playerLine = "[Continue]"
                            npc_response = ""
                            target = $nextTarget
                            result_text = ""
                            tone_effects = @()
                            remnants_effects = @()
                            npc_resonance = @()
                        }
                    )
                    required_flags = $null
                    name = $null
                    scene_context = $null
                    npc_responses = $null
                    shared_beat = $null
                    system_trigger = $null
                    data_hook = $null
                    system_triggers_list = $null
                    is_shared_beat = $true
                }
                
                $passages += $sharedPassage
            }
            
            # Main beat points to first shared passage
            $passage.text = $beat.prompt
            $passage.choices = @(
                [PSCustomObject]@{
                    tone = "T"
                    playerLine = "[Continue]"
                    npc_response = ""
                    target = "beat_$($beat.id)_shared_0"
                    result_text = ""
                    tone_effects = @()
                    remnants_effects = @()
                    npc_resonance = @()
                }
            )
        }
        else {
            # Normal tone choices
            if ($beat.tone_choices) {
                foreach ($toneChoice in $beat.tone_choices) {
                    $choice = [PSCustomObject]@{
                        tone = $toneChoice.tone
                        playerLine = $toneChoice.text
                        label = $toneChoice.label
                        npc_response = if ($toneChoice.npc_response) { $toneChoice.npc_response } else { "" }
                        result_text = if ($toneChoice.result_text) { $toneChoice.result_text } else { "" }
                        target = $nextBeatId
                        tone_effects = if ($toneChoice.tone_effects) { $toneChoice.tone_effects } else { @() }
                        npc_resonance = @()
                        remnants_effects = if ($toneChoice.remnants_effects) { $toneChoice.remnants_effects } else { @() }
                    }
                    
                    $passage.choices += $choice
                }
            }
        }
        
        $passages += $passage
    }
    
    # Create new passages-based JSON structure
    $newData = [PSCustomObject]@{
        name = $sceneName
        startnode = "beat_1"
        passages = $passages
    }
    
    # Convert to JSON with proper formatting
    $jsonOutput = $newData | ConvertTo-Json -Depth 100
    
    # Write back to file
    Set-Content -Path $JsonFilePath -Value $jsonOutput -Encoding UTF8
    
    Write-Host "  ✓ Converted successfully ($($passages.Count) passages)" -ForegroundColor Green
}

# Find all story JSON files
Write-Host "Converting beats-based JSON files to passages format..." -ForegroundColor Magenta
Write-Host "Path: $StoriesPath`n" -ForegroundColor Gray

$jsonFiles = Get-ChildItem -Path $StoriesPath -Filter "*.json" -File

if ($jsonFiles.Count -eq 0) {
    Write-Host "No JSON files found!" -ForegroundColor Red
    exit 1
}

$converted = 0
$skipped = 0

foreach ($file in $jsonFiles) {
    try {
        Convert-BeatsToPassages -JsonFilePath $file.FullName
        $converted++
    }
    catch {
        Write-Host "  ✗ ERROR: $_" -ForegroundColor Red
    }
}

Write-Host "`n═══════════════════════════════════════" -ForegroundColor Magenta
Write-Host "Conversion Complete!" -ForegroundColor Green
Write-Host "  Converted: $converted files" -ForegroundColor Green
Write-Host "  Skipped:   $skipped files (already passages format)" -ForegroundColor Gray
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Review the converted files (they should look normal)"
Write-Host "  2. Build and test the dialogue system"
Write-Host "  3. Delete ConvertBeatsToPassages() method from DialogueManager.cs"
Write-Host "═══════════════════════════════════════" -ForegroundColor Magenta
