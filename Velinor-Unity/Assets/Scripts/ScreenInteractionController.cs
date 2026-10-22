using UnityEngine;
using Velinor.Core;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

/// <summary>
/// Manages the Triglyph Monster Screen interaction workflow:
/// 1. Player approaches screen collider and sees "Press E to Access Screen" prompt
/// 2. Pressing E opens the Codex on Mind Log Primary Screen
/// 3. Primary Screen shows interactive buttons for complex sequence
/// 4. Used as template for future screen interactions (animations, FX, SFX)
/// </summary>
public class ScreenInteractionController : MonoBehaviour
{
    [Header("References")]
    [SerializeField] private CodexController codexController;
    [SerializeField] private GameObject codexPanel;
    [SerializeField] private Collider screenCollider;

    [Header("Interaction Settings")]
    [SerializeField] private string interactionPrompt = "Press E to Access Screen";

    [Header("Mind Log Screen")]
    [SerializeField] private GameObject mindLogPrimaryScreen;

    private bool playerNearScreen = false;
    private bool screenAccessGranted = false;
    private NotificationPanelController _cachedNotificationPanel;

#if ENABLE_INPUT_SYSTEM
    private InputAction _accessScreenAction;

    private void OnEnable()
    {
        _accessScreenAction = new InputAction("AccessScreen", binding: "<Keyboard>/e");
        _accessScreenAction.Enable();
        _accessScreenAction.performed += OnAccessScreen;
    }

    private void OnDisable()
    {
        if (_accessScreenAction != null)
        {
            _accessScreenAction.performed -= OnAccessScreen;
            _accessScreenAction?.Disable();
        }
    }
#endif

    private void Start()
    {
        _cachedNotificationPanel = FindAnyObjectByType<NotificationPanelController>();
        Debug.Log("[Screen Interaction] Controller initialized");
    }

    private void Update()
    {
        // Fallback for InputManager if not using InputSystem
#if !ENABLE_INPUT_SYSTEM
        if (Input.GetKeyDown(KeyCode.E) && playerNearScreen && !screenAccessGranted)
        {
            OnAccessScreen(default);
        }
#endif
    }

    /// <summary>
    /// Called when player enters the screen interaction collider
    /// </summary>
    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            playerNearScreen = true;
            ShowAccessPrompt();
            Debug.Log("[Screen Interaction] Player near screen");
        }
    }

    /// <summary>
    /// Called when player exits the screen interaction collider
    /// </summary>
    private void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            playerNearScreen = false;
            HideAccessPrompt();
            Debug.Log("[Screen Interaction] Player left screen area");
        }
    }

    /// <summary>
    /// Displays the "Press E to Access Screen" prompt
    /// </summary>
    private void ShowAccessPrompt()
    {
        if (_cachedNotificationPanel != null)
        {
            _cachedNotificationPanel.ShowNotification(interactionPrompt);
        }
    }

    /// <summary>
    /// Hides the access prompt
    /// </summary>
    private void HideAccessPrompt()
    {
        if (_cachedNotificationPanel != null)
        {
            _cachedNotificationPanel.HideNotification();
        }
    }

    /// <summary>
    /// Called when player presses E to access the screen
    /// Opens the Codex on Mind Log Primary Screen
    /// </summary>
    private void OnAccessScreen(InputAction.CallbackContext context)
    {
        if (!context.performed || !playerNearScreen || screenAccessGranted)
            return;

        screenAccessGranted = true;
        Debug.Log("[Screen Interaction] Screen access initiated");

        // Hide the access prompt
        HideAccessPrompt();

        // Toggle Codex if not already open
        if (codexController != null)
        {
            codexController.ToggleCodex();
            Debug.Log("[Screen Interaction] Codex toggled");
        }

        // Show Mind Log Primary Screen
        if (mindLogPrimaryScreen != null)
        {
            mindLogPrimaryScreen.SetActive(true);
            Debug.Log("[Screen Interaction] Mind Log Primary Screen activated");
        }

        // TODO: Future complex sequence here
        // - Animations
        // - Visual effects
        // - Sound effects
        // - Button interactions
    }

    /// <summary>
    /// Called when screen sequence is complete
    /// Allows re-interaction
    /// </summary>
    public void ResetScreenAccess()
    {
        screenAccessGranted = false;
        Debug.Log("[Screen Interaction] Screen access reset");
    }

    /// <summary>
    /// Returns whether screen is currently being accessed
    /// </summary>
    public bool IsScreenAccessGranted => screenAccessGranted;
}
