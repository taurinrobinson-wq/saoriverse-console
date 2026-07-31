using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

public abstract class Interactable : MonoBehaviour
{
    public float interactionRange = 3f;
    protected bool hasInteracted = false;

    public abstract void Interact();

    public virtual bool CanInteract()
    {
        return true;
    }

    protected virtual void OnTriggerStay(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            float distance = Vector3.Distance(transform.position, other.transform.position);
            if (distance <= interactionRange)
            {
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
}
