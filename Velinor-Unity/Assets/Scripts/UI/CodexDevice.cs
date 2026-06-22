using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System.Collections.Generic;

public class CodexDevice : MonoBehaviour
{
    [SerializeField] private Image deviceImage;
    [SerializeField] private CanvasGroup deviceCanvasGroup;
    [SerializeField] private RectTransform deviceRect;
    
    private bool isVisible = false;
    private int currentGlyphPage = 0; // Each page shows 9 glyphs
    private List<string> availableGlyphs = new List<string>();
    private string selectedGlyph = "";
    
    private Vector3 hiddenPosition;
    private Vector3 visiblePosition;
    private float animationDuration = 0.4f;

    private void Start()
    {
        // Initialize glyph list (these would come from your game state)
        InitializeGlyphs();
        
        // Set up positions for animation
        if (deviceRect != null)
        {
            hiddenPosition = new Vector3(-500, -400, 0); // Off-screen bottom-left
            visiblePosition = new Vector3(-300, -200, 0); // On-screen, left side
            deviceRect.anchoredPosition = hiddenPosition;
        }
        
        // Start with device hidden
        if (deviceCanvasGroup != null)
        {
            deviceCanvasGroup.alpha = 0;
        }
    }

    private void Update()
    {
        // Toggle device with G key
        if (Input.GetKeyDown(KeyCode.G))
        {
            ToggleDevice();
        }

        // Navigation buttons when device is visible
        if (isVisible)
        {
            if (Input.GetKeyDown(KeyCode.Left) || Input.GetKeyDown(KeyCode.A))
            {
                PreviousPage();
            }
            if (Input.GetKeyDown(KeyCode.Right) || Input.GetKeyDown(KeyCode.D))
            {
                NextPage();
            }
            if (Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.Space))
            {
                SelectGlyph();
            }
        }
    }

    public void ToggleDevice()
    {
        if (isVisible)
        {
            HideDevice();
        }
        else
        {
            ShowDevice();
        }
    }

    private void ShowDevice()
    {
        if (isVisible) return;
        
        isVisible = true;
        StopAllCoroutines();
        StartCoroutine(AnimateDeviceIn());
    }

    private void HideDevice()
    {
        if (!isVisible) return;
        
        isVisible = false;
        StopAllCoroutines();
        StartCoroutine(AnimateDeviceOut());
    }

    private IEnumerator AnimateDeviceIn()
    {
        float elapsed = 0f;
        Vector3 startPos = hiddenPosition;
        
        if (deviceCanvasGroup != null)
        {
            deviceCanvasGroup.alpha = 0;
        }

        while (elapsed < animationDuration)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / animationDuration;
            
            if (deviceRect != null)
            {
                deviceRect.anchoredPosition = Vector3.Lerp(startPos, visiblePosition, EaseOutCubic(t));
            }
            
            if (deviceCanvasGroup != null)
            {
                deviceCanvasGroup.alpha = Mathf.Lerp(0, 1, t);
            }
            
            yield return null;
        }

        if (deviceRect != null)
        {
            deviceRect.anchoredPosition = visiblePosition;
        }
        if (deviceCanvasGroup != null)
        {
            deviceCanvasGroup.alpha = 1;
        }
    }

    private IEnumerator AnimateDeviceOut()
    {
        float elapsed = 0f;
        Vector3 startPos = visiblePosition;

        while (elapsed < animationDuration)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / animationDuration;
            
            if (deviceRect != null)
            {
                deviceRect.anchoredPosition = Vector3.Lerp(startPos, hiddenPosition, EaseInCubic(t));
            }
            
            if (deviceCanvasGroup != null)
            {
                deviceCanvasGroup.alpha = Mathf.Lerp(1, 0, t);
            }
            
            yield return null;
        }

        if (deviceRect != null)
        {
            deviceRect.anchoredPosition = hiddenPosition;
        }
        if (deviceCanvasGroup != null)
        {
            deviceCanvasGroup.alpha = 0;
        }
    }

    private void NextPage()
    {
        int maxPages = Mathf.CeilToInt((float)availableGlyphs.Count / 9f);
        currentGlyphPage = (currentGlyphPage + 1) % maxPages;
        UpdateDeviceDisplay();
    }

    private void PreviousPage()
    {
        int maxPages = Mathf.CeilToInt((float)availableGlyphs.Count / 9f);
        currentGlyphPage--;
        if (currentGlyphPage < 0) currentGlyphPage = maxPages - 1;
        UpdateDeviceDisplay();
    }

    private void SelectGlyph()
    {
        int glyphIndex = currentGlyphPage * 9 + 4; // Center button
        if (glyphIndex < availableGlyphs.Count)
        {
            selectedGlyph = availableGlyphs[glyphIndex];
            Debug.Log($"🔮 Selected Glyph: {selectedGlyph}");
            // TODO: Trigger gameplay effect with selected glyph
        }
    }

    private void UpdateDeviceDisplay()
    {
        // Update UI to show current page of glyphs
        Debug.Log($"📖 Device Page: {currentGlyphPage + 1}");
    }

    private void InitializeGlyphs()
    {
        // Placeholder glyph list - would be loaded from game state
        for (int i = 0; i < 27; i++) // 3 pages of 9 glyphs
        {
            availableGlyphs.Add($"Glyph_{i + 1}");
        }
    }

    public string GetSelectedGlyph()
    {
        return selectedGlyph;
    }

    // Easing functions
    private float EaseOutCubic(float t)
    {
        float f = t - 1f;
        return f * f * f + 1f;
    }

    private float EaseInCubic(float t)
    {
        return t * t * t;
    }
}
