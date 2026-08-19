using UnityEngine;

/// <summary>
/// Detects when the player enters/exits proximity to the triglyph panel.
/// Shows/hides the interaction prompt.
/// </summary>
public class PanelProximity : MonoBehaviour
{
    [SerializeField] private GameObject interactionPrompt;

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            if (interactionPrompt != null)
                interactionPrompt.SetActive(true);
        }
    }

    private void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            if (interactionPrompt != null)
                interactionPrompt.SetActive(false);
        }
    }
}
