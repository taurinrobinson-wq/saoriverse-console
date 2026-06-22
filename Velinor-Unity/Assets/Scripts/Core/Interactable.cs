using UnityEngine;

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
                if (Input.GetKeyDown(KeyCode.E))
                {
                    Interact();
                }
            }
        }
    }
}
