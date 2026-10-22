# Screen Sequence Interactive Comic System - Architecture Guide

## Overview

This is an **interactive comic-strip system** for telling branching story sequences through clickable panels, animations, and progressive reveals. Based on the TriglyphPuzzleController **interaction pattern** (proximity → E-key → complex flow), but with a completely different execution focused on **UI hotspot interactions and animations**.

**Key Differences from TriglyphPuzzleController:**
| Aspect | Triglyph Puzzle | Screen Sequence |
|--------|-----------------|-----------------|
| Primary Interaction | Select 3 glyphs from Codex | Click hotspots on screen image |
| UI Flow | Glyphs → Confirm → Door opens | Mind Log + Screen → Click panels → Animations |
| Player Agency | Binary (select items) | Exploratory (discover story) |
| Sequence Type | Single action (add to panel) | Multi-step with progressive reveals |
| Outcome | Door opens, scene changes | Multiple stages, scene teleport on completion |
| State Tracking | Simple (3 glyphs selected) | Complex (which hotspots clicked, panels revealed, etc.) |

## Architecture Components

### 1. Main Controller: ScreenSequenceController
**Purpose**: Manages the overall sequence flow (replacing ScreenInteractionController)

**Responsibilities:**
- Detect player proximity to screen (collider trigger)
- Show "Press E to Access Screen" prompt
- On E press: Open Codex Mind Log view + activate screen image UI
- Manage sequence state (which panels revealed, which animations played)
- Track Mind Logs added during sequence
- Detect sequence completion
- Trigger teleportation to MachinesCave_01 variant

**Key State:**
```csharp
private bool sequenceInProgress = false;      // Prevents other interactions
private Dictionary<string, bool> revealedPanels;  // Tracks what's been shown
private List<string> addedMindLogs;           // Mind Logs added this sequence
private int currentSequenceStage = 0;         // Which story beat we're on
```

### 2. Screen Image UI: ScreenImagePanel
**Purpose**: Displays the comic-strip image and manages clickable hotspots

**Responsibilities:**
- Display the screen image (comic-strip style)
- Manage clickable hotspots/interactive areas
- Highlight hotspots on hover (visual feedback)
- Pass click events to ScreenSequenceController
- Support multiple screen images (one per sequence variant)

**Structure:**
```
ScreenImagePanel (Canvas)
├── BackgroundImage (RawImage or Image - the comic strip)
├── Hotspot_01 (Button or Graphic Raycaster target)
├── Hotspot_02
├── Hotspot_03
└── AnimationLayer (For reveals, fading, etc.)
```

### 3. Hotspot System: ScreenHotspot
**Purpose**: Defines clickable interactive areas on the screen image

**Responsibilities:**
- Store hotspot metadata (ID, position, linked panel ID, animation type)
- Handle click detection
- Track if already clicked
- Call animation callbacks on click
- Prevent double-clicking same hotspot

**Properties:**
```csharp
public string hotspotID;
public string linkedPanelID;
public enum HotspotAnimationType { SplitApart, FadeIn, SlideIn, Custom }
public HotspotAnimationType animationType;
public bool oneTimeOnly = true;
public AudioClip clickSound;
```

### 4. Animation System: ScreenPanelAnimator
**Purpose**: Handles all UI animations triggered by hotspot clicks

**Responsibilities:**
- Play split-apart animations (panels moving left/right to reveal center)
- Play fade-in animations (new panels appearing)
- Play slide/transition animations
- Sequence multiple animations
- Add delay between animations for pacing
- Call Mind Log callbacks when animations complete

**Animation Types:**
```csharp
// Panels splitting apart to reveal hidden center panel
PlaySplitAnimation(panelID, duration, easeType, onComplete)

// New panel fading in
PlayFadeInAnimation(panelID, duration, delay, onComplete)

// Panel sliding in from edge
PlaySlideAnimation(panelID, slideDirection, duration, onComplete)

// Sequence multiple animations in order
PlaySequenceAnimation(animationList, onComplete)
```

### 5. Mind Log Injection System: ScreenMindLogBridge
**Purpose**: Populates Mind Logs during sequence as player discovers story

