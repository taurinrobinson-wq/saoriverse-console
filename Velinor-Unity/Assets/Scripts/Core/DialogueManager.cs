using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

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

    private Dictionary<string, BeatData> beatsById = new Dictionary<string, BeatData>();
    private Dictionary<float, BeatData> beatsByNumId = new Dictionary<float, BeatData>();
    private BeatData currentBeat;
    private bool isDialogueActive = false;
    private string activeNpcId;

    public System.Action OnDialogueEnded;

    private void Awake()
    {
        if (Instance != null && Instance != this) { Destroy(gameObject); return; }
        Instance = this;
        DontDestroyOnLoad(gameObject);
        
        dialogueUI = FindAnyObjectByType<DialogueUIController>();
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
                foreach (var beat in root.beats)
                {
                    beatsByNumId[beat.id] = beat;
                    beatsById[beat.id.ToString()] = beat; // Also index by string ID
                    beat.mode = InferMode(beat);
                    Debug.Log($"[DialogueManager] Loaded beat: {beat.id} (mode: {beat.mode})");
                }
                Debug.Log($"[DialogueManager] Loaded {beatsByNumId.Count} beats from beats format");
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
        activeNpcId = npcId;
        isDialogueActive = true;

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

        Debug.Log($"[DialogueManager] Displaying beat: {beat.pid ?? beat.id.ToString()} (mode: {beat.mode})");

        // Check if beat has choices
        bool hasChoices = (beat.tone_choices != null && beat.tone_choices.Length > 0) ||
                         (beat.choices != null && beat.choices.Length > 0);

        // Show shared_beat if it exists AND there are NO choices (auto-advance dialogue)
        if (!string.IsNullOrEmpty(beat.shared_beat) && !hasChoices)
        {
            dialogueUI.ShowSpeaker(beat.active_speaker ?? "");
            dialogueUI.ShowText(beat.shared_beat);
            dialogueUI.ShowSharedBeat(beat.shared_beat);
            StartCoroutine(AutoAdvanceAfterSharedBeat(beat));
            return;
        }

        // If there are choices, show prompt + shared_beat + choices together
        if (hasChoices)
        {
            dialogueUI.HideSharedBeat();
            
            // Show prompt
            dialogueUI.ShowSpeaker(beat.active_speaker ?? "");
            dialogueUI.ShowText(beat.prompt ?? "");
            
            // Show shared_beat if it exists (displayed along with prompt)
            if (!string.IsNullOrEmpty(beat.shared_beat))
            {
                dialogueUI.ShowSharedBeat(beat.shared_beat);
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
        dialogueUI.ShowSpeaker(beat.active_speaker ?? "");
        dialogueUI.ShowText(beat.prompt ?? "");
    }

    private IEnumerator AutoAdvanceAfterSharedBeat(BeatData beat)
    {
        yield return dialogueUI.WaitForDisplayComplete();
        
        // Advance to next beat
        float nextId = beat.next_beat_id > 0 ? beat.next_beat_id : (beat.id + 1);
        AdvanceToBeat(nextId);
    }

    private IEnumerator ResolveChoiceCoroutine(BeatData beat, BeatChoice choice)
    {
        dialogueUI.ClearButtons();
        Debug.Log($"[DialogueManager] Choice selected: {choice.text}");

        // 1. Show result_text if it exists
        if (!string.IsNullOrEmpty(choice.result_text))
        {
            Debug.Log($"[DialogueManager] Showing result_text: {choice.result_text}");
            dialogueUI.ShowSpeaker("");
            dialogueUI.ShowText(choice.result_text);
            yield return new WaitForEndOfFrame(); // Just let UI render
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
            dialogueUI.ShowSpeaker(beat.active_speaker ?? "");
            dialogueUI.ShowText(choice.npc_response);
            dialogueUI.HideSharedBeat();
            
            // Always show E "Continue" button and wait for player to click it
            BeatData continueBeat = new BeatData
            {
                id = beat.id,
                active_speaker = beat.active_speaker,
                tone_choices = new BeatChoice[]
                {
                    new BeatChoice
                    {
                        tone = "E",
                        label = "Continue",
                        text = "Continue",
                        result_text = "",
                        npc_response = ""
                    }
                }
            };
            
            float nextBeatId = beat.next_beat_id > 0 ? beat.next_beat_id : (beat.id + 1);
            Debug.Log($"[DialogueManager] Continue button will advance to beat: {nextBeatId}");
            
            dialogueUI.ShowChoices(continueBeat, choice => 
            {
                Debug.Log($"[DialogueManager] Continue button clicked, advancing to beat: {nextBeatId}");
                AdvanceToBeat(nextBeatId);
            });
            
            yield break;
        }

        // 4. No npc_response: Check if there are choices to show
        bool hasChoices = (beat.tone_choices != null && beat.tone_choices.Length > 0) ||
                         (beat.choices != null && beat.choices.Length > 0);
        
        if (hasChoices)
        {
            // Show the choices and wait for player selection
            dialogueUI.ShowChoices(beat, choice => StartCoroutine(ResolveChoiceCoroutine(beat, choice)));
            yield break;
        }

        // 5. No npc_response and no choices: check if we should end dialogue or advance
        if (beat.next_beat_id <= 0)
        {
            // next_beat_id is 0 or negative = end dialogue
            EndDialogue();
        }
        else
        {
            // Advance to next beat
            AdvanceToBeat(beat.next_beat_id);
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

        foreach (var trigger in triggers)
        {
            if (string.IsNullOrEmpty(trigger))
                continue;

            // Handle flag-based triggers (e.g., "met_older_woman=true", "obtain_codex=true")
            if (trigger.Contains("="))
            {
                var parts = trigger.Split('=');
                if (parts.Length == 2)
                {
                    string flagName = parts[0].Trim();
                    string flagValue = parts[1].Trim();
                    
                    // Set the flag in some flag system (TODO: implement flag manager if needed)
                    Debug.Log($"[DialogueManager] Flag set: {flagName} = {flagValue}");
                    
                    // Special handling for obtain_codex
                    if (flagName == "obtain_codex" && flagValue.ToLower() == "true")
                    {
                        dialogueUI.TriggerSystemEvent("give_device");
                    }
                    continue;
                }
            }

            // Handle trigger names directly (e.g., "give_device", "diary_update", "npc_disappear")
            if (trigger == "diary_update" && diaryEntries != null && diaryEntries.Length > 0)
            {
                // Pass diary entries to the event
                dialogueUI.TriggerSystemEvent(trigger, diaryEntries);
            }
            else
            {
                dialogueUI.TriggerSystemEvent(trigger);
            }
            Debug.Log($"[DialogueManager] System trigger executed: {trigger}");
        }
    }

    private void EndDialogue()
    {
        isDialogueActive = false;
        currentBeat = null;
        dialogueUI.HideDialogue();
        Debug.Log("[DialogueManager] Dialogue ended");
        OnDialogueEnded?.Invoke();
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
        foreach (var obj in FindObjectsByType<MonoBehaviour>(FindObjectsSortMode.None))
        {
            if (obj.gameObject.name == activeNpcId)
                return obj.gameObject;
        }

        return null;
    }

    public bool IsDialogueActive => isDialogueActive;
}
