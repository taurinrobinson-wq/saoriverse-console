using UnityEngine;
using TMPro;
using UnityEngine.UI;
using System.Collections.Generic;

public class NPCInteraction : MonoBehaviour
{
    [SerializeField] public string npcId = "Ravi";
    [SerializeField] public string startPassageId = "market_entry";
    [SerializeField] public float interactionRadius = 2.5f;

    private bool playerInRange = false;

    private void Update()
    {
        Collider[] colliders = Physics.OverlapSphere(transform.position, interactionRadius);
        bool playerDetected = false;
        foreach (var col in colliders) if (col.CompareTag("Player")) { playerDetected = true; break; }

        if (playerDetected)
        {
            if (!playerInRange) { playerInRange = true; ShowPrompt(true); }
            if (Input.GetKeyDown(KeyCode.E) && !DialogueManager.Instance.IsDialogueActive)
                DialogueManager.Instance.StartDialogue(npcId, startPassageId);
        }
        else if (playerInRange) { playerInRange = false; ShowPrompt(false); }
    }

    private void ShowPrompt(bool show)
    {
        var ui = FindAnyObjectByType<DialogueUIController>();
        if (ui != null && show) ui.ShowNotification($"Press [E] to talk to {npcId}");
    }

    private void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, interactionRadius);
    }
    
    // LEGACY FIELDS FOR COMPATIBILITY
    public NPCStats raviStats, malrikStats, elenyaStats, saoriStats;
}
