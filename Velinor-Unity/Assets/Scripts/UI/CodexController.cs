using UnityEngine;
using UnityEngine.UI;
using TMPro;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

/// <summary>
/// Handles ONLY Codex UI (Glyph system)
/// Triggered by: C key + player has received codex from Saori
/// Independent from DialogueUIController and DiaryController
/// </summary>
public class CodexController : MonoBehaviour
{
    [Header("Codex Panel")]
    public CanvasGroup codexPanel;
    public Transform viewport;
    public Image codexImage;
    public Sprite codexBackgroundSprite;  // Assign Glyph_Codex2.png in Inspector

    [Header("Navigation")]
    public TextMeshProUGUI glyphNameText;
    public Button nextPageBtn;
    public Button prevPageBtn;

    [Header("Fonts")]
    public TMP_FontAsset codexFont;

    [Header("Codex Access")]
    public bool requiresCodexDevice = true;  // Set to false for testing
    private bool playerHasCodex = false;

    private int _currentCodexPage = 0;
    private const int GlyphsPerPage = 9;

#if ENABLE_INPUT_SYSTEM
    private InputAction _toggleCodexAction;
    private InputAction _leftAction;
    private InputAction _rightAction;

    private void OnEnable()
    {
        _toggleCodexAction = new InputAction("ToggleCodex", binding: "<Keyboard>/c");
        _leftAction = new InputAction("Left", binding: "<Keyboard>/leftArrow");
        _rightAction = new InputAction("Right", binding: "<Keyboard>/rightArrow");

        _toggleCodexAction.Enable();
        _leftAction.Enable();
        _rightAction.Enable();
    }

    private void OnDisable()
    {
        _toggleCodexAction?.Disable();
        _leftAction?.Disable();
        _rightAction?.Disable();
    }
#endif

    private Canvas _cachedCanvas;

    private void Awake()
    {
        // Mark this controller as persistent across scenes
        DontDestroyOnLoad(gameObject);
        Debug.Log("[Codex] CodexController marked as persistent across scenes");

        // Find CodexPanel in UI_Canvas
        Canvas[] allCanvases = FindObjectsByType<Canvas>();
        foreach (Canvas c in allCanvases)
        {
            if (c.gameObject.name == "UI_Canvas")
            {
                _cachedCanvas = c;
                
                Transform codexPanelT = FindPanelRecursive(c.transform, "CodexPanel");
                if (codexPanelT != null)
                {
                    codexPanel = codexPanelT.GetComponent<CanvasGroup>();
                    codexImage = codexPanelT.GetComponent<Image>();
                    viewport = codexPanelT.Find("Viewport");
                    glyphNameText = codexPanelT.Find("Navigation/GlyphName")?.GetComponent<TextMeshProUGUI>();
                    nextPageBtn = codexPanelT.Find("Navigation/NextBtn")?.GetComponent<Button>();
                    prevPageBtn = codexPanelT.Find("Navigation/PrevBtn")?.GetComponent<Button>();
                    
                    Debug.Log("[Codex] CodexPanel found and assigned");
                }
                break;
            }
        }

        if (nextPageBtn != null) nextPageBtn.onClick.AddListener(NextPage);
        if (prevPageBtn != null) prevPageBtn.onClick.AddListener(PrevPage);
    }

    private Transform FindPanelRecursive(Transform parent, string panelName)
    {
        if (parent.name == panelName)
            return parent;

        foreach (Transform child in parent)
        {
            Transform result = FindPanelRecursive(child, panelName);
            if (result != null)
                return result;
        }
        return null;
    }

    private void Start()
    {
        // Check canvas status at Start
        if (_cachedCanvas != null)
        {
            Debug.Log($"[Codex] Canvas status at Start: Active={_cachedCanvas.gameObject.activeSelf}, Enabled={_cachedCanvas.enabled}");
            if (!_cachedCanvas.gameObject.activeSelf)
            {
                _cachedCanvas.gameObject.SetActive(true);
                Debug.LogWarning("[Codex] Canvas was inactive at Start - re-activating it!");
            }
        }

        if (codexPanel != null)
        {
            codexPanel.alpha = 0f;
            codexPanel.blocksRaycasts = false;
            codexPanel.interactable = false;
            Debug.Log("[Codex] CodexPanel initialized (hidden)");
        }

        // Assign the codex background sprite if provided
        if (codexImage != null && codexBackgroundSprite != null)
        {
            codexImage.sprite = codexBackgroundSprite;
            codexImage.type = Image.Type.Simple;
            codexImage.preserveAspect = true;
            Debug.Log($"[Codex] Codex background sprite assigned: {codexBackgroundSprite.name}");
            Debug.Log($"[Codex] Image component: enabled={codexImage.enabled}, raycastTarget={codexImage.raycastTarget}");
        }
        else if (codexImage != null && codexBackgroundSprite == null)
        {
            Debug.LogWarning("[Codex] codexBackgroundSprite is not assigned in Inspector!");
        }

        // For testing: allow access if not requiring device
        if (!requiresCodexDevice)
        {
            playerHasCodex = true;
            Debug.Log("[Codex] TEST MODE: Codex access enabled (no device required)");
        }
    }

