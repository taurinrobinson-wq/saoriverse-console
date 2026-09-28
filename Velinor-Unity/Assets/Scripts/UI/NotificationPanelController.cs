using UnityEngine;
using TMPro;
using System.Collections;
using System.Collections.Generic;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

/// <summary>
/// Handles ONLY Notification UI (interaction prompts, alerts)
/// Independent from DialogueUIController, DiaryController, and CodexController
/// 
/// Supports interruptible notifications:
/// - New notification cancels current one's display timer
/// - Fades to new notification immediately
/// - Each notification displays for full duration unless interrupted
/// </summary>
public class NotificationPanelController : MonoBehaviour
{
    [Header("Notification Panel")]
    public CanvasGroup notificationPanel;
    public TextMeshProUGUI notificationText;

    [Header("Animation")]
    public float fadeDuration = 0.15f;
    public float displayDuration = 3f;

    private Canvas _cachedCanvas;
    private Coroutine _currentFadeCoroutine;
    private Coroutine _displayTimerCoroutine;  // Separate timer for display duration
    private bool _canvasChecked = false;

    private void Awake()
    {
        DontDestroyOnLoad(gameObject);
        Debug.Log("[Notification] NotificationPanelController marked as persistent across scenes");

        Canvas[] allCanvases = FindObjectsByType<Canvas>();
        foreach (Canvas c in allCanvases)
        {
            if (c.gameObject.name == "UI_Canvas")
            {
                _cachedCanvas = c;
                
                Transform notifPanelT = FindPanelRecursive(c.transform, "NotificationPanel");
                if (notifPanelT != null)
                {
                    notificationPanel = notifPanelT.GetComponent<CanvasGroup>();
                    notificationText = notifPanelT.Find("NotificationText")?.GetComponent<TextMeshProUGUI>();
                    Debug.Log("[Notification] NotificationPanel found and assigned");
                }
                break;
            }
        }
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
        if (notificationPanel != null)
        {
            notificationPanel.alpha = 0f;
            notificationPanel.blocksRaycasts = false;
            notificationPanel.interactable = false;
            Debug.Log("[Notification] NotificationPanel initialized (hidden)");
        }
    }

    private void Update()
    {
        if (!_canvasChecked && _cachedCanvas != null)
        {
            if (!_cachedCanvas.gameObject.activeSelf)
            {
                _cachedCanvas.gameObject.SetActive(true);
                Debug.LogWarning("[Notification] Canvas was deactivated - re-activating it!");
            }
            
            if (!_cachedCanvas.enabled)
            {
                _cachedCanvas.enabled = true;
                Debug.LogWarning("[Notification] Canvas component was disabled - re-enabling it!");
            }
            
            _canvasChecked = true;
        }
    }

    /// <summary>
    /// Show a notification. If one is already showing, it interrupts and displays immediately.
    /// New notification will display for full duration unless another comes in.
    /// </summary>
    public void ShowNotification(string text, float duration = -1f)
    {
        if (duration < 0)
            duration = displayDuration;

        Debug.Log($"[Notification] ShowNotification called: '{text}' (duration: {duration}s)");

        // Cancel current display timer - new notification interrupts it
        if (_displayTimerCoroutine != null)
        {
            StopCoroutine(_displayTimerCoroutine);
            Debug.Log("[Notification] Display timer interrupted by new notification");
        }

        // Cancel fade coroutine if one is running
        if (_currentFadeCoroutine != null)
        {
            StopCoroutine(_currentFadeCoroutine);
        }

        // Update text
        if (notificationText != null)
        {
            notificationText.text = text;
        }

        // Fade in immediately and start display timer
        _currentFadeCoroutine = StartCoroutine(FadeInAndStartTimer(duration));
        Debug.Log($"[Notification] Showing: {text}");
    }

    /// <summary>
    /// Hide the notification immediately
    /// </summary>
    public void HideNotification()
    {
        if (_currentFadeCoroutine != null)
        {
            StopCoroutine(_currentFadeCoroutine);
        }

        if (_displayTimerCoroutine != null)
        {
            StopCoroutine(_displayTimerCoroutine);
        }

        if (notificationPanel != null)
        {
            StartCoroutine(FadeTo(0f, fadeDuration));
        }
        Debug.Log("[Notification] Notification hidden");
    }

    private IEnumerator FadeInAndStartTimer(float duration)
    {
        // Fade in
        yield return StartCoroutine(FadeTo(1f, fadeDuration));
        
        // Start display timer (can be interrupted by new notification)
        _displayTimerCoroutine = StartCoroutine(DisplayTimer(duration));
    }

    private IEnumerator DisplayTimer(float duration)
    {
        // Show for duration (can be interrupted)
        yield return new WaitForSeconds(duration);
        
        // Auto-fade out after duration expires (only if not interrupted)
        yield return StartCoroutine(FadeTo(0f, fadeDuration));
    }

    private IEnumerator FadeTo(float targetAlpha, float duration)
    {
        if (notificationPanel == null) yield break;

        float startAlpha = notificationPanel.alpha;
        float elapsed = 0f;

        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            notificationPanel.alpha = Mathf.Lerp(startAlpha, targetAlpha, elapsed / duration);
            yield return null;
        }

        notificationPanel.alpha = targetAlpha;
    }
}
