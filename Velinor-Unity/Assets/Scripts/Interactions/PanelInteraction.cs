using UnityEngine;

/// <summary>
/// Handles player interaction with the panel.
/// When the player presses E while in range, activates the triglyph panel UI and codex.
/// </summary>
public class PanelInteraction : MonoBehaviour
{
    [SerializeField] private GameObject triglyphPanelUI;
    [SerializeField] private GameObject codexUI;

    private bool playerInRange = false;

    private void Update()
    {
        if (playerInRange && Input.GetKeyDown(KeyCode.E))
        {
            InteractWithPanel();
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
            playerInRange = true;
    }

    private void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player"))
            playerInRange = false;
    }

    private void InteractWithPanel()
    {
        if (triglyphPanelUI != null)
            triglyphPanelUI.SetActive(true);

        if (codexUI != null)
            codexUI.SetActive(true);
    }
}
