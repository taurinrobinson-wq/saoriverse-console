using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Velinor.Core;
using Velinor.Management;

/// <summary>
/// Unified dialogue manager for Velinor.
/// Loads and plays dialogue beats using a single consistent system.
/// Empty fields are simply not displayed.
/// </summary>
public class DialogueManager : MonoBehaviour
{
    public static DialogueManager Instance { get; private set; }

    [SerializeField] private TextAsset dialogueJson;
    private DialogueUIController dialogueUI;
    private PortraitManager portraitManager;
    private VoiceoverManager voiceoverManager;
    private NPCDialogueDriver activeNpcDriver; // Reference to current NPC for audio clip access

    private Dictionary<string, BeatData> beatsById = new Dictionary<string, BeatData>();
    private Dictionary<float, BeatData> beatsByNumId = new Dictionary<float, BeatData>();
    private BeatData currentBeat;
    private bool isDialogueActive = false;
    private string activeNpcId;
    private string currentSceneId;
    private bool lastActionWasNpcResponse = false;  // Track if last shown text was an npc_response
    private string lastSelectedTone = "";  // Track the player's selected tone for prompt_source resolution

    public System.Action OnDialogueEnded;

    private void Awake()
    {
        if (Instance != null && Instance != this) { Destroy(gameObject); return; }
        Instance = this;
        DontDestroyOnLoad(gameObject);
        
        dialogueUI = FindAnyObjectByType<DialogueUIController>();
        portraitManager = FindAnyObjectByType<PortraitManager>();
        if (portraitManager == null)
        {
            // Create PortraitManager if it doesn't exist
            GameObject portraitObj = new GameObject("PortraitManager");
            portraitManager = portraitObj.AddComponent<PortraitManager>();
            DontDestroyOnLoad(portraitObj);
        }

        voiceoverManager = FindAnyObjectByType<VoiceoverManager>();
        if (voiceoverManager == null)
        {
            // Create VoiceoverManager if it doesn't exist
            GameObject voiceoverObj = new GameObject("VoiceoverManager");
            voiceoverManager = voiceoverObj.AddComponent<VoiceoverManager>();
            DontDestroyOnLoad(voiceoverObj);
        }
    }

    public void LoadDialogue(TextAsset jsonFile)
    {
        dialogueJson = jsonFile;
        LoadBeatsFromJson();
    }

