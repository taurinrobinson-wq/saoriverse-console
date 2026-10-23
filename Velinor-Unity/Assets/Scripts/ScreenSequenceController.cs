using UnityEngine;
using Velinor.Core;
using Velinor.Management;
using System.Collections;
using System.Collections.Generic;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

/// <summary>
/// Manages interactive comic-strip screen sequences.
/// Based on TriglyphPuzzleController pattern, but for UI hotspot interactions.
/// 
/// Flow:
/// 1. Player approaches screen collider
/// 2. Shows "Press E to Access Screen" prompt
/// 3. Player presses E → Opens Codex (Mind Log view) + activates screen image
/// 4. Player clicks hotspots on screen image
/// 5. Each click triggers animations and adds Mind Logs
/// 6. Sequence complete → Teleports to MachinesCave_01 variant
/// </summary>
public class ScreenSequenceController : MonoBehaviour
{
    [Header("References")]
    [SerializeField] private CodexController codexController;
    [SerializeField] private GameObject screenImagePanel;
    [SerializeField] private Collider2D screenAccessCollider;
    
    [Header("Sequence Configuration")]
    [SerializeField] private int sequenceStageID = 1;  // Which stage (1-4)
    [SerializeField] private bool requireAllHotspotsClicked = false;
    [SerializeField] private string completionMindLogText = "Story concluded...";
    
    [Header("Scene Teleportation")]
    [SerializeField] private string teleportSceneName;  // e.g., "MachinesCave_01_Stage01"
    [SerializeField] private float teleportDelay = 2f;
    
    [Header("Audio")]
    [SerializeField] private AudioClip screenAccessSound;
    [SerializeField] private AudioClip sequenceCompleteSound;
    [SerializeField] private AudioSource audioSource;
    
    // State
    private bool playerNearScreen = false;
    private bool sequenceInProgress = false;
    private bool sequenceCompleted = false;
    private Dictionary<string, bool> clickedHotspots = new Dictionary<string, bool>();
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
        
        if (audioSource == null)
        {
            audioSource = GetComponent<AudioSource>();
            if (audioSource == null)
            {
                audioSource = gameObject.AddComponent<AudioSource>();
                audioSource.playOnAwake = false;
            }
        }
        
