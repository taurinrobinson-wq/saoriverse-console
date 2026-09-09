using UnityEngine;
using TMPro;
using Velinor.Core;

namespace Velinor.Core
{
    public class SaoriNPC : MonoBehaviour, IInteractable
    {
        [SerializeField] private string npcId = "Saori";
        [SerializeField] private string startPassageId = "desert_intro";
        [SerializeField] private float interactionRadius = 0.8f;
        
        [Header("Dialogue")]
        [SerializeField] private TextAsset dialogueJson;  // Should be set to saori_desert_encounter_01.json

        [Header("Transform Configuration")]
        [SerializeField] private Vector3 npcScale = new Vector3(1.8f, 1.8f, 1.8f);  // Configurable scale
        [SerializeField] private bool useDefaultScale = true;  // Toggle to use or customize scale

        [Header("Collider Configuration")]
        [SerializeField] private float colliderHeight = 1.5f;
        [SerializeField] private float colliderRadius = 0.3f;
        [SerializeField] private bool useDefaultCollider = true;  // Toggle to use or customize collider

        [Header("Billboard Effect")]
        [SerializeField] private bool enableBillboardEffect = true;  // Toggle billboard LookAt on/off

        private bool playerInRange = false;
        private GameObject player;
        private bool notificationShown = false;
        private bool isExiting = false;  // Flag to disable billboard effect during exit animation

        private void Start()
        {
            // CRITICAL: Fix X rotation that's baked into the Asuna skeleton (-16.753 degrees)
            // This must happen first, before any other transforms
            Vector3 eulerAngles = transform.localEulerAngles;
            eulerAngles.x = 0f;
            transform.localEulerAngles = eulerAngles;
            Debug.Log("[SaoriNPC] X rotation corrected to 0 (Asuna skeleton fix)");

            // Apply scale if enabled
            if (useDefaultScale)
            {
                transform.localScale = npcScale;
                Debug.Log($"[SaoriNPC] Applied scale: {npcScale}");
            }
            else
            {
                Debug.Log($"[SaoriNPC] Scale customization disabled - keeping current scale: {transform.localScale}");
            }

            // Clean up colliders: keep only CapsuleCollider, remove SphereCollider
            SphereCollider sphere = GetComponent<SphereCollider>();
            if (sphere != null)
            {
                DestroyImmediate(sphere);
                Debug.Log("[SaoriNPC] Removed redundant SphereCollider");
            }

            // Ensure CapsuleCollider exists and is configured correctly
            CapsuleCollider capsule = GetComponent<CapsuleCollider>();
            if (capsule == null)
            {
                capsule = gameObject.AddComponent<CapsuleCollider>();
                Debug.Log("[SaoriNPC] Added CapsuleCollider for interaction");
            }

            capsule.isTrigger = false; // Non-trigger collider for CharacterController collision

            // Apply collider configuration if enabled
            if (useDefaultCollider)
            {
                capsule.height = colliderHeight;
                capsule.radius = colliderRadius;
                Debug.Log($"[SaoriNPC] Applied collider: height={colliderHeight}, radius={colliderRadius}");
            }
            else
            {
                Debug.Log($"[SaoriNPC] Collider customization disabled - keeping current dimensions");
            }

            capsule.enabled = true; // ENSURE collider is enabled
            Debug.Log("[SaoriNPC] CapsuleCollider enabled for proper collision");
        }

        private void OnTriggerStay(Collider other)
        {
            // This is now handled by CharacterController collision
        }

        private void Update()
        {
            // Billboard effect - face the camera (but not during exit animation or if disabled!)
            if (enableBillboardEffect && !isExiting && Camera.main != null)
            {
                transform.LookAt(Camera.main.transform);

                // CRITICAL: Force X rotation to 0 after LookAt to preserve upright posture
                Vector3 eulerAngles = transform.localEulerAngles;
                eulerAngles.x = 0f;
                transform.localEulerAngles = eulerAngles;
            }

            // Check if player is in range (for proximity indication)
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
                NotificationPanelController notificationPanel = FindAnyObjectByType<NotificationPanelController>();
                if (notificationPanel != null)
                {
                    notificationPanel.ShowNotification($"Press G to talk to {npcId}", duration: 10f);
                    notificationShown = true;
                    Debug.Log($"[SaoriNPC] Showing interaction prompt");
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
                    Debug.Log($"[SaoriNPC] Hiding interaction prompt");
                }
            }
        }

        public void Interact(GameObject triggeringPlayer)
        {
            // Check if DialogueManager exists
            if (DialogueManager.Instance == null)
            {
                Debug.LogError("[SaoriNPC] DialogueManager.Instance not found!");
                return;
            }

            // Only start dialogue if not already active
            if (!DialogueManager.Instance.IsDialogueActive)
            {
                // Load dialogue JSON if assigned
                if (dialogueJson != null)
                {
                    DialogueManager.Instance.LoadDialogue(dialogueJson);
                }
                else
                {
                    Debug.LogError("[SaoriNPC] Dialogue JSON not assigned in Inspector!");
                    return;
                }

                Debug.Log($"[SaoriNPC] Starting dialogue: npcId={npcId}, beatId={startPassageId}");
                DialogueManager.Instance.StartDialogue(npcId, startPassageId);
            }
            else
            {
                Debug.Log("[SaoriNPC] Dialogue already active");
            }
        }

        /// <summary>
        /// Called by DialogueUIController when NPC exit animation starts
        /// Disables the billboard LookAt effect so rotation can be controlled
        /// </summary>
        public void SetExitingState(bool exiting)
        {
            isExiting = exiting;
            Debug.Log($"[SaoriNPC] Exit state set to: {exiting}");
        }

        private void OnDrawGizmosSelected()
        {
            // Visualize interaction range in editor
            Gizmos.color = Color.yellow;
            Gizmos.DrawWireSphere(transform.position, interactionRadius);
        }
    }
}
