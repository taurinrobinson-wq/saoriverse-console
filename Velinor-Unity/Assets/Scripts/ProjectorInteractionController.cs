using UnityEngine;
using Velinor.Core;
using System.Collections;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

/// <summary>
/// Manages the Triglyph Projector interaction flow.
/// 
/// Progression across scene variants:
/// - Stage 01-03: Player interacts → adds Mind Log with distorted descriptions → can interact again
/// - Stage 04: Player interacts → final Mind Log → collects Glyph of Contained Loss → 
///           Velinor sequence plays → door opens → final Mind Log added
/// - B-Variants: Projector disabled (set projectorDisabled = true in inspector)
/// </summary>
public class ProjectorInteractionController : MonoBehaviour
{
    [System.Serializable]
    public enum ProjectorStage
    {
        Stage01,  // "What is this machine? The image looks really distorted..."
        Stage02,  // "The image looks less distorted..."
        Stage03,  // "It definitely looks more like a person but there's two faces..."
        Stage04   // "The image looks fully resolved now... It's even smiling..."
    }

    [System.Serializable]
    public enum InteractionState
    {
        None,
        CanInteract,
        WaitingForGlyph,
        LockedDuringSequence
    }

    [Header("Stage Configuration")]
    [SerializeField] private ProjectorStage currentStage = ProjectorStage.Stage01;
    [SerializeField] private bool projectorDisabled = false;

    [Header("References")]
    [SerializeField] private Collider projectorCollider;
    [SerializeField] private CodexController codexController;
    [SerializeField] private TriglyphMonsterProjector projectorDisplay;

    [Header("Mind Log Entries")]
    [SerializeField] private string mindLogImage_Stage01 = "DefaultMindLogImage";
    [SerializeField] private string mindLogText_Stage01 = "What is this machine? The image on it looks really distorted...maybe its broken";
    
    [SerializeField] private string mindLogText_Stage02 = "The image looks less distorted, but I still don't know what it is.";
    
    [SerializeField] private string mindLogText_Stage03 = "It definitely looks more like a person but there's like two faces...What is this supposed to be.";
    
    [SerializeField] private string mindLogImage_Stage04 = "DefaultMindLogImage";
    [SerializeField] private string mindLogText_Stage04_Initial = "The image looks fully resolved now...It's even smiling like something has been resolved. But why am I seeing all of this? Oh looks like the machine is working now.";
    
    [SerializeField] private string mindLogImage_Velinor = "VelinorImage";
    [SerializeField] private string mindLogText_Final = "I... I don't know what just happened... the projector showed a woman I've never seen... she looked... terrified, like she was trying to get out, and then... she was just gone... This place... it feels like it was built for something I don't understand... everything feels... wrong. At least the cave door opened and I can finally leave. Maybe I should ask around and see if anyone knows anything.";

    [Header("Glyph Settings")]
    [SerializeField] private string glyphName = "Contained Loss";
    [SerializeField] private Sprite glyphSprite;

    [Header("Stage 04 Sequence")]
    [SerializeField] private float glyphFadeInDuration = 1f;
    [SerializeField] private float velinorSequenceDelay = 2f;
    [SerializeField] private float triglyphScreenDisplayDuration = 3f;
    [SerializeField] private GameObject triglyphScreenPanel;
    [SerializeField] private AudioClip doorOpenSound;
    [SerializeField] private AudioSource audioSource;

    [Header("Door")]
    [SerializeField] private Collider sceneTransitionCollider;

    private bool playerNearProjector = false;
    private InteractionState interactionState = InteractionState.None;
    private bool stage04ReadyForSequence = false;
    private bool waitingForGlyphCollect = false;
    private bool stage04SequenceComplete = false;
    private NotificationPanelController _cachedNotificationPanel;
    private MindLogController _cachedMindLogController;

#if ENABLE_INPUT_SYSTEM
    private InputAction _interactProjectorAction;

    private void OnEnable()
    {
        _interactProjectorAction = new InputAction("InteractProjector", binding: "<Keyboard>/e");
        _interactProjectorAction.Enable();
        _interactProjectorAction.performed += OnInteractProjector;
    }

    private void OnDisable()
    {
        if (_interactProjectorAction != null)
        {
            _interactProjectorAction.performed -= OnInteractProjector;
            _interactProjectorAction?.Disable();
        }
    }
#endif

