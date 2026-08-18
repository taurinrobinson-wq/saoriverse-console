using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections;
using System.Collections.Generic;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

public class DiaryController : MonoBehaviour
{
    [Header("Page Visuals")]
    public Image pageBackground;
    public Button nextButton;
    public Button prevButton;

    [Header("Text Layers")]
    public TextMeshProUGUI textDisplay;

    [Header("Animation Settings")]
    public float swingDuration = 0.5f;
    [SerializeField] private Vector2 openPosition = new Vector2(300, -400);  // Upper-left area (anchored at top-left)
    [SerializeField] private Vector2 closedPosition = new Vector2(300, -1200f);  // Off-screen below

    private bool diaryOpen = false;
    private bool isAnimating = false;
    private CanvasGroup cg;
    private RectTransform rectTransform;

    private int currentIndex = 0;
    private List<string> entries = new List<string>();

    public bool IsAnimating => isAnimating;
    public bool IsOpen => diaryOpen;

#if ENABLE_INPUT_SYSTEM
    private InputAction _nextPageAction;
    private InputAction _prevPageAction;

    private void OnEnable()
    {
        _nextPageAction = new InputAction("NextPage", binding: "<Keyboard>/rightArrow");
        _prevPageAction = new InputAction("PrevPage", binding: "<Keyboard>/leftArrow");
        _nextPageAction.Enable();
        _prevPageAction.Enable();
    }

    private void OnDisable()
    {
        _nextPageAction?.Disable();
        _prevPageAction?.Disable();
    }
#endif

    void Start()
    {
        Debug.Log("[Diary] DiaryController.Start() called!");
        cg = GetComponent<CanvasGroup>();
        if (cg == null) cg = gameObject.AddComponent<CanvasGroup>();
        rectTransform = GetComponent<RectTransform>();
        
        Debug.Log($"[Diary] CanvasGroup found: {(cg != null ? "YES" : "NO")}, RectTransform found: {(rectTransform != null ? "YES" : "NO")}");
        
        // Set anchors to upper-left corner for proper positioning
        rectTransform.anchorMin = new Vector2(0, 1);  // Top-left
        rectTransform.anchorMax = new Vector2(0, 1);  // Top-left
        rectTransform.pivot = new Vector2(0, 1);      // Top-left pivot
        
        Debug.Log($"[Diary] Anchors set to: Min=(0, 1), Max=(0, 1), Pivot=(0, 1)");
        
        // Set the initial closed position
        rectTransform.anchoredPosition = closedPosition;
        cg.interactable = false;
        cg.blocksRaycasts = false;
        cg.alpha = 0f;
        
        Debug.Log($"[Diary] Initial position set to: {rectTransform.anchoredPosition}, alpha: {cg.alpha}");
    }

    void Update()
    {
        // CHECK FOR N KEY FIRST (toggle diary open/close)
        bool nPressed = false;

#if ENABLE_INPUT_SYSTEM
        var keyboard = Keyboard.current;
        if (keyboard != null && keyboard.nKey.wasPressedThisFrame)
            nPressed = true;
#endif

        if (nPressed)
        {
            Debug.Log("[Diary] N key pressed - toggling diary");
            Toggle();
            return;
        }

        // Only handle page navigation if diary is open and not animating
        if (!diaryOpen || isAnimating) return;

        bool nextPressed = false;
        bool prevPressed = false;

#if ENABLE_INPUT_SYSTEM
        if (_nextPageAction != null && _nextPageAction.WasPressedThisFrame()) nextPressed = true;
        if (_prevPageAction != null && _prevPageAction.WasPressedThisFrame()) prevPressed = true;

        if (keyboard != null)
        {
            if (keyboard.rightArrowKey.wasPressedThisFrame) nextPressed = true;
            if (keyboard.leftArrowKey.wasPressedThisFrame) prevPressed = true;
        }
#endif

        if (nextPressed)
        {
            NextPage();
        }
        else if (prevPressed)
        {
            PrevPage();
        }
    }

    public void Toggle()
    {
        Debug.Log($"[Diary] Toggle() called! isAnimating={isAnimating}, diaryOpen={diaryOpen}");
        if (isAnimating) 
        {
            Debug.Log("[Diary] Already animating, ignoring toggle request");
            return;
        }
        
        if (!diaryOpen) 
        {
            Debug.Log("[Diary] Starting OpenDiary coroutine");
            StartCoroutine(OpenDiary());
        }
        else 
        {
            Debug.Log("[Diary] Starting CloseDiary coroutine");
            StartCoroutine(CloseDiary());
        }
    }

    public void SetEntries(List<string> newEntries)
    {
        entries = newEntries;
        currentIndex = 0;
        UpdatePageText();
    }

    private void UpdatePageText()
    {
        if (textDisplay != null)
        {
            textDisplay.text = (entries != null && currentIndex < entries.Count) ? entries[currentIndex] : "";
        }

        if (nextButton != null)
        {
            nextButton.interactable = entries != null && currentIndex < entries.Count - 1;
        }

        if (prevButton != null)
        {
            prevButton.interactable = currentIndex > 0;
        }
    }

    public void NextPage()
    {
        if (isAnimating) return;
        if (currentIndex < entries.Count - 1)
        {
            currentIndex++;
            UpdatePageText();
        }
    }

    public void PrevPage()
    {
        if (isAnimating) return;
        if (currentIndex > 0)
        {
            currentIndex--;
            UpdatePageText();
        }
    }

    public IEnumerator OpenDiary()
    {
        Debug.Log("[Diary] OpenDiary coroutine started!");
        isAnimating = true;
        diaryOpen = true;
        cg.interactable = true;
        cg.blocksRaycasts = true;
        cg.alpha = 1f;

        UpdatePageText();

        float t = 0f;
        while (t < swingDuration)
        {
            t += Time.deltaTime;
            float normalized = t / swingDuration;
            float eased = 1f - Mathf.Pow(1f - normalized, 3f);
            rectTransform.anchoredPosition = Vector2.Lerp(closedPosition, openPosition, eased);
            yield return null;
        }

        rectTransform.anchoredPosition = openPosition;
        isAnimating = false;
        Debug.Log($"[Diary] OpenDiary complete! Final position: {rectTransform.anchoredPosition}");
    }

    public IEnumerator CloseDiary()
    {
        Debug.Log("[Diary] CloseDiary coroutine started!");
        isAnimating = true;
        diaryOpen = false;
        cg.interactable = false;
        cg.blocksRaycasts = false;

        float t = 0f;
        while (t < swingDuration)
        {
            t += Time.deltaTime;
            float normalized = t / swingDuration;
            float eased = Mathf.Pow(normalized, 3f);
            rectTransform.anchoredPosition = Vector2.Lerp(openPosition, closedPosition, eased);
            yield return null;
        }

        rectTransform.anchoredPosition = closedPosition;
        cg.alpha = 0f;
        isAnimating = false;
        Debug.Log($"[Diary] CloseDiary complete! Final position: {rectTransform.anchoredPosition}");
    }
}


