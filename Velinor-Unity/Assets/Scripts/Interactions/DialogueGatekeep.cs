using UnityEngine;
using Velinor.Core;
using System.Collections.Generic;

/// <summary>
/// Dialogue Gatekeep System
/// 
/// Prevents player progression until dialogue is complete.
/// - Keeps forward colliders DISABLED until dialogue ends
/// - When dialogue ends AND completion flag is set, enables forward colliders
/// - Allows safe scene backtracking at any time
/// 
/// Usage:
/// 1. Create child GameObjects for each dialogue interaction:
///    - "Gate_Ravi_Nima" containing disabled forward colliders
/// 2. Add a StartDialogueOnTrigger to your NPC collider that:
///    - Sets a GameFlag on dialogue completion (e.g., "ravi_nima_dialogue_complete")
/// 3. Create this DialogueGatekeep script on a scene root manager
/// 4. In inspector, set up gates with:
///    - Completion flag name (must match StartDialogueOnTrigger's flag)
///    - NPC ID (for documentation; not used for logic)
///    - List of colliders to enable after dialogue completes
///    - Optional: colliders to disable after dialogue completes
/// 5. Script subscribes to DialogueManager.OnDialogueEnded
/// 6. When dialogue ends, checks if completion flag is true, enables corresponding colliders
/// 
/// Example Scene Setup - InsideMarket_00:
/// ├── [DialogueGatekeep] (this script on root)
/// ├── Collider_Back_To_Entrance (ALWAYS enabled - safe to use anytime)
/// ├── DialogueGates/
/// │   └── Gate_Ravi_Nima/
/// │       ├── Collider_To_Market_01_01 (disabled initially)
/// │       └── Collider_To_Market_01_02 (disabled initially, alt path)
/// └── Ravi + Nima NPCs
///     └── [StartDialogueOnTrigger] (sets "ravi_nima_dialogue_complete" flag)
/// 
/// Flow:
/// 1. Player enters InsideMarket_00
/// 2. Tries to move forward, hits disabled collider, can't progress
/// 3. Approaches Ravi/Nima, dialogue starts (StartDialogueOnTrigger handles it)
/// 4. Dialogue completes
/// 5. StartDialogueOnTrigger's callback sets "ravi_nima_dialogue_complete" flag
/// 6. DialogueManager.OnDialogueEnded fires
/// 7. DialogueGatekeep.HandleDialogueEnded() checks flag, finds it's true
/// 8. Enables Gate_Ravi_Nima colliders
/// 9. Player can now progress forward
/// 10. If player revisits InsideMarket_00_02 (backtrack version):
///     - Flag remains set (persistent in GameFlags)
///     - Gate colliders remain enabled
///     - Player can exit freely
/// </summary>
public class DialogueGatekeep : MonoBehaviour
{
    [System.Serializable]
    public class DialogueGate
    {
        [Tooltip("Flag to set when this dialogue completes (e.g., 'ravi_nima_dialogue_complete')")]
        public string completionFlag;

        [Tooltip("NPC ID that triggers this dialogue (e.g., 'Ravi', 'Nima', 'player')")]
        public string npcId;

        [Tooltip("Colliders to enable when this dialogue completes (forward gates)")]
        public List<Collider> forwardColliders = new List<Collider>();

        [Tooltip("Optional: Colliders to disable when this dialogue completes (e.g., blocked areas)")]
        public List<Collider> collidersThenDisable = new List<Collider>();
    }

    [SerializeField] private List<DialogueGate> dialogueGates = new List<DialogueGate>();

    private void OnEnable()
    {
        // Subscribe to dialogue completion
        if (DialogueManager.Instance != null)
        {
            DialogueManager.Instance.OnDialogueEnded += HandleDialogueEnded;
            Debug.Log("[DialogueGatekeep] Subscribed to DialogueManager.OnDialogueEnded");
        }
        else
        {
            Debug.LogWarning("[DialogueGatekeep] DialogueManager.Instance is null on OnEnable!");
        }
    }

    private void OnDisable()
    {
        // Unsubscribe from dialogue completion
        if (DialogueManager.Instance != null)
        {
            DialogueManager.Instance.OnDialogueEnded -= HandleDialogueEnded;
        }
    }

    /// <summary>
    /// Called when any dialogue ends.
    /// Enables colliders for any gate whose flag has been set.
    /// (The dialogue trigger should have already set the completion flag.)
    /// </summary>
    private void HandleDialogueEnded()
    {
        Debug.Log("[DialogueGatekeep] Dialogue ended - checking gates...");

        // Check all gates: if flag is set, enable forward colliders
        foreach (var gate in dialogueGates)
        {
            if (GameFlags.Get(gate.completionFlag))
            {
                // Flag is set - enable forward colliders for this gate
                Debug.Log($"[DialogueGatekeep] Gate flag is set: {gate.completionFlag} - enabling forward colliders");

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
    }

    /// <summary>
    /// Public method to manually unlock a gate (useful for debugging or alt paths).
    /// </summary>
    public void UnlockGate(string completionFlag)
    {
        foreach (var gate in dialogueGates)
        {
            if (gate.completionFlag == completionFlag)
            {
                GameFlags.Set(gate.completionFlag, true);

                foreach (var collider in gate.forwardColliders)
                {
                    if (collider != null) collider.enabled = true;
                }

                Debug.Log($"[DialogueGatekeep] Gate manually unlocked: {completionFlag}");
                return;
            }
        }

        Debug.LogWarning($"[DialogueGatekeep] Gate not found: {completionFlag}");
    }
}
