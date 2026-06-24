using UnityEngine;

/// <summary>
/// NPCInteraction: Per-NPC GameObject script that detects player proximity and initiates dialogue.
/// 
/// Responsibilities:
/// - Detect when player enters/exits trigger range
/// - Show/hide interaction prompt via InteractionUI
/// - Listen for E-key press
/// - Call DialogueManager.StartDialogue() with npcId and startingPassageId
/// 
/// Non-Responsibilities:
/// - Does NOT contain dialogue text
/// - Does NOT manage UI elements
/// - Does NOT modify stats or REMNANTS/TONE
/// - Does NOT store NPC state
/// </summary>
public class NPCInteraction : MonoBehaviour
{
    [SerializeField] private string npcId;
    [SerializeField] private string startingPassageId;
    [SerializeField] private float interactionRange = 3f;

    private bool playerInRange = false;

    private void Update()
    {
        if (playerInRange && Input.GetKeyDown(KeyCode.E))
        {
            if (DialogueManager.Instance != null)
            {
                DialogueManager.Instance.StartDialogue(npcId, startingPassageId);
            }
            else
            {
                Debug.LogError("[NPCInteraction] DialogueManager.Instance not found");
            }
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            playerInRange = true;
            InteractionUI.Instance?.ShowPrompt($"Press E to talk to {npcId}");
            Debug.Log($"[NPCInteraction] Player entered range of NPC '{npcId}'");
        }
    }

    private void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            playerInRange = false;
            InteractionUI.Instance?.HidePrompt();
            Debug.Log($"[NPCInteraction] Player left range of NPC '{npcId}'");
        }
    }
}