**Responsibilities:**
- Define which Mind Logs appear at which story beats
- Add Mind Logs when hotspots are clicked or animations complete
- Support conditional Mind Logs (appear only if certain panels revealed)
- Track Mind Logs added so player can see story in Codex

**Structure:**
```csharp
[Serializable]
public class ScreenMindLogEvent
{
    public string triggerHotspotID;          // Which hotspot triggers this
    public string mindLogImageKey;           // Icon to display
    public string mindLogText;               // Story text
    public float delayBeforeAdding = 0f;     // Wait before adding Mind Log
    public bool addBeforeAnimation = false;  // Add during animation or after
}

public ScreenMindLogEvent[] mindLogEvents;   // Array in Inspector
```

### 6. Scene Teleportation: ScreenSequenceCompletion
**Purpose**: Handles end-of-sequence behavior

**Responsibilities:**
- Detect when sequence is complete (all required hotspots clicked)
- Add final "completion" Mind Log
- Transition visual (fade out, effects)
- Teleport player to MachinesCave_01 variant
- Track completion state for variant progression

**Properties:**
```csharp
public string completionMindLogText;        // Final Mind Log
public bool requireAllHotspotsClicked = false; // Can skip some hotspots?
public SceneTransitionData teleportTarget;  // Where to send player
public float teleportDelay = 2f;            // Time before teleport
```

## Scene Variant Structure

### For Each Story Sequence

