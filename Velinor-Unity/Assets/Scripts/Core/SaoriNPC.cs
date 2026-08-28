using UnityEngine;
using TMPro;
using Velinor.Core;

namespace Velinor.Core
{
    public class SaoriNPC : MonoBehaviour, IInteractable
    {
        [SerializeField] private string npcId = "Saori";
        [SerializeField] private string startPassageId = "saori_beat_1";
        [SerializeField] private float interactionRadius = 1.5f;

        private bool playerInRange = false;
        private GameObject player;
        private bool notificationShown = false;

        private void Start()
        {
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
            capsule.height = 2f;
            capsule.radius = 0.5f;
            Debug.Log("[SaoriNPC] CapsuleCollider configured for proper collision");
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
                transform.rotation = Quaternion.Euler(0, transform.rotation.eulerAngles.y + 180, 0);
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
                    notificationPanel.ShowNotification($"Press E to talk to {npcId}", duration: 10f);
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
                DialogueManager.Instance.StartDialogue(npcId, startPassageId);
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
