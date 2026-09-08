using UnityEngine;
using TMPro;
using Velinor.Core;

namespace Velinor.Core
{
    /// <summary>
    /// NPCDialogueDriver: Generic NPC dialogue trigger that replaces SaoriNPC.
    /// Supports:
    /// - Any JSON dialogue file (configurable via Inspector)
    /// - Single-NPC and multi-NPC scenes
    /// - Optional movement driver (NPCController)
    /// - All original SaoriNPC functionality (billboard effect, collider setup, etc.)
    /// </summary>
    public class NPCDialogueDriver : MonoBehaviour, IInteractable
    {
        [Header("Dialogue Configuration")]
        [SerializeField] private TextAsset dialogueJson;           // Assign dialogue JSON in Inspector
        [SerializeField] private string conversationId;            // e.g. "saori_encounter_01", "nima_encounter_01"
        [SerializeField] private string npcName = "NPC";           // "Saori", "Nima", "Ravi", "Willy", "Kaelen"
        [SerializeField] private string startPassageId = "start";  // Fallback start passage
        [SerializeField] private bool isMultiNpcScene = false;     // Set true for scenes like ravi_nima_market_discovery
        [SerializeField] private string multiNpcDisplayName = "[Multiple NPCs]";  // Display name for multi-NPC scenes, e.g. "Young Man and Woman"

        [Header("Movement")]
        [SerializeField] private NPCController npcController;      // Optional movement driver

        [Header("Interaction")]
        [SerializeField] private float interactionRadius = 0.8f;

        [Header("Transform Configuration")]
        [SerializeField] private Vector3 npcScale = new Vector3(1.8f, 1.8f, 1.8f);
        [SerializeField] private bool useDefaultScale = true;

        [Header("Collider Configuration")]
        [SerializeField] private float colliderHeight = 1.5f;
        [SerializeField] private float colliderRadius = 0.3f;
        [SerializeField] private bool useDefaultCollider = true;

        [Header("Billboard Effect")]
        [SerializeField] private bool enableBillboardEffect = true;

        private bool playerInRange = false;
        private GameObject player;
        private bool notificationShown = false;
        private bool isExiting = false;

        private DialogueManager dialogueManager;

        // Track which JSON was last processed to detect changes in OnValidate
        private TextAsset lastProcessedJson = null;

        private void Awake()
        {
            dialogueManager = FindAnyObjectByType<DialogueManager>();

            // Fix any baked-in X rotation (e.g., Asuna skeleton)
            Vector3 eulerAngles = transform.localEulerAngles;
            eulerAngles.x = 0f;
            transform.localEulerAngles = eulerAngles;
            Debug.Log($"[NPCDialogueDriver] {npcName}: X rotation corrected to 0");

            // Apply scale if enabled
            if (useDefaultScale)
            {
                transform.localScale = npcScale;
                Debug.Log($"[NPCDialogueDriver] {npcName}: Applied scale {npcScale}");
            }

            // Clean up colliders
            SphereCollider sphere = GetComponent<SphereCollider>();
            if (sphere != null)
            {
                DestroyImmediate(sphere);
                Debug.Log($"[NPCDialogueDriver] {npcName}: Removed redundant SphereCollider");
            }

            // Setup CapsuleCollider
            CapsuleCollider capsule = GetComponent<CapsuleCollider>();
            if (capsule == null)
            {
                capsule = gameObject.AddComponent<CapsuleCollider>();
                Debug.Log($"[NPCDialogueDriver] {npcName}: Added CapsuleCollider");
            }

            capsule.isTrigger = false;

            if (useDefaultCollider)
            {
                capsule.height = colliderHeight;
                capsule.radius = colliderRadius;
                // Debug.Log($"[NPCDialogueDriver] {npcName}: Applied collider height={colliderHeight}, radius={colliderRadius}");
            }

            capsule.enabled = true;
        }

        private void OnValidate()
        {
            // Auto-populate dialogue fields when JSON is assigned or changed in Inspector
            if (dialogueJson != null && dialogueJson != lastProcessedJson)
            {
                try
                {
                    // Try parsing as passages-based format first
                    DialogueManager.StoryJson storyData = JsonUtility.FromJson<DialogueManager.StoryJson>(dialogueJson.text);

                    if (storyData != null && storyData.passages != null && storyData.passages.Count > 0)
                    {
                        // Passages-based format
                        if (!string.IsNullOrEmpty(storyData.passages[0].conversationId))
                        {
                            conversationId = storyData.passages[0].conversationId;
                        }

                        if (!string.IsNullOrEmpty(storyData.startnode))
                        {
                            startPassageId = storyData.startnode;
                        }

                        Debug.Log($"[NPCDialogueDriver] Auto-populated from passages-based JSON: conversationId='{conversationId}', startPassageId='{startPassageId}'");
                    }
                    else
                    {
                        // Try parsing as beats-based format
                        BeatBasedStoryJson beatData = JsonUtility.FromJson<BeatBasedStoryJson>(dialogueJson.text);

                        if (beatData != null)
                        {
                            // Use scene_id as conversationId for beat-based files
                            if (!string.IsNullOrEmpty(beatData.scene_id))
                            {
                                conversationId = beatData.scene_id;
                            }

                            // Use first beat's ID as startPassageId
                            if (beatData.beats != null && beatData.beats.Length > 0)
                            {
                                startPassageId = $"beat_{beatData.beats[0].id}";
                            }

                            Debug.Log($"[NPCDialogueDriver] Auto-populated from beats-based JSON: conversationId='{conversationId}', startPassageId='{startPassageId}'");
                        }
                    }

                    // Mark this JSON as processed
                    lastProcessedJson = dialogueJson;
                }
                catch (System.Exception ex)
                {
                    Debug.LogWarning($"[NPCDialogueDriver] Failed to parse JSON for auto-population: {ex.Message}");
                }
            }
        }

