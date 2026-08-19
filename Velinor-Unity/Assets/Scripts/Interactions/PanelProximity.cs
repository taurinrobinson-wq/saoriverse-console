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
        Debug.Log($"[PanelProximity] OnTriggerEnter: {other.gameObject.name}, tag={other.tag}");
        if (other.CompareTag("Player"))
        {
            Debug.Log("[PanelProximity] Player detected! Showing prompt.");
            if (interactionPrompt != null)
            {
                interactionPrompt.SetActive(true);
                Debug.Log("[PanelProximity] Prompt activated.");
            }
            else
                Debug.LogError("[PanelProximity] interactionPrompt is NULL!");
        }
    }

    private void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            Debug.Log("[PanelProximity] Player left. Hiding prompt.");
            if (interactionPrompt != null)
                interactionPrompt.SetActive(false);
        }
    }
}
