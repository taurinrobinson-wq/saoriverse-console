using UnityEngine;
using TMPro;
using UnityEngine.InputSystem;

/// <summary>
/// Handles player interaction with the panel.
/// When the player presses E while in range, activates the triglyph panel UI and codex.
/// </summary>
public class PanelInteraction : MonoBehaviour
{
    [SerializeField] private GameObject triglyphPanelUI;
    [SerializeField] private GameObject codexUI;
    [SerializeField] private TextMeshProUGUI interactionPrompt;  // "Press E to access panel"

    private bool playerInRange = false;

    private void Update()
    {
        if (playerInRange && Keyboard.current != null && Keyboard.current.eKey.wasPressedThisFrame)
        {
            InteractWithPanel();
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            playerInRange = true;
            ShowPrompt(true);
        }
    }

    private void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            playerInRange = false;
            ShowPrompt(false);
        }
    }

    private void ShowPrompt(bool show)
    {
        if (interactionPrompt != null)
        {
            interactionPrompt.enabled = show;
            if (show)
                interactionPrompt.text = "Press E to access panel";
        }
    }

    private void InteractWithPanel()
    {
        if (triglyphPanelUI != null)
            triglyphPanelUI.SetActive(true);

        if (codexUI != null)
            codexUI.SetActive(true);

        ShowPrompt(false);

        Debug.Log("[Panel] Triglyph Panel and Codex activated!");
    }
}
