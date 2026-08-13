using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

public class GlyphObject : Interactable
{
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

    override protected void OnTriggerStay(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            float distance = Vector3.Distance(transform.position, other.transform.position);
            if (distance <= interactionRange)
            {
                // Show prompt UI if it exists
                InteractionUI.Instance?.ShowPrompt("Press E to examine glyph");

                bool interactPressed = false;
#if ENABLE_INPUT_SYSTEM
                if (Keyboard.current != null && Keyboard.current.eKey.wasPressedThisFrame)
                {
                    interactPressed = true;
                }
#else
                if (Input.GetKeyDown(KeyCode.E))
                {
                    interactPressed = true;
                }
#endif

                if (interactPressed)
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
            Debug.Log("🔷 Glyph examined! It disappears.");
            hasInteracted = true;
            InteractionUI.Instance?.HidePrompt();  // IMPORTANT: Hide prompt before deactivating
            gameObject.SetActive(false);  // Glyph vanishes after first interaction
        }
        else
        {
            Debug.Log("🔷 This glyph was already examined.");
        }
    }
}
