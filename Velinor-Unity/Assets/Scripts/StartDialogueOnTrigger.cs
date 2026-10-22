using UnityEngine;
using StarterAssets;
using Velinor.Core;

public class StartDialogueOnTrigger : MonoBehaviour
{
    [Header("Dialogue")]
    [SerializeField] private string npcId = "Kaelen";
    [SerializeField] private string startingPassageId = "beat_1";
    [SerializeField] private TextAsset dialogueJson; // Drag the dialogue JSON here
    [SerializeField] private string requiredFlag = "completed_willy";
    [SerializeField] private bool requireFlag = true;

    [Header("Movement")]
    [SerializeField] private bool lockPlayerMovement = true;

    private bool hasTriggered;
    private string completionFlag; // Automatically extracted from dialogue JSON

    private void OnTriggerEnter(Collider other)
    {
        if (hasTriggered) return;
        if (!other.CompareTag("Player")) return;

        if (requireFlag && !GameFlags.Get(requiredFlag))
            return;

        hasTriggered = true;

        if (lockPlayerMovement)
        {
            var playerController = other.GetComponentInParent<VelinorPlayerController>();
            if (playerController != null)
            {
                playerController.enabled = false;
            }
        }

        if (DialogueManager.Instance != null)
        {
            // Use the dialogueJson directly
            if (dialogueJson == null)
            {
                Debug.LogError($"[StartDialogueOnTrigger] dialogueJson is not assigned!");
                return;
            }

            DialogueManager.Instance.LoadDialogue(dialogueJson);

            // Extract completion flag from JSON
            ExtractCompletionFlagFromJson();

            // Subscribe to dialogue end event
            DialogueManager.Instance.OnDialogueEnded -= HandleDialogueEnded;
            DialogueManager.Instance.OnDialogueEnded += HandleDialogueEnded;
            
            // Start dialogue at specified beat
            DialogueManager.Instance.StartDialogue(npcId, startingPassageId);
        }
    }

    private void HandleDialogueEnded()
    {
        // Set completion flag if it was extracted from JSON
        if (!string.IsNullOrEmpty(completionFlag))
        {
            GameFlags.Set(completionFlag, true);
            Debug.Log($"[StartDialogueOnTrigger] Set completion flag: {completionFlag}");
        }

        if (lockPlayerMovement)
        {
            var player = GameObject.FindGameObjectWithTag("Player");
            if (player != null)
            {
                var playerController = player.GetComponentInChildren<VelinorPlayerController>();
                if (playerController != null)
                {
                    playerController.enabled = true;
                }
            }
        }

        // Unsubscribe
        if (DialogueManager.Instance != null)
        {
            DialogueManager.Instance.OnDialogueEnded -= HandleDialogueEnded;
        }

        // Reset for potential retrigger
        hasTriggered = false;
    }

    /// <summary>
    /// Extracts the completionFlag from the dialogue JSON.
    /// Looks for a "completionFlag" field at the root level of the JSON.
    /// </summary>
    private void ExtractCompletionFlagFromJson()
    {
        if (dialogueJson == null)
        {
            Debug.LogWarning("[StartDialogueOnTrigger] dialogueJson is null, cannot extract completion flag");
            return;
        }

        try
        {
            var json = JsonUtility.FromJson<DialogueMetadata>(dialogueJson.text);
            if (json != null && !string.IsNullOrEmpty(json.completionFlag))
            {
                completionFlag = json.completionFlag;
                Debug.Log($"[StartDialogueOnTrigger] Extracted completion flag from JSON: {completionFlag}");
            }
            else
            {
                Debug.LogWarning($"[StartDialogueOnTrigger] No completionFlag found in dialogue JSON");
                completionFlag = null;
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[StartDialogueOnTrigger] Failed to parse JSON: {e.Message}");
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

