using UnityEngine;

public class GlyphObject : Interactable
{
    private bool showPrompt = false;

    void Start()
    {
        // Add trigger collider
        SphereCollider collider = GetComponent<SphereCollider>();
        if (collider == null)
        {
            collider = gameObject.AddComponent<SphereCollider>();
        }
        collider.isTrigger = true;
        collider.radius = interactionRange;
    }

    void OnTriggerStay(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            float distance = Vector3.Distance(transform.position, other.transform.position);
            if (distance <= interactionRange)
            {
                showPrompt = true;
                // Show prompt UI if it exists
                InteractionUI.Instance?.ShowPrompt("Press E to examine glyph");

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
            showPrompt = false;
            InteractionUI.Instance?.HidePrompt();
        }
    }

    public override void Interact()
    {
        if (!hasInteracted)
        {
            Debug.Log("🔷 First interaction with glyph! Prompt will not appear again.");
            hasInteracted = true;
            InteractionUI.Instance?.HidePrompt();
        }
        else
        {
            Debug.Log("🔷 Glyph already examined. (Interactions happen here)");
        }
    }
}