        Debug.Log($"[Screen Sequence {sequenceStageID}] Controller initialized");
    }

    private void Update()
    {
        // Fallback for InputManager if not using InputSystem
#if !ENABLE_INPUT_SYSTEM
        if (Input.GetKeyDown(KeyCode.E) && playerNearScreen && !sequenceInProgress && !sequenceCompleted)
        {
            OnAccessScreen(default);
        }
#endif
    }

    private void OnTriggerEnter(Collider other)
    {
        if (sequenceCompleted || sequenceInProgress)
            return;
            
        if (other.CompareTag("Player"))
        {
            playerNearScreen = true;
            SetPrompt("Press E to Access Screen", true);
            Debug.Log("[Screen Sequence] Player near screen");
        }
    }
    
    private void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            playerNearScreen = false;
            if (!sequenceInProgress)
                SetPrompt("", false);
            Debug.Log("[Screen Sequence] Player left screen area");
        }
    }
    
    private void OnAccessScreen(InputAction.CallbackContext context)
    {
        if (!context.performed || !playerNearScreen || sequenceInProgress || sequenceCompleted)
            return;
        
        StartSequence();
    }
    
    /// <summary>
    /// Initiates the screen sequence
    /// </summary>
    public void StartSequence()
    {
        sequenceInProgress = true;
        SetPrompt("", false);
        
        // Play access sound
        if (audioSource != null && screenAccessSound != null)
            audioSource.PlayOneShot(screenAccessSound);
        
        // Open Codex on Mind Log view
        if (codexController != null)
            codexController.ToggleCodex();
        
        // Show screen image panel
        if (screenImagePanel != null)
            screenImagePanel.SetActive(true);
        
        Debug.Log($"[Screen Sequence {sequenceStageID}] Sequence started");
    }
    
    /// <summary>
    /// Called by ScreenHotspot when clicked
    /// </summary>
    public void OnHotspotClicked(string hotspotID)
    {
        if (!sequenceInProgress || sequenceCompleted)
            return;
        
        if (!clickedHotspots.ContainsKey(hotspotID))
            clickedHotspots[hotspotID] = false;
        
        if (clickedHotspots[hotspotID])
            return; // Already clicked this hotspot
        
        clickedHotspots[hotspotID] = true;
        Debug.Log($"[Screen Sequence {sequenceStageID}] Hotspot clicked: {hotspotID} ({clickedHotspots.Count} total)");
        
        // Trigger associated animations and Mind Logs
        StartCoroutine(ProcessHotspotInteraction(hotspotID));
    }
    
    private IEnumerator ProcessHotspotInteraction(string hotspotID)
    {
        // TODO: Get animation and Mind Log data for this hotspot from configuration
        // TODO: Play animations via ScreenPanelAnimator
        // TODO: Add Mind Logs via MindLogManager
        
        yield return new WaitForSeconds(0.1f);
        
        CheckSequenceCompletion();
    }
    
    private void CheckSequenceCompletion()
    {
        // Check if all required hotspots have been clicked
        // TODO: Define per-stage which hotspots are required (or if all must be clicked)
        
        // For now, this is a placeholder - you'll configure this per stage
        // Example: if (clickedHotspots.Count >= requiredHotspotsPerStage)
        
        // If complete:
        // CompleteSequence();
    }
    
    /// <summary>
    /// Call this when sequence is complete
    /// </summary>
    public void CompleteSequence()
    {
        if (sequenceCompleted)
            return;
        
        sequenceCompleted = true;
        sequenceInProgress = false;
        
        // Add final Mind Log
        AddMindLog("Completion", completionMindLogText);
        
        // Play completion sound
        if (audioSource != null && sequenceCompleteSound != null)
            audioSource.PlayOneShot(sequenceCompleteSound);
        
        // Fade out and teleport
        StartCoroutine(TeleportAfterDelay());
    }
    
    private IEnumerator TeleportAfterDelay()
    {
        yield return new WaitForSeconds(teleportDelay);
        
        // Close Codex
        if (codexController != null)
            codexController.ToggleCodex();
        
        // Hide screen panel
        if (screenImagePanel != null)
            screenImagePanel.SetActive(false);
        
        // Teleport to MachinesCave_01 variant
        if (!string.IsNullOrEmpty(teleportSceneName))
        {
            UnityEngine.SceneManagement.SceneManager.LoadScene(teleportSceneName);
        }
        
        Debug.Log($"[Screen Sequence {sequenceStageID}] Sequence complete, teleporting to {teleportSceneName}");
    }
    
    /// <summary>
    /// Adds a Mind Log entry
    /// </summary>
    private void AddMindLog(string imageKey, string text)
    {
        var manager = MindLogManager.GetOrCreate();
        if (manager == null)
        {
            Debug.LogError("[Screen Sequence] Failed to get MindLogManager");
            return;
        }
        
        // Load the sprite from resources
        Sprite icon = Resources.Load<Sprite>($"MindLogImages/{imageKey}");
        if (icon == null)
        {
            Debug.LogWarning($"[Screen Sequence] Mind log image not found: {imageKey}");
        }
        
        // Create a new Mind Log entry with a unique ID
        string logID = $"screen_{sequenceStageID}_{System.DateTime.Now.Ticks}";
        var entry = new MindLogEntry(
            logID,
            icon,
            "Story Discovery",  // Summary text
            text                 // Full text
        );
        
        manager.AddLog(entry);
        Debug.Log($"[Screen Sequence] Mind Log added: {text.Substring(0, Mathf.Min(50, text.Length))}...");
    }
    
    private void SetPrompt(string text, bool active)
    {
        if (_cachedNotificationPanel == null)
            return;
        
        if (active)
            _cachedNotificationPanel.ShowNotification(text);
        else
            _cachedNotificationPanel.HideNotification();
    }
    
    /// <summary>
    /// Returns true if the sequence is currently in progress
    /// Use to gate other interactions
    /// </summary>
    public bool IsSequenceInProgress => sequenceInProgress;
    
    /// <summary>
    /// Returns true if the sequence has been completed
    /// </summary>
    public bool IsSequenceCompleted => sequenceCompleted;
    
    /// <summary>
    /// Returns the stage ID for this sequence
    /// </summary>
    public int GetSequenceStageID() => sequenceStageID;
    
    /// <summary>
    /// Returns how many hotspots have been clicked
    /// </summary>
    public int GetClickedHotspotCount() => clickedHotspots.Count;
}
