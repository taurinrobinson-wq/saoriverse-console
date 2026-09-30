using UnityEngine;
using TMPro;
using Velinor.Core;
using System.Collections.Generic;

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
        [SerializeField] private string npcName = "NPC";           // "Saori", "Nima", "Ravi", "Willy", "Kaelen"
        [SerializeField] private string startPassageId = "start";  // Fallback start passage
        [SerializeField] private bool isMultiNpcScene = false;     // Set true for scenes like ravi_nima_market_discovery
        [SerializeField] private string multiNpcDisplayName = "[Multiple NPCs]";  // Display name for multi-NPC scenes, e.g. "Young Man and Woman"

        [Header("Movement")]
        [SerializeField] private NPCController npcController;      // Optional movement driver

        [Header("Interaction")]
        [SerializeField] private float interactionRadius = 0.8f;
        [SerializeField] private GameObject interactionGlow;      // Visual feedback when in range

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

        // Audio clip cache: maps "beat_id_tone" to AudioClip for fast playback
        // Populated in OnValidate when JSON is assigned
        private Dictionary<string, AudioClip> audioClipCache = new Dictionary<string, AudioClip>();
        private string currentSceneId = ""; // Cache the scene_id from JSON

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
                    DialogueJson dialogueData = JsonUtility.FromJson<DialogueJson>(dialogueJson.text);

                    if (dialogueData != null)
                    {
                        // Try passages format first
                        if (dialogueData.passages != null && dialogueData.passages.Length > 0)
                        {
                            startPassageId = !string.IsNullOrEmpty(dialogueData.startnode) 
                                ? dialogueData.startnode 
                                : dialogueData.passages[0].pid;
                            
                            Debug.Log($"[NPCDialogueDriver] Auto-populated from passages JSON: startPassageId='{startPassageId}'");
                        }
                        // Try beats format
                        else if (dialogueData.beats != null && dialogueData.beats.Length > 0)
                        {
                            startPassageId = "1"; // Default to first beat
                            Debug.Log($"[NPCDialogueDriver] Auto-populated from beats JSON: startPassageId='{startPassageId}'");
                            
                            // Pre-load audio clips for all beats
                            PreloadAudioClips(dialogueData);
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

        /// <summary>
        /// Pre-load all audio clips referenced in the dialogue JSON.
        /// Called during OnValidate when JSON is assigned in Inspector.
        /// This caches clips for O(1) lookup during gameplay, avoiding runtime file reads.
        /// </summary>
        private void PreloadAudioClips(DialogueJson dialogueData)
        {
            if (dialogueData == null || dialogueData.beats == null)
            {
                return;
            }

            // Clear previous cache
            audioClipCache.Clear();
            currentSceneId = dialogueData.scene_id ?? "";

            if (string.IsNullOrEmpty(currentSceneId))
            {
                Debug.LogWarning($"[NPCDialogueDriver] {npcName}: scene_id not found in JSON");
                return;
            }

            int clipsLoaded = 0;

            // Iterate through all beats
            foreach (var beat in dialogueData.beats)
            {
                if (beat == null)
                    continue;

                string beatId = beat.id.ToString();

                // Load beat intro audio (e.g., "Saori_scene_1")
                if (!string.IsNullOrEmpty(beat.audio_clip))
                {
                    AudioClip clip = Resources.Load<AudioClip>($"Audio/Voiceover/{currentSceneId}/{beat.audio_clip}");
                    if (clip != null)
                    {
                        audioClipCache[$"{beatId}"] = clip;
                        clipsLoaded++;
                    }
                }

                // Load tone choice audio (player and NPC response)
                if (beat.tone_choices != null)
                {
                    foreach (var choice in beat.tone_choices)
                    {
                        if (choice == null)
                            continue;

                        string tone = choice.tone ?? "";

                        // Player choice audio (e.g., "beat_1_T")
                        if (!string.IsNullOrEmpty(choice.audio_clip_on_choice))
                        {
                            AudioClip clip = Resources.Load<AudioClip>($"Audio/Voiceover/{currentSceneId}/{choice.audio_clip_on_choice}");
                            if (clip != null)
                            {
                                audioClipCache[$"{beatId}_{tone}"] = clip;
                                clipsLoaded++;
                            }
                        }

                        // NPC response audio (e.g., "beat_1_T_npc")
                        if (!string.IsNullOrEmpty(choice.audio_clip_on_response))
                        {
                            AudioClip clip = Resources.Load<AudioClip>($"Audio/Voiceover/{currentSceneId}/{choice.audio_clip_on_response}");
                            if (clip != null)
                            {
                                audioClipCache[$"{beatId}_{tone}_npc"] = clip;
                                clipsLoaded++;
                            }
                        }
                    }
                }
            }

            if (clipsLoaded > 0)
            {
                Debug.Log($"[NPCDialogueDriver] {npcName}: Pre-loaded {clipsLoaded} audio clips from {currentSceneId}");
            }
        }

        /// <summary>
        /// Get a pre-loaded audio clip by beat ID and optional tone.
        /// Returns null if not found or not pre-loaded.
        /// </summary>
        public AudioClip GetAudioClip(string beatId, string tone = "")
        {
            string key = string.IsNullOrEmpty(tone) ? beatId : $"{beatId}_{tone}";
            audioClipCache.TryGetValue(key, out AudioClip clip);
            return clip;
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
                    break;
                }
            }

            // Show notification when entering range
            if (playerInRange && !notificationShown)
            {
                if (interactionGlow != null) interactionGlow.SetActive(true);
                
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
                if (interactionGlow != null) interactionGlow.SetActive(false);
                
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
                Debug.LogError($"[NPCDialogueDriver] {npcName}: dialogueJson TextAsset not assigned in Inspector!");
                return;
            }

            Debug.Log($"[NPCDialogueDriver] {npcName}: Starting dialogue - startBeatId={startPassageId}");

            // Load the dialogue JSON
            dialogueManager.LoadDialogue(dialogueJson);
            
            // Start dialogue at specified beat
            dialogueManager.StartDialogue(gameObject.name, startPassageId);
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
