using UnityEngine;

/// <summary>
/// Controls door animation and chamber entrance activation.
/// Links to a trigger collider that gates entry to a chamber.
/// </summary>
public class DoorController : MonoBehaviour
{
    [Header("Door Animation")]
    [SerializeField] private Animator animator;
    [SerializeField] private bool isOpen = false;

    [Header("Linked Transition Zone")]
    [SerializeField] private Collider2D chamberEntranceCollider;

    private void Awake()
    {
        // Lock the chamber entrance until door opens
        if (chamberEntranceCollider != null)
            chamberEntranceCollider.enabled = false;
    }

    public void OpenDoor()
    {
        if (isOpen) return;

        isOpen = true;

        // Play animation
        if (animator != null)
            animator.SetTrigger("Open");

        // Activate chamber entrance
        if (chamberEntranceCollider != null)
            chamberEntranceCollider.enabled = true;

        Debug.Log("[DoorController] Door opened!");
    }
}
