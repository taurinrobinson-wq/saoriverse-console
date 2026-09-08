using UnityEngine;
using TMPro;
using UnityEngine.InputSystem;
using Velinor.Core;

/// <summary>
/// Handles player interaction with the triglyph panel at specific location.
/// When player presses E while in range:
/// 1. Activates the TriglyphPanelUI (from InteractionUICanvas)
/// 2. Shows the CodexPanel via CodexController (from UI_Canvas)
/// 3. Disables player movement
/// 
/// When player presses C or leaves trigger:
/// 1. Closes all panels
/// 2. Re-enables player movement
/// 
/// All prompts show via NotificationPanelController only (no separate interact prompt UI).
/// </summary>
public class PanelInteraction : MonoBehaviour
{
    [SerializeField] private GameObject triglyphPanelUI;
    [SerializeField] private GameObject codexUI;  // Legacy reference - no longer used

    private bool playerInRange = false;
    private bool panelsOpen = false;
    private CodexController codexController;
    private NotificationPanelController notificationPanel;


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
        if (notificationPanel == null)
        {
            notificationPanel = FindAnyObjectByType<NotificationPanelController>();
        }

        if (notificationPanel != null)
        {
            if (show)
            {
                notificationPanel.ShowNotification("Press E to access triglyph panel", duration: 10f);
                Debug.Log("[PanelInteraction] Showing prompt via NotificationPanel");
            }
            else
            {
                notificationPanel.ShowNotification("", duration: 0.1f);
                Debug.Log("[PanelInteraction] Hiding prompt via NotificationPanel");
            }
        }
        else
        {
            Debug.LogWarning("[PanelInteraction] NotificationPanelController not found!");
        }
    }

    private void InteractWithPanel()
    {
        // Find CodexController on first interaction
        if (codexController == null)
        {
            codexController = FindAnyObjectByType<CodexController>();
            if (codexController == null)
            {
                Debug.LogError("[PanelInteraction] CodexController not found in scene!");
            }
            else
            {
                Debug.Log("[PanelInteraction] CodexController found and cached");
            }
        }

        Debug.Log($"[PanelInteraction] InteractWithPanel called");
        Debug.Log($"[PanelInteraction] triglyphPanelUI is null: {triglyphPanelUI == null}");
        Debug.Log($"[PanelInteraction] codexController is null: {codexController == null}");

        // Activate the triglyph panel (from InteractionUICanvas)
        if (triglyphPanelUI != null)
        {
            triglyphPanelUI.SetActive(true);
            Debug.Log($"[PanelInteraction] Activated triglyphPanelUI, now active: {triglyphPanelUI.activeSelf}");

            // Show cursor since player needs to interact with the puzzle UI
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
            Debug.Log("[PanelInteraction] Cursor shown for triglyph panel interaction");
        }
        else
        {
            Debug.LogError("[PanelInteraction] triglyphPanelUI is NULL - not assigned in inspector!");
        }

        // Show the codex via CodexController (from UI_Canvas)
        if (codexController != null)
        {
            codexController.ToggleCodex();
            Debug.Log("[PanelInteraction] Called CodexController.ToggleCodex()");
        }
        else
        {
            Debug.LogError("[PanelInteraction] CodexController not available - codex will not show!");
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

        // Close the codex via CodexController
        if (codexController != null)
        {
            codexController.ToggleCodex();
            Debug.Log("[PanelInteraction] Called CodexController.ToggleCodex() to close");
        }

        // Lock cursor since UI panels are closed
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
        Debug.Log("[PanelInteraction] Cursor locked (panels closed)");

        panelsOpen = false;
        ShowPrompt(playerInRange);

        // Re-enable movement when panels are closed
        InputManager.EnableMovement();

        Debug.Log("[Panel] Triglyph Panel and Codex deactivated!");
    }
}