**MachinesCave_02_Stage01:**
- ScreenSequenceController (with this stage's settings)
- ScreenImagePanel with Stage01 image
- 8-12 Hotspots (clickable areas on image)
- ScreenMindLogBridge with Stage01 Mind Logs
- Leads to MachinesCave_01_Stage01 on completion

**MachinesCave_02_Stage02:**
- Same structure, but different image, hotspots, Mind Logs
- Leads to MachinesCave_01_Stage02 on completion

**MachinesCave_02_Stage03:**
- Same pattern continues

**MachinesCave_02_Stage04 (Final):**
- Same structure
- Final Mind Log + major story revelation
- Leads to MachinesCave_01_Stage04 (final scene) on completion

### MachinesCave_01 Variants
- Empty/exploration scenes
- Optional interactions or story continuation
- Door back to corresponding MachinesCave_02 variant for repeat access

---

## Detailed Setup Instructions

### Step 1: Create ScreenSequenceController Script

**File:** `Assets/Scripts/ScreenSequenceController.cs`

```csharp
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
/// </summary>
public class ScreenSequenceController : MonoBehaviour
{
    [Header("References")]
    [SerializeField] private CodexController codexController;
    [SerializeField] private GameObject mindLogPrimaryScreen;
    [SerializeField] private GameObject screenImagePanel;
    [SerializeField] private Collider screenAccessCollider;
    
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
        Debug.Log($"[Screen Sequence {sequenceStageID}] Controller initialized");
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
        if (!context.performed || !playerNearScreen || sequenceInProgress)
            return;
        
        StartSequence();
    }
    
    public void StartSequence()
    {
        sequenceInProgress = true;
        SetPrompt("", false);
        
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
        
        if (clickedHotspots[hotspotID] && requireAllHotspotsClicked)
            return; // Already clicked
        
        clickedHotspots[hotspotID] = true;
        Debug.Log($"[Screen Sequence {sequenceStageID}] Hotspot clicked: {hotspotID}");
        
        // Trigger associated animations and Mind Logs
        StartCoroutine(ProcessHotspotInteraction(hotspotID));
    }
    
    private IEnumerator ProcessHotspotInteraction(string hotspotID)
    {
        // TODO: Get animation and Mind Log data for this hotspot
        // TODO: Play animations
        // TODO: Add Mind Logs
        // TODO: Check if sequence complete
        
        yield return new WaitForSeconds(0.1f);
        
        CheckSequenceCompletion();
    }
    
    private void CheckSequenceCompletion()
    {
        // Check if all required hotspots have been clicked
        // For now, simple check: if all hotspots clicked, complete
        // (Make this configurable based on sequenceStageID)
        
        // TODO: Define per-stage which hotspots are required
        
        // If complete:
        // CompleteSequence();
    }
    
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
    
    private void AddMindLog(string imageKey, string text)
    {
        var manager = MindLogManager.GetOrCreate();
        if (manager == null) return;
        
        Sprite icon = Resources.Load<Sprite>($"MindLogImages/{imageKey}");
        string logID = $"screen_{sequenceStageID}_{System.DateTime.Now.Ticks}";
        var entry = new MindLogEntry(logID, icon, "Story Discovery", text);
        
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
    
    public bool IsSequenceInProgress => sequenceInProgress;
    public bool IsSequenceCompleted => sequenceCompleted;
    public int GetSequenceStageID() => sequenceStageID;
}
```

### Step 2: Create ScreenHotspot Script

**File:** `Assets/Scripts/ScreenHotspot.cs`

```csharp
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Clickable hotspot on screen image
/// Triggers animations and Mind Log events when clicked
/// </summary>
public class ScreenHotspot : MonoBehaviour, IPointerClickHandler
{
    [SerializeField] private string hotspotID;
    [SerializeField] private ScreenSequenceController screenController;
    [SerializeField] private Graphic highlightGraphic;  // Shows on hover
    [SerializeField] private bool oneTimeOnly = true;
    [SerializeField] private AudioClip clickSound;
    
    private bool alreadyClicked = false;
    private ScreenPanelAnimator animator;
    
    private void Start()
    {
        if (screenController == null)
            screenController = GetComponentInParent<Canvas>().GetComponent<ScreenSequenceController>();
        
        animator = GetComponent<ScreenPanelAnimator>();
    }
    
    public void OnPointerClick(PointerEventData eventData)
    {
        if (oneTimeOnly && alreadyClicked)
            return;
        
        alreadyClicked = true;
        
        // Play click sound
        if (clickSound != null)
            AudioSource.PlayClipAtPoint(clickSound, transform.position);
        
        // Notify controller
        if (screenController != null)
            screenController.OnHotspotClicked(hotspotID);
        
        // Play animation
        if (animator != null)
            animator.PlayHotspotAnimation();
        
        Debug.Log($"[Screen Hotspot] Clicked: {hotspotID}");
    }
    
    public void OnPointerEnter(PointerEventData eventData)
    {
        if (highlightGraphic != null)
            highlightGraphic.enabled = true;
    }
    
    public void OnPointerExit(PointerEventData eventData)
    {
        if (highlightGraphic != null)
            highlightGraphic.enabled = false;
    }
}
```

### Step 3: Create ScreenPanelAnimator Script

**File:** `Assets/Scripts/ScreenPanelAnimator.cs`

```csharp
using UnityEngine;
using System.Collections;

/// <summary>
/// Handles animations for screen panels (split, fade, slide, etc.)
/// </summary>
public class ScreenPanelAnimator : MonoBehaviour
{
    [SerializeField] private AnimationType animationType;
    [SerializeField] private float duration = 1f;
    [SerializeField] private float delay = 0f;
    [SerializeField] private AnimationCurve easeType = AnimationCurve.EaseInOut(0, 0, 1, 1);
    
    public enum AnimationType { SplitApart, FadeIn, SlideIn, ScaleIn, Custom }
    
    private CanvasGroup canvasGroup;
    private RectTransform rectTransform;
    private Vector2 startPosition;
    private Vector3 startScale;
    private float startAlpha;
    
    private void Start()
    {
        canvasGroup = GetComponent<CanvasGroup>();
        if (canvasGroup == null)
            canvasGroup = gameObject.AddComponent<CanvasGroup>();
        
        rectTransform = GetComponent<RectTransform>();
        startPosition = rectTransform.anchoredPosition;
        startScale = rectTransform.localScale;
        startAlpha = canvasGroup.alpha;
    }
    
    public void PlayHotspotAnimation()
    {
        StopAllCoroutines();
        StartCoroutine(PlayAnimation());
    }
    
    private IEnumerator PlayAnimation()
    {
        yield return new WaitForSeconds(delay);
        
        switch (animationType)
        {
            case AnimationType.FadeIn:
                yield return StartCoroutine(AnimateFadeIn());
                break;
            case AnimationType.SplitApart:
                yield return StartCoroutine(AnimateSplitApart());
                break;
            case AnimationType.SlideIn:
                yield return StartCoroutine(AnimateSlideIn());
                break;
            case AnimationType.ScaleIn:
                yield return StartCoroutine(AnimateScaleIn());
                break;
        }
    }
    
    private IEnumerator AnimateFadeIn()
    {
        float elapsed = 0f;
        canvasGroup.alpha = 0f;
        
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t = easeType.Evaluate(elapsed / duration);
            canvasGroup.alpha = Mathf.Lerp(0f, startAlpha, t);
            yield return null;
        }
        
        canvasGroup.alpha = startAlpha;
    }
    
    private IEnumerator AnimateSplitApart()
    {
        // TODO: Implement panel split animation
        // Panels move left and right to reveal center
        yield return new WaitForSeconds(duration);
    }
    
    private IEnumerator AnimateSlideIn()
    {
        // TODO: Implement slide animation
        yield return new WaitForSeconds(duration);
    }
    
    private IEnumerator AnimateScaleIn()
    {
        float elapsed = 0f;
        rectTransform.localScale = Vector3.zero;
        
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t = easeType.Evaluate(elapsed / duration);
            rectTransform.localScale = Vector3.Lerp(Vector3.zero, startScale, t);
            yield return null;
        }
        
        rectTransform.localScale = startScale;
    }
}
```

---

## Inspector Configuration Per Scene Variant

### For MachinesCave_02_Stage01:

**ScreenSequenceController:**
- Sequence Stage ID: 1
- Require All Hotspots Clicked: false (player can explore at own pace)
- Completion Mind Log Text: "I... I don't understand what I just saw... but I feel like I understand more now..."
- Teleport Scene Name: "MachinesCave_01_Stage01"
- Teleport Delay: 2.0

**Screen Image Panel:**
- Stage Texture: Stage01_ScreenImage
- 8-12 Hotspots positioned on interactive areas
- Each with linked animations and Mind Log events

---

## Data Flow

```
Player Approach
    ↓
Show "Press E" Prompt (NotificationPanelController)
    ↓
Player Presses E
    ↓
ScreenSequenceController.StartSequence()
    ├→ Open Codex (Mind Log view)
    └→ Activate ScreenImagePanel
    ↓
Player Clicks Hotspot
    ↓
ScreenHotspot.OnPointerClick()
    ├→ Play click sound
    └→ Call ScreenSequenceController.OnHotspotClicked()
    ↓
ScreenSequenceController.ProcessHotspotInteraction()
    ├→ Trigger ScreenPanelAnimator
    ├→ Add Mind Log via MindLogManager
    └→ Check if sequence complete
    ↓
If Complete: ScreenSequenceController.CompleteSequence()
    ├→ Add final Mind Log
    ├→ Play completion sound
    └→ Teleport after delay
    ↓
Load MachinesCave_01 variant
```

---

## Next Steps

1. **Create ScreenSequenceController** (main coordinator)
2. **Create ScreenHotspot** (clickable areas)
3. **Create ScreenPanelAnimator** (animation handler)
4. **Set up Mind Log event system** (define which logs appear when)
5. **Create UI canvas** with screen image and hotspots
6. **Configure per-stage** (sequence ID, image, hotspots, Mind Logs)
7. **Test hotspot clicks** → animations → Mind Logs
8. **Add scene teleportation** on completion
9. **Create scene variants** (Stage01-04 in both caves)
10. **Build out full story** with images, panels, reveals

---

## Future Enhancements

- **Dialogue boxes** on top of screen image (like actual comic panels)
- **Conditional hotspots** (some only appear if others clicked first)
- **Multiple branches** (different hotspots lead to different story outcomes)
- **Inventory system** (collect items during sequences)
- **Dialogue interactions** (talk to characters in comic)
- **Puzzle elements** (solve mini-puzzles to progress)
