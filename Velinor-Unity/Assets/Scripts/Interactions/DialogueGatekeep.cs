using UnityEngine;
using Velinor.Core;
using System.Collections.Generic;

/// <summary>
/// Dialogue Gatekeep System (Refactored)
/// 
/// Now works with dialogue JSON files directly. Simply:
/// 1. Drag the same dialogue JSON into the gatekeepJson field
/// 2. Add the dialogueGates list with colliders to enable/disable
/// 3. The system automatically extracts completionFlag from the JSON
/// 
/// Flow:
/// 1. Player enters scene with gated collider (disabled)
/// 2. Dialogue starts (StartDialogueOnTrigger handles it)
/// 3. Dialogue completes, StartDialogueOnTrigger sets the flag from JSON
/// 4. DialogueGatekeep detects flag is set, enables forward colliders
/// 5. Player can progress
/// </summary>
public class DialogueGatekeep : MonoBehaviour
{
    [System.Serializable]
    public class DialogueGate
    {
        [Tooltip("Colliders to enable when dialogue completes")]
        public List<Collider> forwardColliders = new List<Collider>();

        [Tooltip("Optional: Colliders to disable when dialogue completes")]
        public List<Collider> collidersThenDisable = new List<Collider>();
    }

    [SerializeField] private TextAsset gatekeepJson; // Drag the dialogue JSON here - it extracts the completionFlag automatically
    [SerializeField] private List<DialogueGate> dialogueGates = new List<DialogueGate>();

    private string completionFlag;
    private bool gateUnlocked = false;

    private void Start()
    {
        // Extract completion flag from JSON
        ExtractCompletionFlagFromJson();

        // Subscribe to dialogue completion
        if (DialogueManager.Instance != null)
        {
            DialogueManager.Instance.OnDialogueEnded += HandleDialogueEnded;
            Debug.Log("[DialogueGatekeep] Subscribed to DialogueManager.OnDialogueEnded");
        }
        else
        {
            Debug.LogWarning("[DialogueGatekeep] DialogueManager.Instance is null on Start!");
        }

        // Check if gate is already unlocked (e.g., on scene reload)
        CheckAndUnlockGate();
    }

    private void OnDisable()
    {
        if (DialogueManager.Instance != null)
        {
            DialogueManager.Instance.OnDialogueEnded -= HandleDialogueEnded;
        }
    }

    private void HandleDialogueEnded()
    {
        Debug.Log("[DialogueGatekeep] Dialogue ended - checking gate...");
        CheckAndUnlockGate();
    }

    private void CheckAndUnlockGate()
    {
        if (gateUnlocked) return; // Already unlocked, no need to check again
        if (string.IsNullOrEmpty(completionFlag)) return;

        if (GameFlags.Get(completionFlag))
        {
            Debug.Log($"[DialogueGatekeep] Gate flag is set: {completionFlag} - enabling forward colliders");
            UnlockGate();
        }
    }

    private void UnlockGate()
    {
        gateUnlocked = true;

        foreach (var gate in dialogueGates)
        {
            // Enable forward colliders
            foreach (var collider in gate.forwardColliders)
            {
                if (collider != null)
                {
                    collider.enabled = true;
                    Debug.Log($"[DialogueGatekeep] Enabled forward collider: {collider.gameObject.name}");
                }
            }

            // Disable blocked colliders (if any)
            foreach (var collider in gate.collidersThenDisable)
            {
                if (collider != null)
                {
                    collider.enabled = false;
                    Debug.Log($"[DialogueGatekeep] Disabled collider: {collider.gameObject.name}");
                }
            }
        }
    }

    /// <summary>
    /// Extracts the completionFlag from the dialogue JSON.
    /// </summary>
    private void ExtractCompletionFlagFromJson()
    {
        if (gatekeepJson == null)
        {
            Debug.LogWarning("[DialogueGatekeep] gatekeepJson is not assigned!");
            return;
        }

        try
        {
            var json = JsonUtility.FromJson<DialogueMetadata>(gatekeepJson.text);
            if (json != null && !string.IsNullOrEmpty(json.completionFlag))
            {
                completionFlag = json.completionFlag;
                Debug.Log($"[DialogueGatekeep] Extracted completion flag from JSON: {completionFlag}");
            }
            else
            {
                Debug.LogWarning($"[DialogueGatekeep] No completionFlag found in dialogue JSON");
                completionFlag = null;
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[DialogueGatekeep] Failed to parse JSON: {e.Message}");
            completionFlag = null;
        }
    }

    /// <summary>
    /// Minimal wrapper to extract just the completionFlag from dialogue JSON.
    /// </summary>
    [System.Serializable]
    private class DialogueMetadata
    {
        public string completionFlag;
    }
}

