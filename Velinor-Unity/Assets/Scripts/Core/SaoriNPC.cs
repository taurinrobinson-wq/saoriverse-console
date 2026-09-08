using UnityEngine;
using TMPro;
using Velinor.Core;

namespace Velinor.Core
{
    public class SaoriNPC : MonoBehaviour, IInteractable
    {
        [SerializeField] private string npcId = "Saori";
        [SerializeField] private string startPassageId = "market_entry";  // Changed from saori_beat_1 to match new story flow
        [SerializeField] private float interactionRadius = 0.8f; // Detection radius for proximity prompt

        private bool playerInRange = false;
        private GameObject player;
        private bool notificationShown = false;

        private void Start()
        {
            // Scale down Asuna to match player size
            transform.localScale = new Vector3(1.8f, 1.8f, 1.8f);

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
            capsule.height = 1.5f;
            capsule.radius = 0.3f;
            capsule.enabled = true; // ENSURE collider is enabled
            Debug.Log("[SaoriNPC] CapsuleCollider configured and enabled for proper collision");
        }

        private void OnTriggerStay(Collider other)
        {
            // This is now handled by CharacterController collision
        }

        private void Update()
        {
            // Billboard effect - face the camera
            if (Camera.main != null)
            {
                transform.LookAt(Camera.main.transform);
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
                    string displayName = DialogueManager.GetDisplayName(npcId);
                    notificationPanel.ShowNotification($"Press G to talk to {displayName}", duration: 10f);
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
                Debug.Log($"[SaoriNPC] Starting dialogue: npcId={npcId}, passageId={startPassageId}");
                DialogueManager.Instance.StartDialogue(npcId, startPassageId, "", gameObject);
            }
            else
            {
                Debug.Log("[SaoriNPC] Dialogue already active");
            }
        }

        private void OnDrawGizmosSelected()
        {
            // Visualize interaction range in editor
            Gizmos.color = Color.yellow;
            Gizmos.DrawWireSphere(transform.position, interactionRadius);
        }
    }
}