    private void Start()
    {
        _cachedNotificationPanel = FindAnyObjectByType<NotificationPanelController>();
        _cachedMindLogController = FindAnyObjectByType<MindLogController>();
        Debug.Log($"[Projector Interaction] Controller initialized - Stage: {currentStage}");
    }

    private void Update()
    {
        if (projectorDisabled)
            return;

#if !ENABLE_INPUT_SYSTEM
        if (Input.GetKeyDown(KeyCode.E) && playerNearProjector && interactionState == InteractionState.CanInteract)
        {
            OnInteractProjector(default);
        }
        else if (Input.GetKeyDown(KeyCode.E) && playerNearProjector && interactionState == InteractionState.WaitingForGlyph)
        {
            OnInteractProjector(default);
        }
#endif
    }

    /// <summary>
    /// Centralized helper for prompt display/hiding
    /// </summary>
    private void SetPrompt(string text, bool active)
    {
        if (_cachedNotificationPanel == null)
            return;

        if (active)
        {
            _cachedNotificationPanel.ShowNotification(text);
        }
        else
        {
            _cachedNotificationPanel.HideNotification();
        }
    }

    /// <summary>
    /// Called when player enters projector collider
    /// </summary>
    private void OnTriggerEnter(Collider other)
    {
        if (projectorDisabled)
            return;

        if (other.CompareTag("Player"))
        {
            playerNearProjector = true;
            if (interactionState == InteractionState.None)
                interactionState = InteractionState.CanInteract;
            SetPrompt("Press E to Interact with Projector", true);
            Debug.Log("[Projector Interaction] Player near projector");
        }
    }

    /// <summary>
    /// Called when player exits projector collider
    /// </summary>
    private void OnTriggerExit(Collider other)
    {
        if (projectorDisabled)
            return;

        if (other.CompareTag("Player"))
        {
            playerNearProjector = false;
            if (interactionState != InteractionState.LockedDuringSequence)
                interactionState = InteractionState.None;
            SetPrompt("", false);
            Debug.Log("[Projector Interaction] Player left projector area");
        }
    }

    private void ShowInteractPrompt()
    {
        string prompt = "Press E to Interact with Projector";
        
        // Stage 04: After glyph collected, show "interact again" prompt
        if (currentStage == ProjectorStage.Stage04 && waitingForGlyphCollect)
        {
            prompt = "Press E to collect the glyph";
        }
        
        SetPrompt(prompt, true);
    }

    private void HideInteractPrompt()
    {
        SetPrompt("", false);
    }

    /// <summary>
    /// Called when player presses E while near projector
    /// Handles different flows based on current stage
    /// </summary>
    private void OnInteractProjector(InputActionPhase phase)
    {
        if (projectorDisabled || !playerNearProjector)
            return;

        if (interactionState == InteractionState.None || interactionState == InteractionState.LockedDuringSequence)
            return;

        Debug.Log($"[Projector Interaction] Interaction triggered - Stage: {currentStage}");

        switch (currentStage)
        {
            case ProjectorStage.Stage01:
            case ProjectorStage.Stage02:
            case ProjectorStage.Stage03:
                HandleEarlyStageInteraction();
                break;

            case ProjectorStage.Stage04:
                HandleStage04Interaction();
                break;
        }
    }

    /// <summary>
    /// Handles interactions for stages 01-03: Add Mind Log and allow re-interaction
    /// </summary>
    private void HandleEarlyStageInteraction()
    {
        HideInteractPrompt();
        interactionState = InteractionState.None;

        string mindLogText = currentStage switch
        {
            ProjectorStage.Stage01 => mindLogText_Stage01,
            ProjectorStage.Stage02 => mindLogText_Stage02,
            ProjectorStage.Stage03 => mindLogText_Stage03,
            _ => "Error: Unknown stage"
        };

        AddMindLog(mindLogImage_Stage01, mindLogText);

        // Allow re-interaction after brief delay
        StartCoroutine(ReenableInteractionAfterDelay(1f));
    }

    /// <summary>
    /// Handles the final stage 04 interaction sequence
    /// First press: Show final Mind Log, prompt to collect glyph
    /// Second press: Play Velinor sequence, add final Mind Log, open door
    /// </summary>
    private void HandleStage04Interaction()
    {
        if (!stage04ReadyForSequence)
        {
            // First interaction: Show Mind Log, prepare glyph
            HandleStage04FirstInteraction();
        }
        else if (!stage04SequenceComplete && waitingForGlyphCollect)
        {
            // Second interaction: Collect glyph and play sequence
            HandleStage04SequenceStart();
        }
    }

