using UnityEngine;
using TMPro;
using UnityEngine.InputSystem;
using Velinor.Core;

/// <summary>
/// Handles player interaction with the panel.
/// When the player presses E while in range, activates the triglyph panel UI and codex.
/// Also disables player movement while panels are open.
/// </summary>
public class PanelInteraction : MonoBehaviour
{
    [SerializeField] private GameObject triglyphPanelUI;
    [SerializeField] private GameObject codexUI;
    [SerializeField] private TextMeshProUGUI interactionPrompt;  // "Press E to access panel"

    private bool playerInRange = false;
    private bool panelsOpen = false;
    private GameObject dialogueCanvas;  // Reference to ensure it stays hidden

    private void Update()
    {
        if (playerInRange)
        {
            if (Keyboard.current != null && Keyboard.current.eKey.wasPressedThisFrame)
            {
                Debug.Log("[PanelInteraction] E key pressed while in range!");
                InteractWithPanel();
            }
        }

        // Listen for C key to close panels (codex toggle)
        if (panelsOpen && Keyboard.current != null && Keyboard.current.cKey.wasPressedThisFrame)
        {
            Debug.Log("[PanelInteraction] C key pressed - closing panels");
            CloseAllPanels();
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        Debug.Log($"[PanelInteraction] OnTriggerEnter: {other.gameObject.name}, tag={other.tag}");
        if (other.CompareTag("Player"))
        {
            Debug.Log("[PanelInteraction] Player in range!");
            playerInRange = true;
            ShowPrompt(true);
        }
    }

    private void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            Debug.Log("[PanelInteraction] Player left range.");
            playerInRange = false;
            ShowPrompt(false);

            // Close panels if player leaves trigger area
            if (panelsOpen)
            {
                CloseAllPanels();
            }
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
        // Find and cache the dialogue canvas if not already cached
        if (dialogueCanvas == null)
        {
            var canvas = GameObject.Find("DialogueCanvas");
            if (canvas != null) dialogueCanvas = canvas;
        }

        Debug.Log($"[PanelInteraction] InteractWithPanel called");
        Debug.Log($"[PanelInteraction] triglyphPanelUI is null: {triglyphPanelUI == null}");
        Debug.Log($"[PanelInteraction] codexUI is null: {codexUI == null}");

        if (triglyphPanelUI != null)
        {
            triglyphPanelUI.SetActive(true);
            Debug.Log($"[PanelInteraction] Activated triglyphPanelUI, now active: {triglyphPanelUI.activeSelf}");
        }
        else
        {
            Debug.LogError("[PanelInteraction] triglyphPanelUI is NULL - not assigned in inspector!");
        }

        if (codexUI != null)
        {
            codexUI.SetActive(true);
            Debug.Log($"[PanelInteraction] Activated codexUI, now active: {codexUI.activeSelf}");
        }
        else
        {
            Debug.LogError("[PanelInteraction] codexUI is NULL - not assigned in inspector!");
        }

        // Ensure dialogue canvas is hidden while panels are open
        if (dialogueCanvas != null)
        {
            var canvasComponent = dialogueCanvas.GetComponent<Canvas>();
            if (canvasComponent != null)
            {
                canvasComponent.enabled = false;
                Debug.Log("[PanelInteraction] DialogueCanvas disabled");
            }
        }

        ShowPrompt(false);
        panelsOpen = true;

        // Disable movement while panels are open
        InputManager.DisableMovement();

        Debug.Log("[Panel] Triglyph Panel and Codex activated!");
    }


    private void CloseAllPanels()
    {
        if (triglyphPanelUI != null)
            triglyphPanelUI.SetActive(false);

        if (codexUI != null)
            codexUI.SetActive(false);

        panelsOpen = false;
        ShowPrompt(playerInRange);

        // Re-enable movement when panels are closed
        InputManager.EnableMovement();

        // Note: Keep dialogue canvas hidden unless explicitly started by an NPC
        if (dialogueCanvas != null)
        {
            var canvasComponent = dialogueCanvas.GetComponent<Canvas>();
            if (canvasComponent != null) canvasComponent.enabled = false;
        }

        Debug.Log("[Panel] Triglyph Panel and Codex deactivated!");
    }
}
