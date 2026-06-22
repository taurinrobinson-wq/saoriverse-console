using UnityEngine;

public class NPCObject : Interactable
{
    public string npcName = "NPC";

    void Start()
    {
        gameObject.tag = "Interactable";
        // Add trigger collider
        BoxCollider collider = GetComponent<BoxCollider>();
        if (collider == null)
        {
            collider = gameObject.AddComponent<BoxCollider>();
        }
        collider.isTrigger = true;
        collider.size = new Vector3(1, 2, 1);
    }

    void OnTriggerStay(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            float distance = Vector3.Distance(transform.position, other.transform.position);
            if (distance <= interactionRange)
            {
                // Show prompt UI if it exists
                InteractionUI.Instance?.ShowPrompt($"Press E to talk to {npcName}");

                if (Input.GetKeyDown(KeyCode.E))
                {
                    Interact();
                }
            }
        }
    }

    void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            InteractionUI.Instance?.HidePrompt();
        }
    }

    public override void Interact()
    {
        if (!hasInteracted)
        {
            Debug.Log($"💬 First dialogue with {npcName}!");
            hasInteracted = true;
        }
        
        Debug.Log($"💬 Opening dialogue with {npcName}...");
        // TODO: Open dialogue UI here
    }
}