    private void LoadBeatsFromJson()
    {
        if (dialogueJson == null)
        {
            Debug.LogError("[DialogueManager] No dialogue JSON loaded");
            return;
        }

        try
        {
            beatsById.Clear();
            beatsByNumId.Clear();

            var root = JsonUtility.FromJson<DialogueJson>(dialogueJson.text);

            if (root == null)
            {
                Debug.LogError("[DialogueManager] Failed to parse dialogue JSON");
                return;
            }

            // Try passages format
            if (root.passages != null && root.passages.Length > 0)
            {
                foreach (var beat in root.passages)
                {
                    beatsById[beat.pid] = beat;
                    beat.mode = InferMode(beat);
                    Debug.Log($"[DialogueManager] Loaded beat: {beat.pid} (mode: {beat.mode})");
                }
                Debug.Log($"[DialogueManager] Loaded {beatsById.Count} beats from passages format");
                return;
            }

            // Try beats format
            if (root.beats != null && root.beats.Length > 0)
            {
                currentSceneId = root.scene_id;  // Capture scene ID for voiceover file paths
                foreach (var beat in root.beats)
                {
                    beatsByNumId[beat.id] = beat;
                    beatsById[beat.id.ToString()] = beat; // Also index by string ID
                    beat.mode = InferMode(beat);
                    Debug.Log($"[DialogueManager] Loaded beat: {beat.id} (mode: {beat.mode})");
                }
                Debug.Log($"[DialogueManager] Loaded {beatsByNumId.Count} beats from beats format (scene: {currentSceneId})");
                return;
            }

            Debug.LogError("[DialogueManager] No passages or beats array found in JSON");
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"[DialogueManager] Error parsing dialogue JSON: {ex.Message}");
        }
    }

    public void StartDialogue(string npcId, string startBeatId)
    {
        // Clear diary at start of each dialogue session
        var diaryManager = FindAnyObjectByType<DiaryManager>();
        if (diaryManager != null)
        {
            diaryManager.ClearDiary();
        }

        // Clear portrait at start of dialogue (will be populated as beats display)
        if (portraitManager != null)
        {
            portraitManager.HidePortrait();
        }

        // Reset append flag for new dialogue
        lastActionWasNpcResponse = false;

        activeNpcId = npcId;
        isDialogueActive = true;

        // Find the NPC driver by GameObject name to access pre-loaded audio clips
        GameObject npcGameObject = GameObject.Find(npcId);
        if (npcGameObject != null)
        {
            activeNpcDriver = npcGameObject.GetComponent<NPCDialogueDriver>();
        }

        // Try to find beat by string ID (passages format)
        if (beatsById.TryGetValue(startBeatId, out var beat))
        {
            DisplayBeat(beat);
            return;
        }

        // Try to find beat by numeric ID (beats format)
        if (float.TryParse(startBeatId, out var numId) && beatsByNumId.TryGetValue(numId, out beat))
        {
            DisplayBeat(beat);
            return;
        }

        Debug.LogError($"[DialogueManager] No beat found with ID '{startBeatId}'");
        EndDialogue();
    }

    private void DisplayBeat(BeatData beat)
    {
        currentBeat = beat;
        dialogueUI.ClearButtons();

        // Process beat-level system triggers (e.g., update_dialogue_names)
        ProcessBeatSystemTriggers(beat.system_triggers);

        // Show portrait for NPC dialogue (if portrait_expression field exists)
        if (!string.IsNullOrEmpty(beat.active_speaker) && portraitManager != null)
        {
            string expression = !string.IsNullOrEmpty(beat.portrait_expression) ? beat.portrait_expression : "neutral";
            portraitManager.ShowPortrait(beat.active_speaker, expression);
        }

        // Play voiceover for this beat if audio clip is specified
        if (!string.IsNullOrEmpty(beat.audio_clip) && voiceoverManager != null)
        {
            // Try to use pre-loaded clip from NPC driver first (faster, no file I/O)
            if (activeNpcDriver != null)
            {
                AudioClip preloadedClip = activeNpcDriver.GetAudioClip(beat.id.ToString());
                if (preloadedClip != null)
                {
                    voiceoverManager.PlayVoiceoverClip(preloadedClip);
                }
                else
                {
                    // Fallback: load from file if not pre-loaded
                    voiceoverManager.PlayVoiceover(currentSceneId, beat.audio_clip);
                }
            }
            else
            {
                // No NPC driver, load from file
                voiceoverManager.PlayVoiceover(currentSceneId, beat.audio_clip);
            }
        }

        Debug.Log($"[DialogueManager] Displaying beat: {beat.pid ?? beat.id.ToString()} (mode: {beat.mode})");

        // Resolve prompt if it uses prompt_source
        string resolvedPrompt = ResolvePrompt(beat);

        // Check if beat has choices
        bool hasChoices = (beat.tone_choices != null && beat.tone_choices.Length > 0) ||
                         (beat.choices != null && beat.choices.Length > 0);

        // Show shared_beat if it exists AND there are NO choices (auto-advance dialogue)
        if (!string.IsNullOrEmpty(beat.shared_beat) && !hasChoices)
        {
            dialogueUI.ShowSpeaker(beat.active_speaker ?? "", beat.display_name);
            dialogueUI.ShowText(beat.shared_beat);
            dialogueUI.ShowSharedBeat(beat.shared_beat);
            StartCoroutine(AutoAdvanceAfterSharedBeat(beat));
            return;
        }

        // If there are choices, show prompt + shared_beat + choices together
        if (hasChoices)
        {
            dialogueUI.HideSharedBeat();
            
            // Check if we should append (continuation) or replace text
            if (lastActionWasNpcResponse)
            {
                // Continuation beat: append prompt + shared_beat instead of replacing
                Debug.Log($"[DialogueManager] Continuation beat detected. Appending text instead of replacing.");

                string appendText = BuildContinuationText(beat, resolvedPrompt);

                if (!string.IsNullOrEmpty(appendText))
                {
                    dialogueUI.AppendText(appendText, useTypewriter: true);
                }
                
                lastActionWasNpcResponse = false;  // Reset flag
            }
            else
            {
                // Normal beat: show prompt and shared_beat as usual
                dialogueUI.ShowSpeaker(beat.active_speaker ?? "", beat.display_name);
                dialogueUI.ShowText(resolvedPrompt ?? "");
                
                if (!string.IsNullOrEmpty(beat.shared_beat))
                {
                    dialogueUI.ShowSharedBeat(beat.shared_beat);
                }
            }
            
            // Show choices
            if (beat.tone_choices != null && beat.tone_choices.Length > 0)
            {
                dialogueUI.ShowChoices(beat, choice => StartCoroutine(ResolveChoiceCoroutine(beat, choice)));
            }
            else if (beat.choices != null && beat.choices.Length > 0)
            {
                dialogueUI.ShowChoices(beat, choice => StartCoroutine(ResolveChoiceCoroutine(beat, choice)));
            }
            return;
        }

        // No choices and no shared_beat - just show prompt
        dialogueUI.HideSharedBeat();
        dialogueUI.ShowSpeaker(beat.active_speaker ?? "", beat.display_name);
        if (lastActionWasNpcResponse)
        {
            string appendText = BuildContinuationText(beat, resolvedPrompt);
            if (!string.IsNullOrEmpty(appendText))
            {
                dialogueUI.AppendText(appendText, useTypewriter: true);
            }
            lastActionWasNpcResponse = false;
        }
        else
        {
            dialogueUI.ShowText(resolvedPrompt ?? "");
        }
    }

    private IEnumerator AutoAdvanceAfterSharedBeat(BeatData beat)
    {
        yield return dialogueUI.WaitForDisplayComplete();
        
        // Advance to next beat
        float nextId = beat.next_beat_id > 0 ? beat.next_beat_id : (beat.id + 1);
        AdvanceToBeat(nextId);
    }

    /// <summary>
    /// Resolves a beat's prompt, handling prompt_source references.
    /// If the beat has a prompt_source, fetches the referenced beat's npc_response (or prompt).
    /// Otherwise, uses the beat's own prompt.
    /// </summary>
    private string ResolvePrompt(BeatData beat)
    {
        // If no prompt_source, return beat's prompt as-is
        if (beat.prompt_source == null || beat.prompt_source.type != "previous_choice_response")
        {
            return beat.prompt ?? "";
        }

        // Resolve prompt_source: fetch the prior beat's choice response
        BeatData priorBeat = GetBeatById(beat.prompt_source.beat_id);
        if (priorBeat == null)
        {
            Debug.LogWarning($"[DialogueManager] prompt_source references unknown beat_id: {beat.prompt_source.beat_id}");
            return beat.prompt ?? "";
        }

        // Get the field from the prior beat (usually npc_response from a choice)
        string sourceText = "";
        
        if (beat.prompt_source.choice_field == "npc_response")
        {
            // Try to get npc_response from the selected choice
            if (priorBeat.tone_choices != null && priorBeat.tone_choices.Length > 0)
            {
                // Find the choice that matches the last selected tone
                foreach (var choice in priorBeat.tone_choices)
                {
                    if (choice.tone == lastSelectedTone)
                    {
                        sourceText = choice.npc_response ?? "";
                        break;
                    }
                }
            }
            else if (priorBeat.choices != null && priorBeat.choices.Length > 0)
            {
                // For standard choices, use first one's npc_response (or could track selection)
                sourceText = priorBeat.choices[0].npc_response ?? "";
            }
        }
        else if (beat.prompt_source.choice_field == "prompt")
        {
            // Use the prior beat's prompt field
            sourceText = priorBeat.prompt ?? "";
        }

        // If we got the source text, return it
        if (!string.IsNullOrEmpty(sourceText))
        {
            return sourceText;
        }

        // Fallback to beat's own prompt
        return beat.prompt ?? "";
    }

    private string BuildContinuationText(BeatData beat, string resolvedPrompt)
    {
        bool inheritsPreviousChoiceResponse =
            beat.prompt_source != null &&
            beat.prompt_source.type == "previous_choice_response";

        string appendText = inheritsPreviousChoiceResponse ? "" : (resolvedPrompt ?? "");

        if (!string.IsNullOrEmpty(beat.shared_beat))
        {
            if (!string.IsNullOrEmpty(appendText))
            {
                appendText += "\n";
            }

            appendText += beat.shared_beat;
        }

        return appendText;
    }

    private BeatData GetBeatById(float id)
    {
        if (beatsByNumId.TryGetValue(id, out var beat))
            return beat;
        return null;
    }

    private IEnumerator ResolveChoiceCoroutine(BeatData beat, BeatChoice choice)
    {
        // Store the selected tone for prompt_source resolution
        lastSelectedTone = choice.tone ?? "";

        // Fade out any ongoing voiceover to prevent clipping
        if (voiceoverManager != null)
        {
            voiceoverManager.FadeOutAndStop(0.3f);
        }

        dialogueUI.ClearButtons();
        Debug.Log($"[DialogueManager] Choice selected: {choice.text}");

        // Play voiceover for player's choice if audio clip is specified
        if (!string.IsNullOrEmpty(choice.audio_clip_on_choice) && voiceoverManager != null)
        {
            // Try to use pre-loaded clip from NPC driver first (faster, no file I/O)
            if (activeNpcDriver != null)
            {
                AudioClip preloadedClip = activeNpcDriver.GetAudioClip(beat.id.ToString(), choice.tone);
                if (preloadedClip != null)
                {
                    voiceoverManager.PlayVoiceoverClip(preloadedClip);
                }
                else
                {
                    // Fallback: load from file if not pre-loaded
                    voiceoverManager.PlayVoiceover(currentSceneId, choice.audio_clip_on_choice);
                }
            }
            else
            {
                // No NPC driver, load from file
                voiceoverManager.PlayVoiceover(currentSceneId, choice.audio_clip_on_choice);
            }
        }

        // 1. Handle result_text - either show in notification or skip
        if (!string.IsNullOrEmpty(choice.result_text))
        {
            if (choice.show_result_in_notification)
            {
                // Show result_text in notification panel
                Debug.Log($"[DialogueManager] Showing result_text in notification: {choice.result_text}");
                dialogueUI.TriggerSystemEvent("show_notification", new string[] { choice.result_text });
            }
            else
            {
                // Legacy: show in dialogue (invisible, 1 frame flash)
                Debug.Log($"[DialogueManager] Skipping result_text display (show_result_in_notification=false)");
            }
        }

        // 2. Apply tone and remnants effects
        ApplyToneEffects(choice.tone_effects);
        ApplyRemnantsEffects(choice.remnants_effects);
        
        // 2b. Process system triggers from the choice (pass beat's diary entries)
        ProcessSystemTriggers(choice.system_triggers, beat.diary_entries);

        // 3. Show npc_response if it exists
        if (!string.IsNullOrEmpty(choice.npc_response))
        {
            Debug.Log($"[DialogueManager] Showing npc_response: {choice.npc_response}");
            
            // Use npc_speaker if provided (for player_inner beats where NPC responds)
            // Otherwise fall back to beat.active_speaker
            string npcSpeaker = !string.IsNullOrEmpty(choice.npc_speaker) ? choice.npc_speaker : beat.active_speaker;
            
            // Show portrait expression for the response (if specified)
            if (!string.IsNullOrEmpty(choice.portrait_expression_on_response) && portraitManager != null)
            {
                portraitManager.ShowPortrait(npcSpeaker, choice.portrait_expression_on_response);
                Debug.Log($"[DialogueManager] Showing response portrait: {npcSpeaker}_{choice.portrait_expression_on_response}");
            }

            // Play voiceover for NPC response if audio clip is specified
            if (!string.IsNullOrEmpty(choice.audio_clip_on_response) && voiceoverManager != null)
            {
                // Try to use pre-loaded clip from NPC driver first (faster, no file I/O)
                if (activeNpcDriver != null)
                {
                    AudioClip preloadedClip = activeNpcDriver.GetAudioClip(beat.id.ToString(), $"{choice.tone}_npc");
                    if (preloadedClip != null)
                    {
                        voiceoverManager.PlayVoiceoverClip(preloadedClip);
                    }
                    else
                    {
                        // Fallback: load from file if not pre-loaded
                        voiceoverManager.PlayVoiceover(currentSceneId, choice.audio_clip_on_response);
                    }
                }
                else
                {
                    // No NPC driver, load from file
                    voiceoverManager.PlayVoiceover(currentSceneId, choice.audio_clip_on_response);
                }
            }
            
            string npcDisplayName = !string.IsNullOrEmpty(choice.npc_display_name) ? choice.npc_display_name : beat.display_name;
            
            dialogueUI.ShowSpeaker(npcSpeaker ?? "", npcDisplayName);
            dialogueUI.ShowText(choice.npc_response);
            dialogueUI.HideSharedBeat();
            
            // Mark that we just showed an npc_response so the next beat knows to append instead of replace
            lastActionWasNpcResponse = true;
            
            // Advance to next beat - it will have the appropriate choices defined in JSON
            // (either 4 tone choices, 1 Continue choice, or 1 End choice)
            float nextBeatId = choice.target > 0
                ? choice.target
                : (beat.next_beat_id > 0 ? beat.next_beat_id : (beat.id + 1));
            Debug.Log($"[DialogueManager] NPC response shown. Advancing to beat: {nextBeatId}");
            AdvanceToBeat(nextBeatId);
            
            yield break;
        }

        // 4. No npc_response: Use choice's target to determine next beat
        float choiceTarget = choice.target > 0 ? choice.target : beat.next_beat_id;
        
        if (choiceTarget <= 0)
        {
            // Choice or beat indicates end of dialogue
            Debug.Log($"[DialogueManager] Choice target is {choice.target}, ending dialogue");
            EndDialogue();
        }
        else
        {
            // Advance to the choice's target beat
            Debug.Log($"[DialogueManager] Advancing to beat from choice target: {choiceTarget}");
            AdvanceToBeat(choiceTarget);
        }
    }

    private void AdvanceToBeat(float beatId)
    {
        if (beatId <= 0)
        {
            EndDialogue();
            return;
        }

        if (beatsByNumId.TryGetValue(beatId, out var beat))
        {
            DisplayBeat(beat);
            return;
        }

        if (beatsById.TryGetValue(beatId.ToString(), out beat))
        {
            DisplayBeat(beat);
            return;
        }

        Debug.LogError($"[DialogueManager] No beat found with ID '{beatId}'");
        EndDialogue();
    }

    private void ApplyToneEffects(BeatEffect[] effects)
    {
        if (effects == null) return;

        foreach (var effect in effects)
        {
            if (StatManager.Instance != null && effect.delta != 0)
            {
                var toneType = ParseTone(effect.stat);
                StatManager.Instance.AdjustPlayerTone(toneType, effect.delta, activeNpcId);
                Debug.Log($"[DialogueManager] Applied tone effect: {effect.stat} {effect.delta:+0.00;-0.00}");
            }
        }
    }

    private void ApplyRemnantsEffects(BeatEffect[] effects)
    {
        if (effects == null) return;

        foreach (var effect in effects)
        {
            if (StatManager.Instance != null && effect.delta != 0)
            {
                string target = effect.target == "activeNpcId" ? activeNpcId : effect.target;
                var remnantType = ParseRemnantType(effect.stat);
                Debug.Log($"[DialogueManager] Applied remnants effect: {target}.{effect.stat} {effect.delta:+0.00;-0.00}");
                // TODO: Apply to actual NPC remnants when system is ready
            }
        }
    }

    private DialogueMode InferMode(BeatData beat)
    {
        bool hasChoices = (beat.tone_choices != null && beat.tone_choices.Length > 0) 
                       || (beat.choices != null && beat.choices.Length > 0);

        if (beat.type == "npc_shared")
            return DialogueMode.NPCToNPC;
        
        if (beat.type == "player_posture" && hasChoices)
            return DialogueMode.PlayerActionChoice;
        
        if (beat.type == "npc_turn" && hasChoices)
            return DialogueMode.NPCToPlayer;
        
        if (beat.type == "player_posture" && !hasChoices)
            return DialogueMode.PlayerInnerThought;

        return hasChoices ? DialogueMode.NPCToPlayer : DialogueMode.NPCToNPC;
    }

    private ToneType ParseTone(string statName)
    {
        return statName.ToLower() switch
        {
            "trust" => ToneType.Trust,
            "observation" => ToneType.Observation,
            "narrative" or "narrativepresence" => ToneType.NarrativePresence,
            "empathy" => ToneType.Empathy,
            _ => ToneType.Trust
        };
    }

    private RemnantType ParseRemnantType(string statName)
    {
        return statName.ToLower() switch
        {
            "resolve" => RemnantType.Resolve,
            "empathy" => RemnantType.Empathy,
            "memory" => RemnantType.Memory,
            "nuance" => RemnantType.Nuance,
            "authority" => RemnantType.Authority,
            "need" => RemnantType.Need,
            "trust" => RemnantType.Trust,
            "skepticism" => RemnantType.Skepticism,
            _ => RemnantType.Trust
        };
    }

    private void ProcessSystemTriggers(string[] triggers, string[] diaryEntries = null)
    {
        if (triggers == null || triggers.Length == 0)
            return;

        // Process diary_update FIRST to ensure its notification is shown
        foreach (var trigger in triggers)
        {
            if (trigger == "diary_update" && diaryEntries != null && diaryEntries.Length > 0)
            {
                Debug.Log($"[DialogueManager] Passing {diaryEntries.Length} diary entries to TriggerSystemEvent");
                dialogueUI.TriggerSystemEvent(trigger, diaryEntries);
                break;
            }
        }

        // Then process all other triggers
        foreach (var trigger in triggers)
        {
            if (string.IsNullOrEmpty(trigger))
                continue;

            // Skip diary_update since we already processed it
            if (trigger == "diary_update")
                continue;

            // Handle flag-based triggers (e.g., "met_older_woman=true", "obtain_codex=true")
            if (trigger.Contains("="))
            {
                var parts = trigger.Split('=');
                if (parts.Length == 2)
                {
                    string flagName = parts[0].Trim();
                    string flagValue = parts[1].Trim();
                    
                    Debug.Log($"[DialogueManager] Flag set: {flagName} = {flagValue}");
                    
                    // Special handling for obtain_codex
                    if (flagName == "obtain_codex" && flagValue.ToLower() == "true")
                    {
                        dialogueUI.TriggerSystemEvent("give_device");
                    }
                    continue;
                }
            }

            // Handle other trigger names directly (e.g., "give_device", "npc_disappear")
            dialogueUI.TriggerSystemEvent(trigger);
            Debug.Log($"[DialogueManager] System trigger executed: {trigger}");
        }
    }

    /// <summary>
    /// Process beat-level system triggers (SystemTrigger objects with type and data fields).
    /// These are executed when the beat is displayed.
    /// </summary>
    private void ProcessBeatSystemTriggers(SystemTrigger[] triggers)
    {
        if (triggers == null || triggers.Length == 0)
            return;

        foreach (var trigger in triggers)
        {
            if (trigger == null || string.IsNullOrEmpty(trigger.type))
                continue;

            Debug.Log($"[DialogueManager] Processing beat system trigger: {trigger.type}");

            // Handle update_dialogue_names: replace placeholders with actual names
            if (trigger.type == "update_dialogue_names" && trigger.data != null && trigger.data.Length > 0)
            {
                foreach (var name in trigger.data)
                {
                    Debug.Log($"[DialogueManager] Character name revealed: {name}");
                }
                continue;
            }

            // Handle set_flag: persist flag globally
            if (trigger.type == "set_flag")
            {
                if (trigger.data != null && trigger.data.Length >= 1)
                {
                    string flagKey = trigger.data[0];
                    bool flagValue = trigger.data.Length >= 2 ? trigger.data[1] == "true" : true;
                    GameFlags.Set(flagKey, flagValue);
                    Debug.Log($"[DialogueManager] Flag set: {flagKey} = {flagValue}");
                }
                continue;
            }

            // Handle diary_append: create MindLog entry
            if (trigger.type == "diary_append")
            {
                if (trigger.data != null && trigger.data.Length >= 1)
                {
                    string content = trigger.data[0];
                    string title = trigger.data.Length >= 2 ? trigger.data[1] : "Encounter Log";
                    string logID = $"mindlog_{System.DateTime.Now.Ticks}";
                    
                    var entry = new MindLogEntry
                    {
                        LogID = logID,
                        Title = title,
                        Content = content,
                        Icon = "default_encounter",
                        Tags = new[] { "encounter", "memory" }
                    };
                    
                    Velinor.Management.MindLogManager.GetOrCreate().AddLog(entry);
                    Debug.Log($"[DialogueManager] MindLog entry added: {title}");
                }
                continue;
            }

            // Handle movement_speed: apply speed modifier to player
            if (trigger.type == "movement_speed")
            {
                if (trigger.data != null && trigger.data.Length >= 1)
                {
                    if (float.TryParse(trigger.data[0], out float speedModifier))
                    {
                        GameObject player = GameObject.FindGameObjectWithTag("Player");
                        if (player != null)
                        {
                            PlayerController2D5 playerController = player.GetComponent<PlayerController2D5>();
                            if (playerController != null)
                            {
                                playerController.SetMoveSpeed(speedModifier);
                                Debug.Log($"[DialogueManager] Player speed set to: {speedModifier}");
                            }
                        }
                    }
                }
                continue;
            }

            // Handle glyph_collect: trigger glyph collection gameplay
            if (trigger.type == "glyph_collect")
            {
                dialogueUI.TriggerSystemEvent("glyph_collect");
                Debug.Log($"[DialogueManager] Glyph collect triggered");
                continue;
            }

            // Handle close_dialogue: end the dialogue
            if (trigger.type == "close_dialogue")
            {
                dialogueUI.TriggerSystemEvent("close_dialogue");
                Debug.Log($"[DialogueManager] Close dialogue triggered");
                continue;
            }

            // Handle other custom triggers by passing type as event
            dialogueUI.TriggerSystemEvent(trigger.type, trigger.data);
            Debug.Log($"[DialogueManager] System trigger executed: {trigger.type}");
        }
    }

    private void EndDialogue()
    {
        Debug.Log($"[DialogueManager] EndDialogue called. CurrentBeat: {currentBeat?.id ?? 0}, has mind_log_unlocks: {(currentBeat?.mind_log_unlocks != null && currentBeat.mind_log_unlocks.Length > 0)}");
        
        // Process Mind Log unlocks from current beat before ending dialogue
        if (currentBeat != null && currentBeat.mind_log_unlocks != null && currentBeat.mind_log_unlocks.Length > 0)
        {
            Debug.Log($"[DialogueManager] Processing {currentBeat.mind_log_unlocks.Length} mind log unlocks");
            ProcessMindLogUnlocks(currentBeat.mind_log_unlocks);
        }
        else
        {
            Debug.Log("[DialogueManager] No mind log unlocks to process");
        }

        // Reset append flag
        lastActionWasNpcResponse = false;

        isDialogueActive = false;
        currentBeat = null;
        if (portraitManager != null)
        {
            portraitManager.HidePortrait();
        }
        if (voiceoverManager != null)
        {
            voiceoverManager.StopVoiceover();
        }
        dialogueUI.HideDialogue();
        Debug.Log("[DialogueManager] Dialogue ended");
        OnDialogueEnded?.Invoke();
    }

    /// <summary>
    /// Process Mind Log unlocks from dialogue beat.
    /// This also unlocks the Codex when the first memory is obtained.
    /// </summary>
    private void ProcessMindLogUnlocks(MindLogUnlock[] unlocks)
    {
        if (unlocks == null || unlocks.Length == 0)
        {
            return;
        }

        var mindLogManager = MindLogManager.GetOrCreate();
        if (mindLogManager == null)
        {
            Debug.LogError("[DialogueManager] Failed to get or create MindLogManager");
            return;
        }

        bool anySuccessfullyAdded = false;

        foreach (var unlock in unlocks)
        {
            if (string.IsNullOrEmpty(unlock.assetPath))
            {
                Debug.LogWarning("[DialogueManager] Mind Log unlock has empty assetPath");
                continue;
            }

            // Load the MindLogAsset from Resources
            Debug.Log($"[DialogueManager] Attempting to load Mind Log asset: {unlock.assetPath}");
            var asset = Resources.Load<MindLogAsset>(unlock.assetPath);
            if (asset == null)
            {
                Debug.LogError($"[DialogueManager] Failed to load Mind Log asset: {unlock.assetPath}");
                Debug.LogError($"[DialogueManager] Trying alternate load from: Assets/Resources/{unlock.assetPath}.asset");
                continue;
            }

            // Convert asset to entry and add to manager
            var entry = asset.ToEntry();
            mindLogManager.AddLog(entry);
            Debug.Log($"[DialogueManager] Added Mind Log: {entry.LogID}");
            anySuccessfullyAdded = true;
        }

        // If any memories were successfully added, unlock the Codex
        if (anySuccessfullyAdded)
        {
            MindLogPersistence.UnlockCodex();
            Debug.Log("[DialogueManager] CODEX UNLOCKED - Player can now access the Mind Log!");
        }
    }

    public GameObject GetCurrentNPCGameObject()
    {
        if (string.IsNullOrEmpty(activeNpcId))
            return null;

        // Try to find NPC by name in scene
        GameObject npc = GameObject.Find(activeNpcId);
        if (npc != null)
            return npc;

        // Fallback: search all GameObjects in scene for matching name
        foreach (var obj in FindObjectsByType<MonoBehaviour>())
        {
            if (obj.gameObject.name == activeNpcId)
                return obj.gameObject;
        }

        return null;
    }

    public bool IsDialogueActive => isDialogueActive;
}
