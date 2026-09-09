using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Beat-based dialogue runner for Velinor.
/// Manages dialogue flow, player choices, NPC responses, and stat effects.
/// 
/// Core concept: A beat is the fundamental unit of dialogue.
/// Each beat has text, optional choices, and optional NPC responses.
/// The system advances based on player choices or auto-advance to next beat.
/// </summary>
public class DialogueManager : MonoBehaviour
{
    public static DialogueManager Instance { get; private set; }

    [SerializeField] private TextAsset dialogueJson;
    private DialogueUIController dialogueUI;

    private Dictionary<string, BeatData> beatsById = new Dictionary<string, BeatData>();
    private BeatData currentBeat;
    private bool isDialogueActive = false;
    private string currentConversationId;
    private string activeNpcId;

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

            // Try passages format first (name, passages, startnode)
            try
            {
                var root = JsonUtility.FromJson<DialogueJson>(dialogueJson.text);
                if (root != null && root.passages != null && root.passages.Length > 0)
                {
                    LoadFromPassages(root);
                    return;
                }
            }
            catch { }

            // Try beats format (scene_id, beats, required_flags)
            // For now, log warning - we'll implement this next
            Debug.LogWarning("[DialogueManager] JSON format not recognized. Expected 'passages' or 'beats' array.");
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"[DialogueManager] Error parsing dialogue JSON: {ex.Message}");
        }
    }

    private void LoadFromPassages(DialogueJson root)
    {
        if (root == null || root.passages == null)
        {
            Debug.LogError("[DialogueManager] Passages root is null");
            return;
        }

        foreach (var beat in root.passages)
        {
            // Derive the tone from tone_str in each choice
            if (beat.choices != null)
            {
                foreach (var choice in beat.choices)
                {
                    choice.tone = DeriveTonesFromStr(choice.tone_str);
                }
            }

            // Infer the dialogue mode for this beat (based on presence of choices)
            beat.mode = InferModeFromPassage(beat);
            beatsById[beat.pid] = beat;
            
            Debug.Log($"[DialogueManager] Loaded beat: {beat.pid} (mode: {beat.mode})");
        }

        Debug.Log($"[DialogueManager] Loaded {beatsById.Count} beats from passages format");
    }

    private string DeriveTonesFromStr(string tone_str)
    {
        if (string.IsNullOrEmpty(tone_str)) return "T";
        return tone_str switch
        {
            "Trust" => "T",
            "Observation" => "O",
            "NarrativePresence" => "N",
            "Narrative" => "N",
            "Empathy" => "E",
            _ => tone_str
        };
    }

    private DialogueMode InferModeFromPassage(BeatData beat)
    {
        // Simple rule: if beat has choices, it's NPCToPlayer
        // Otherwise, we'd need more info to distinguish, so default to NPCToNPC
        if (beat.choices != null && beat.choices.Length > 0)
        {
            return DialogueMode.NPCToPlayer;
        }
        return DialogueMode.NPCToNPC;
    }

    public void StartDialogue(string npcId, string startBeatPid)
    {
        if (!beatsById.ContainsKey(startBeatPid))
        {
            Debug.LogError($"[DialogueManager] No beat with pid '{startBeatPid}'");
            return;
        }

        activeNpcId = npcId;
        currentConversationId = beatsById[startBeatPid].conversationId;
        isDialogueActive = true;

        var startBeat = beatsById[startBeatPid];
        DisplayBeat(startBeat);
    }

    private void DisplayBeat(BeatData beat)
    {
        currentBeat = beat;
        dialogueUI.ClearButtons();

        Debug.Log($"[DialogueManager] Displaying beat: {beat.pid} (mode: {beat.mode})");

        switch (beat.mode)
        {
            case DialogueMode.NPCToNPC:
                // NPC speaks, dialogue auto-continues to next beat
                DisplayNpcLine(beat);
                HandleAutoAdvance(beat);
                break;

            case DialogueMode.NPCToPlayer:
                // NPC speaks, player chooses, NPC responds
                DisplayNpcLine(beat);
                DisplayChoices(beat);
                break;

            case DialogueMode.PlayerInnerThought:
                // Player monologue, auto-continues
                DisplayPlayerThought(beat);
                HandleAutoAdvance(beat);
                break;

            case DialogueMode.PlayerActionChoice:
                // Player chooses an action
                DisplayPlayerLine(beat);
                DisplayChoices(beat);
                break;
        }
    }

    private void DisplayNpcLine(BeatData beat)
    {
        // For passages format, we don't have explicit speaker, so just show the NPC name from conversationId context
        // TODO: Derive NPC name from conversationId or context
        dialogueUI.ShowSpeaker("");  // Passages format doesn't have explicit speaker data
        dialogueUI.ShowText(beat.text);
    }

    private void DisplayPlayerThought(BeatData beat)
    {
        dialogueUI.HideSpeaker();
        dialogueUI.ShowText(beat.text);
    }

    private void DisplayPlayerLine(BeatData beat)
    {
        dialogueUI.ShowSpeaker(""); // or "Player" if you want
        dialogueUI.ShowText(beat.text);
    }

    private void DisplayChoices(BeatData beat)
    {
        Debug.Log($"[DialogueManager] DisplayChoices called for beat: {beat.pid}");
        Debug.Log($"[DialogueManager]   - choices present: {beat.choices != null}");
        Debug.Log($"[DialogueManager]   - choices length: {beat.choices?.Length ?? 0}");
        
        if (beat.choices == null || beat.choices.Length == 0)
        {
            Debug.Log($"[DialogueManager] No choices to display");
            return;
        }

        dialogueUI.ShowChoices(beat, choice => StartCoroutine(ResolveChoiceCoroutine(choice)));
    }

    private void HandleAutoAdvance(BeatData beat)
    {
        // For auto-advancing beats (NPCToNPC, PlayerInnerThought)
        // If there's a single [Continue] choice, show it
        if (beat.choices != null && beat.choices.Length == 1)
        {
            dialogueUI.ShowChoices(beat, choice => StartCoroutine(ResolveChoiceCoroutine(choice)));
        }
        else
        {
            // No choices: just show beat and end dialogue
            StartCoroutine(AutoAdvanceAfterDisplay(beat));
        }
    }

    private IEnumerator AutoAdvanceAfterDisplay(BeatData beat)
    {
        yield return dialogueUI.WaitForDisplayComplete();
        
        if (beat.choices != null && beat.choices.Length == 1)
        {
            yield return ResolveChoiceCoroutine(beat.choices[0]);
        }
        else
        {
            EndDialogue();
        }
    }

    private IEnumerator ResolveChoiceCoroutine(BeatChoice choice)
    {
        dialogueUI.ClearButtons();
        Debug.Log($"[DialogueManager] ResolveChoiceCoroutine: playerLine={choice.playerLine}, target={choice.target}");

        // 1. Apply TONE and REMNANTS effects if present
        ApplyToneEffectsFromWrapper(choice.tone_effects);
        ApplyNpcResonanceEffects(choice.npc_resonance);

        // 2. Show NPC response (shared_beat) if appropriate
        if (!string.IsNullOrEmpty(choice.shared_beat))
        {
            Debug.Log($"[DialogueManager] Showing NPC response (shared_beat): {choice.shared_beat}");
            // For passages format, we don't have explicit speaker info, so just show the response
            dialogueUI.ShowSpeaker(""); // TODO: determine speaker from context
            dialogueUI.ShowText(choice.shared_beat);
            yield return dialogueUI.WaitForDisplayComplete();
            
            // Wait for player to continue before advancing to next beat
            Debug.Log($"[DialogueManager] Waiting for player to continue before advancing to {choice.target}");
            yield return dialogueUI.WaitForPlayerContinue();
            Debug.Log($"[DialogueManager] Player continued, now advancing to {choice.target}");
        }
        else
        {
            Debug.Log($"[DialogueManager] No NPC response to show (shared_beat is empty)");
        }

        // 3. Advance to next beat or end dialogue
        if (choice.target == "DIALOGUE_END")
        {
            Debug.Log($"[DialogueManager] Dialogue ended");
            EndDialogue();
            yield break;
        }

        if (!beatsById.TryGetValue(choice.target, out var nextBeat))
        {
            Debug.LogError($"[DialogueManager] No beat with pid '{choice.target}'");
            EndDialogue();
            yield break;
        }

        Debug.Log($"[DialogueManager] Advancing to next beat: {choice.target}");
        DisplayBeat(nextBeat);
    }

    private void ApplyToneEffectsFromWrapper(EffectWrapper wrapper)
    {
        if (wrapper == null || wrapper.entries == null) return;

        foreach (var entry in wrapper.entries)
        {
            if (StatManager.Instance != null)
            {
                // Convert stat name to ToneType and apply
                var toneType = ParseTone(entry.key);
                StatManager.Instance.AdjustPlayerTone(toneType, entry.value, activeNpcId);
                Debug.Log($"[DialogueManager] Applied tone effect: {entry.key} {entry.value:+0.00;-0.00}");
            }
        }
    }

    private void ApplyNpcResonanceEffects(EffectWrapper wrapper)
    {
        if (wrapper == null || wrapper.entries == null) return;

        foreach (var entry in wrapper.entries)
        {
            if (StatManager.Instance != null)
            {
                // entry.key is NPC name (e.g., "OlderWoman")
                // entry.value is the delta
                Debug.Log($"[DialogueManager] Applied NPC resonance effect: {entry.key} {entry.value:+0.00;-0.00}");
                // TODO: Implement NPC resonance/affinity system
            }
        }
    }

    private DialogueMode InferModeFromBeat(BeatData beat)
    {
        // This method is now deprecated - use InferModeFromPassage instead
        return InferModeFromPassage(beat);
    }

    private string ResolveSpeakerName(string activeSpeaker)
    {
        if (string.IsNullOrEmpty(activeSpeaker) || activeSpeaker == "Shared")
            return "";
        return activeSpeaker;
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

    private void EndDialogue()
    {
        isDialogueActive = false;
        currentBeat = null;
        dialogueUI.ClearButtons();
        dialogueUI.HideSpeaker();
        Debug.Log("[DialogueManager] Dialogue ended");
        OnDialogueEnded?.Invoke();
    }

    public bool IsDialogueActive => isDialogueActive;

    /// <summary>
    /// Event fired when dialogue ends.
    /// </summary>
    public event System.Action OnDialogueEnded;

    /// <summary>
    /// Get the current NPC's game object for animations or other NPC-specific logic.
    /// </summary>
    private GameObject currentNpcGameObject;
    public GameObject GetCurrentNPCGameObject() => currentNpcGameObject;
}