    private void Update()
    {
        // FORCE canvas to stay active if it got deactivated
        if (_cachedCanvas != null && !_cachedCanvas.gameObject.activeSelf)
        {
            _cachedCanvas.gameObject.SetActive(true);
            Debug.LogWarning("[Codex] Canvas GameObject was deactivated - re-activating it!");
        }
        
        // Also ensure Canvas component is enabled (DialogueManager disables it)
        if (_cachedCanvas != null && !_cachedCanvas.enabled)
        {
            _cachedCanvas.enabled = true;
            Debug.LogWarning("[Codex] Canvas component was disabled - re-enabling it!");
        }

        bool cPressed = false;
        bool leftPressed = false;
        bool rightPressed = false;

#if ENABLE_INPUT_SYSTEM
        if (_toggleCodexAction != null && _toggleCodexAction.WasPressedThisFrame())
            cPressed = true;

        if (_leftAction != null && _leftAction.WasPressedThisFrame())
            leftPressed = true;

        if (_rightAction != null && _rightAction.WasPressedThisFrame())
            rightPressed = true;

        var keyboard = Keyboard.current;
        if (keyboard != null)
        {
            if (keyboard.cKey.wasPressedThisFrame) cPressed = true;
            if (keyboard.leftArrowKey.wasPressedThisFrame) leftPressed = true;
            if (keyboard.rightArrowKey.wasPressedThisFrame) rightPressed = true;
        }
#endif

        if (cPressed)
        {
            if (playerHasCodex || !requiresCodexDevice)
            {
                ToggleCodex();
            }
            else
            {
                Debug.Log("[Codex] Player does not have codex device yet");
            }
        }

        if (codexPanel != null && codexPanel.alpha > 0.5f)
        {
            if (leftPressed) PrevPage();
            if (rightPressed) NextPage();
        }
    }

    public void ToggleCodex()
    {
        if (codexPanel == null)
        {
            Debug.LogError("[Codex] codexPanel is NULL");
            return;
        }

        bool opening = codexPanel.alpha < 0.5f;
        Debug.Log($"[Codex] ToggleCodex: opening={opening}");

        codexPanel.alpha = opening ? 1f : 0f;
        codexPanel.blocksRaycasts = opening;
        codexPanel.interactable = opening;

        // Set image color to WHITE so sprite shows (not black)
        if (codexImage != null)
        {
            codexImage.color = opening ? new Color(1, 1, 1, 1f) : new Color(1, 1, 1, 0);
            Debug.Log($"[Codex] Image color set to {codexImage.color}");
        }

        // Activate/deactivate viewport
        if (viewport != null)
        {
            viewport.gameObject.SetActive(opening);
            Debug.Log($"[Codex] Viewport set to Active: {opening}");
        }

        if (opening)
        {
            _currentCodexPage = 0;
            UpdateCodexUI();
        }

        Debug.Log($"[Codex] Codex panel now {(opening ? "OPEN" : "CLOSED")}");
    }

    public void NextPage()
    {
        _currentCodexPage++;
        UpdateCodexUI();
    }

    public void PrevPage()
    {
        if (_currentCodexPage > 0)
        {
            _currentCodexPage--;
            UpdateCodexUI();
        }
    }

    private void UpdateCodexUI()
    {
        if (codexPanel == null) return;

        // TODO: Wire this to actual CodexManager or game data system
        // For now, show placeholder text

        if (glyphNameText != null)
        {
            glyphNameText.text = $"Codex - Page {_currentCodexPage + 1}";
        }

        // Debug: Check and visualize the grid slots
        Transform gridT = codexPanel.transform.Find("GlyphGrid");
        if (gridT != null)
        {
            Debug.Log($"[Codex] GlyphGrid found with {gridT.childCount} children (slots)");
            for (int i = 0; i < gridT.childCount; i++)
            {
                Transform slot = gridT.GetChild(i);
                Image slotImage = slot.GetComponent<Image>();
                RectTransform slotRect = slot.GetComponent<RectTransform>();
                
                Debug.Log($"[Codex]   Slot_{i}: Image={slotImage != null}, Size={slotRect?.sizeDelta}, " +
                    $"Color={slotImage?.color}, Active={slot.gameObject.activeSelf}");
                
                // If slot doesn't have Image, add a debug one
                if (slotImage == null)
                {
                    slotImage = slot.gameObject.AddComponent<Image>();
                    slotImage.color = new Color(0.2f, 0.2f, 0.2f, 1f);  // Dark gray for visibility
                    Debug.Log($"[Codex]   ⚠ Slot_{i} had NO Image - added placeholder!");
                }
            }
        }
        else
        {
            Debug.LogWarning("[Codex] GlyphGrid not found!");
        }

        // Log all CodexPanel children for structure debugging
        Debug.Log($"[Codex] CodexPanel children count: {codexPanel.transform.childCount}");
        foreach (Transform child in codexPanel.transform)
        {
            Debug.Log($"[Codex]   - Child: {child.name}, Active: {child.gameObject.activeSelf}");
        }
    }

    /// <summary>
    /// Call this when player encounters Saori and receives codex device
    /// </summary>
    public void UnlockCodex()
    {
        playerHasCodex = true;
        Debug.Log("[Codex] Codex unlocked! Player can now press C to open Codex");
    }

    /// <summary>
    /// Add a new glyph/entry to codex
    /// </summary>
    public void AddCodexEntry(string entryName)
    {
        Debug.Log($"[Codex] New entry unlocked: {entryName}");
        // TODO: Wire to actual codex data system
    }
}
