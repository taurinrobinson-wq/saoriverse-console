using UnityEngine;
using TMPro;
using System.Collections;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

/// <summary>
/// Handles ONLY Notification UI (interaction prompts, alerts)
/// Independent from DialogueUIController, DiaryController, and CodexController
/// </summary>
public class NotificationPanelController : MonoBehaviour
{
    [Header("Notification Panel")]
    public CanvasGroup notificationPanel;
    public TextMeshProUGUI notificationText;

    [Header("Animation")]
    public float fadeDuration = 0.3f;

    private Canvas _cachedCanvas;
    private Coroutine _currentFadeCoroutine;

    private void Awake()
    {
        // Mark this controller as persistent across scenes
        DontDestroyOnLoad(gameObject);
        Debug.Log("[Notification] NotificationPanelController marked as persistent across scenes");

        // Find NotificationPanel in UI_Canvas
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
        // FORCE canvas to stay active if it got deactivated
        if (_cachedCanvas != null && !_cachedCanvas.gameObject.activeSelf)
        {
            _cachedCanvas.gameObject.SetActive(true);
            Debug.LogWarning("[Notification] Canvas was deactivated - re-activating it!");
        }
        
        // Also ensure Canvas component is enabled
        if (_cachedCanvas != null && !_cachedCanvas.enabled)
        {
            _cachedCanvas.enabled = true;
            Debug.LogWarning("[Notification] Canvas component was disabled - re-enabling it!");
        }
    }

    /// <summary>
    /// Show a notification with optional auto-hide after duration
    /// </summary>
    public void ShowNotification(string text, float duration = 3f)
    {
        if (notificationText != null)
        {
            notificationText.text = text;
        }

        // Stop any existing fade coroutine
        if (_currentFadeCoroutine != null)
        {
            StopCoroutine(_currentFadeCoroutine);
        }

        // Fade in and auto-hide
        _currentFadeCoroutine = StartCoroutine(FadeInThenOut(duration));
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

        if (notificationPanel != null)
        {
            StartCoroutine(FadeTo(0f, fadeDuration));
        }
        Debug.Log("[Notification] Notification hidden");
    }

    private IEnumerator FadeInThenOut(float displayDuration)
    {
        // Fade in
        yield return StartCoroutine(FadeTo(1f, fadeDuration));
        
        // Show for duration
        yield return new WaitForSeconds(displayDuration);
        
        // Fade out
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
