using UnityEngine;
using UnityEngine.UI;
using System.Collections;

/// <summary>
/// Handles fade-to-black transitions during dialogue beats.
/// Works like stage lighting: lights fade to black, props are rearranged (triggers fired),
/// then lights fade back in to reveal the new scene.
/// 
/// Used for seamless scene transitions without restarting dialogue.
/// </summary>
public class DialogueTransitionFade : MonoBehaviour
{
    private Image fadeImage;
    private float fadeDuration = 0.5f;
    private float holdDuration = 0.5f;

    private void OnEnable()
    {
        // Find or create the fade image
        if (fadeImage == null)
        {
            // Try to find existing fade image
            fadeImage = GameObject.Find("TransitionFadeImage")?.GetComponent<Image>();
            
            if (fadeImage == null)
            {
                Debug.LogWarning("[DialogueTransitionFade] TransitionFadeImage not found. Creating one...");
                CreateFadeImage();
            }
        }
    }

    private void CreateFadeImage()
    {
        // Find the canvas
        Canvas canvas = FindAnyObjectByType<Canvas>();
        if (canvas == null)
        {
            Debug.LogError("[DialogueTransitionFade] No Canvas found in scene!");
            return;
        }

        // Create fade image GameObject
        GameObject fadeObj = new GameObject("TransitionFadeImage");
        fadeObj.transform.SetParent(canvas.transform, false);

        // Setup RectTransform to fill entire screen
        RectTransform rectTransform = fadeObj.AddComponent<RectTransform>();
        rectTransform.anchorMin = Vector2.zero;
        rectTransform.anchorMax = Vector2.one;
        rectTransform.offsetMin = Vector2.zero;
        rectTransform.offsetMax = Vector2.zero;

        // Add Image component
        fadeImage = fadeObj.AddComponent<Image>();
        fadeImage.color = new Color(0, 0, 0, 0); // Black, fully transparent

        // Set sort order so it's on top
        Canvas fadeCanvas = fadeObj.AddComponent<Canvas>();
        fadeCanvas.renderMode = RenderMode.ScreenSpaceOverlay;
        GraphicRaycaster raycaster = fadeObj.AddComponent<GraphicRaycaster>();

        Debug.Log("[DialogueTransitionFade] Created TransitionFadeImage");
    }

    /// <summary>
    /// Execute the fade-to-black transition with prop changes.
    /// Fades to black, fires triggers, pauses, then fades back in.
    /// </summary>
    public void ExecuteTransitionFade(System.Action onFadeComplete)
    {
        StartCoroutine(TransitionFadeRoutine(onFadeComplete));
    }

    private IEnumerator TransitionFadeRoutine(System.Action onFadeComplete)
    {
        if (fadeImage == null)
        {
            Debug.LogError("[DialogueTransitionFade] fadeImage is null!");
            yield break;
        }

        Color fadeColor = fadeImage.color;

        // 1. Fade to black (alpha 0 → 255)
        yield return StartCoroutine(FadeToAlpha(1f, fadeDuration));

        Debug.Log("[DialogueTransitionFade] Fade complete, screen is black. Props are now being rearranged...");

        // 2. While screen is black, trigger the system events (debris_clear, glyph_appear)
        onFadeComplete?.Invoke();

        // 3. Hold on black screen for a moment
        yield return new WaitForSeconds(holdDuration);

        // 4. Fade back in (alpha 255 → 0)
        yield return StartCoroutine(FadeToAlpha(0f, fadeDuration));

        Debug.Log("[DialogueTransitionFade] Lights back up! Scene transition complete.");
    }

    private IEnumerator FadeToAlpha(float targetAlpha, float duration)
    {
        Color startColor = fadeImage.color;
        Color targetColor = startColor;
        targetColor.a = targetAlpha;

        float elapsed = 0f;

        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / duration;
            fadeImage.color = Color.Lerp(startColor, targetColor, t);
            yield return null;
        }

        fadeImage.color = targetColor;
    }
}
