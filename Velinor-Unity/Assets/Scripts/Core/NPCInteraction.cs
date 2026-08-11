using UnityEngine;
using TMPro;
using UnityEngine.UI;
using System.Collections.Generic;
using Velinor.Core;

public class NPCInteraction : MonoBehaviour, IInteractable
{
    [SerializeField] public string npcId = "Saori";
    [SerializeField] public string startPassageId = "saori_beat_1";
    [SerializeField] public float interactionRadius = 2.5f;

    private bool playerInRange = false;

    private void Update()
    {
        // Keep proximity check for prompt display only
        Collider[] colliders = Physics.OverlapSphere(transform.position, interactionRadius);
        bool playerDetected = false;
        foreach (var col in colliders) if (col.CompareTag("Player")) { playerDetected = true; break; }

        if (playerDetected)
        {
            if (!playerInRange) { playerInRange = true; ShowPrompt(true); }
        }
        else if (playerInRange) { playerInRange = false; ShowPrompt(false); }
    }

    public void Interact(GameObject player)
    {
        if (!DialogueManager.Instance.IsDialogueActive)
        {
            DialogueManager.Instance.StartDialogue(npcId, startPassageId);
        }
    }

    private void ShowPrompt(bool show)
    {
        var ui = FindAnyObjectByType<DialogueUIController>();
        if (ui != null)
        {
            ui.SetNotificationActive("Press E to Interact", show);
        }
    }

    private void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, interactionRadius);
    }
    
    // LEGACY FIELDS FOR COMPATIBILITY
    public NPCStats raviStats, malrikStats, elenyaStats, saoriStats;
}