        // Data class for beat-based story format
        [System.Serializable]
        private class BeatBasedStoryJson
        {
            public string scene_id;
            public string[] required_flags;
            public BeatData[] beats;
        }

        [System.Serializable]
        private class BeatData
        {
            public int id;
            public string type;
            public string active_speaker;
        }

        private void Update()
        {
            // Billboard effect - face camera (disabled during exit animation)
            if (enableBillboardEffect && !isExiting && Camera.main != null)
            {
                transform.LookAt(Camera.main.transform);

                // Force X rotation back to 0 after LookAt
                Vector3 eulerAngles = transform.localEulerAngles;
                eulerAngles.x = 0f;
                transform.localEulerAngles = eulerAngles;
            }

            // Check if player is in interaction range
            Collider[] colliders = Physics.OverlapSphere(transform.position, interactionRadius);
            bool wasInRange = playerInRange;
            playerInRange = false;

            foreach (var col in colliders)
            {
                if (col.CompareTag("Player"))
                {
                    playerInRange = true;
                    player = col.gameObject;
                    // Debug.Log($"[NPCDialogueDriver] {npcName}: Player detected in range!");
                    break;
                }
            }

            // Show notification when entering range
            if (playerInRange && !notificationShown)
            {
                NotificationPanelController notificationPanel = FindAnyObjectByType<NotificationPanelController>();
                if (notificationPanel != null)
                {
                    // For multi-NPC scenes, use the customizable multiNpcDisplayName instead of specific name
                    string displayName = isMultiNpcScene ? multiNpcDisplayName : npcName;
                    notificationPanel.ShowNotification($"Press G to talk to {displayName}", duration: 10f);
                    notificationShown = true;
                    Debug.Log($"[NPCDialogueDriver] {npcName}: Showing interaction prompt (display: {displayName})");
                }
            }

            // Hide notification when leaving range
            if (!playerInRange && notificationShown)
            {
                NotificationPanelController notificationPanel = FindAnyObjectByType<NotificationPanelController>();
                if (notificationPanel != null)
                {
                    notificationPanel.HideNotification();
                    notificationShown = false;
                    Debug.Log($"[NPCDialogueDriver] {npcName}: Hiding interaction prompt");
                }
            }
        }

        /// <summary>
        /// Trigger dialogue for this NPC.
        /// Called from Interact() interface or manual invocation.
        /// </summary>
        public void TriggerDialogue()
        {
            if (dialogueManager == null)
            {
                Debug.LogWarning($"[NPCDialogueDriver] {npcName}: DialogueManager not found");
                return;
            }

            if (dialogueJson == null)
            {
                Debug.LogWarning($"[NPCDialogueDriver] {npcName}: dialogueJson TextAsset not assigned");
                return;
            }

            Debug.Log($"[NPCDialogueDriver] {npcName}: Starting dialogue - conversationId={conversationId}, startPassageId={startPassageId}");

            // Use new TextAsset-based method if available, otherwise fall back
            if (dialogueManager.CanLoadFromTextAsset())
            {
                dialogueManager.StartDialogue(dialogueJson, conversationId, npcName, isMultiNpcScene, startPassageId, gameObject);
            }
            else
            {
                // Fallback for backward compatibility (legacy method)
                Debug.LogWarning($"[NPCDialogueDriver] {npcName}: DialogueManager doesn't support TextAsset method, using legacy approach");
                dialogueManager.StartDialogue(npcName, startPassageId, "", gameObject);
            }
        }

        /// <summary>
        /// IInteractable implementation - called when player presses interact key.
        /// </summary>
        public void Interact(GameObject triggeringPlayer)
        {
            if (!dialogueManager.IsDialogueActive)
            {
                TriggerDialogue();
            }
        }

        /// <summary>
        /// Called by DialogueUIController during exit animation to disable billboard.
        /// </summary>
        public void SetExitingState(bool exiting)
        {
            isExiting = exiting;
        }

        /// <summary>
        /// Movement helper - move NPC to target position.
        /// </summary>
        public void MoveTowardsTarget(Vector3 targetPosition, float speed)
        {
            if (npcController != null)
            {
                npcController.MoveTo(targetPosition, speed);
            }
            else
            {
                Debug.LogWarning($"[NPCDialogueDriver] {npcName}: NPCController not assigned, cannot move");
            }
        }

        /// <summary>
        /// Movement helper - look at target transform.
        /// </summary>
        public void LookAtTarget(Transform target)
        {
            if (npcController != null)
            {
                npcController.LookAt(target);
            }
            else
            {
                Debug.LogWarning($"[NPCDialogueDriver] {npcName}: NPCController not assigned, cannot look");
            }
        }

        // Expose properties for external access
        public string NPCName => npcName;
        public bool IsExiting => isExiting;
        public NPCController Controller => npcController;
    }
}