    private void HandleStage04FirstInteraction()
    {
        HideInteractPrompt();
        interactionState = InteractionState.None;

        // Add Mind Log about the resolved image
        AddMindLog(mindLogImage_Stage04, mindLogText_Stage04_Initial);

        // After brief delay, show glyph collect prompt
        StartCoroutine(ShowGlyphCollectPromptAfterDelay(1f));
    }

    private IEnumerator ShowGlyphCollectPromptAfterDelay(float delay)
    {
        yield return new WaitForSeconds(delay);

        waitingForGlyphCollect = true;
        stage04ReadyForSequence = true;
        interactionState = InteractionState.WaitingForGlyph;
        SetPrompt("Press E to collect the glyph", true);
    }

    private void HandleStage04SequenceStart()
    {
        HideInteractPrompt();
        interactionState = InteractionState.LockedDuringSequence;
        waitingForGlyphCollect = false;

        // Collect glyph
        CollectGlyph();

        // Play the complex sequence
        StartCoroutine(PlayStage04Sequence());
    }

    private IEnumerator PlayStage04Sequence()
    {
        // Safety lock: prevent sequence from running twice
        if (stage04SequenceComplete)
            yield break;
        stage04SequenceComplete = true;

        // 1. Fade out projector image
        if (projectorDisplay != null)
        {
            projectorDisplay.HideProjection();
        }

        yield return new WaitForSeconds(1f);

        // 2. Wait before Velinor sequence
        yield return new WaitForSeconds(velinorSequenceDelay);

        // 3. Show Triglyph Screen (Velinor sequence)
        if (triglyphScreenPanel != null)
        {
            triglyphScreenPanel.SetActive(true);
            Debug.Log("[Projector Interaction] Triglyph Screen appeared");
        }

        // 4. Play glitch/effect (could add animation here)
        // For now just holds the screen visible

        yield return new WaitForSeconds(triglyphScreenDisplayDuration);

        // 5. Hide Triglyph Screen
        if (triglyphScreenPanel != null)
        {
            triglyphScreenPanel.SetActive(false);
            Debug.Log("[Projector Interaction] Triglyph Screen disappeared");
        }

        // 6. Projector turns off (already hidden from step 1)

        // 7. Open door (enable collider passage)
        if (sceneTransitionCollider != null)
        {
            sceneTransitionCollider.enabled = false; // Allow player passage
            Debug.Log("[Projector Interaction] Door opened");
        }

        // 8. Play door opening sound
        if (audioSource != null && doorOpenSound != null)
        {
            audioSource.PlayOneShot(doorOpenSound);
        }

        yield return new WaitForSeconds(0.5f);

        // 9. Add final Mind Log with Velinor image
        AddMindLog(mindLogImage_Velinor, mindLogText_Final);

        // 10. Lock all interaction
        interactionState = InteractionState.None;
        SetPrompt("", false);
        Debug.Log("[Projector Interaction] Stage 04 sequence complete");
    }

    /// <summary>
    /// Adds a Mind Log entry
    /// </summary>
    private void AddMindLog(string imageKey, string text)
    {
        if (_cachedMindLogController != null)
        {
            _cachedMindLogController.AddMindLogEntry(imageKey, text);
            Debug.Log($"[Projector Interaction] Mind Log added: {text.Substring(0, Mathf.Min(50, text.Length))}...");
        }
        else
        {
            Debug.LogWarning("[Projector Interaction] MindLogController not found");
        }
    }

    /// <summary>
    /// Adds the Glyph of Contained Loss to player's Codex
    /// </summary>
    private void CollectGlyph()
    {
        if (codexController != null && glyphSprite != null)
        {
            // TODO: Create proper glyph data and add to codex
            // This depends on your glyph system structure
            Debug.Log("[Projector Interaction] Glyph collected and sequence ready");
        }
    }

    private IEnumerator ReenableInteractionAfterDelay(float delay)
    {
        yield return new WaitForSeconds(delay);
        if (playerNearProjector && !projectorDisabled)
        {
            interactionState = InteractionState.CanInteract;
            SetPrompt("Press E to Interact with Projector", true);
        }
    }

    /// <summary>
    /// Returns current stage
    /// </summary>
    public ProjectorStage GetCurrentStage() => currentStage;

    /// <summary>
    /// Returns whether stage 04 sequence is complete
    /// </summary>
    public bool IsStage04SequenceComplete() => stage04SequenceComplete;
}
