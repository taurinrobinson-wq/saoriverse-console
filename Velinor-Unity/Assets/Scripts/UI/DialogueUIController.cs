using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

public class DialogueUIController : MonoBehaviour
{
    [Header("UI Panels")]
    public CanvasGroup codexPanel;
    public CanvasGroup diaryPanel;
    public CanvasGroup notificationPanel;
    public TextMeshProUGUI notificationText;

    private void Update()
    {
#if ENABLE_INPUT_SYSTEM
        if (Keyboard.current != null)
        {
            if (Keyboard.current.cKey.wasPressedThisFrame)
            {
                ToggleCodex();
            }
            if (Keyboard.current.nKey.wasPressedThisFrame)
            {
                ToggleDiary();
            }
        }
#else
        if (Input.GetKeyDown(KeyCode.C))
        {
            ToggleCodex();
        }
        if (Input.GetKeyDown(KeyCode.N))
        {
            ToggleDiary();
        }
        if (Input.GetKeyDown(KeyCode.E))
        {
            TryInteract();
        }
#endif
    }

    public void ToggleCodex()
    {
        if (codexPanel == null) return;
        bool opening = codexPanel.alpha < 0.5f;
        codexPanel.alpha = opening ? 1f : 0f;
        codexPanel.blocksRaycasts = opening;
        codexPanel.interactable = opening;
        
        if (opening)
        {
            UpdateCodexUI();
        }
    }

    private void UpdateCodexUI()
    {
        var codexImage = codexPanel.transform.Find("CodexImage");
        if (codexImage == null) return;

        // Clear previous
        foreach (Transform child in codexImage)
        {
            Destroy(child.gameObject);
        }

        if (Velinor.Core.CodexManager.Instance == null) return;
        var state = Velinor.Core.CodexManager.Instance.State;

        GameObject textObj = new GameObject("CodexText");
        textObj.transform.SetParent(codexImage, false);
        var textMesh = textObj.AddComponent<TextMeshProUGUI>();
        textMesh.fontSize = 20;
        textMesh.color = Color.white;
        textMesh.alignment = TextAlignmentOptions.Center;

        string fullContent = "<b>🌌 CODEX DEVICE</b>\n\n";
        fullContent += $"Resonance Level: <color=#00FFFF>{state.ResonanceLevel * 100:F1}%</color>\n\n";
        fullContent += "<b>Active Emotional Tags:</b>\n";
        if (state.ActiveTags.Count == 0)
        {
            fullContent += "<i>None. Converse with others to unlock emotional resonance.</i>\n";
        }
        else
        {
            foreach (var tag in state.ActiveTags)
            {
                fullContent += $"• <color=#FFAAAA>{tag}</color>\n";
            }
        }

        fullContent += "\n<b>Resolved Glyphs:</b>\n";
        if (state.ResolvedGlyphIds.Count == 0)
        {
            fullContent += "<i>None yet. Discover hidden glyph structures in the world.</i>";
        }
        else
        {
            fullContent += $"• {state.ResolvedGlyphIds.Count} glyphs resolved.";
        }

        textMesh.text = fullContent;
    }

    public void ToggleDiary()
    {
        if (diaryPanel == null) return;
        bool opening = diaryPanel.alpha < 0.5f;
        diaryPanel.alpha = opening ? 1f : 0f;
        diaryPanel.blocksRaycasts = opening;
        diaryPanel.interactable = opening;
        
        if (opening)
        {
            UpdateDiaryUI();
        }
    }

    private void UpdateDiaryUI()
    {
        var viewport = diaryPanel.transform.Find("Viewport");
        if (viewport == null) return;
        var content = viewport.Find("Content");
        if (content == null) return;

        // Clear previous
        foreach (Transform child in content)
        {
            Destroy(child.gameObject);
        }

        if (DiaryManager.Instance == null) return;
        var entries = DiaryManager.Instance.GetEntries();

        GameObject textObj = new GameObject("DiaryText");
        textObj.transform.SetParent(content, false);
        var textMesh = textObj.AddComponent<TextMeshProUGUI>();
        textMesh.fontSize = 18;
        textMesh.color = Color.white;
        textMesh.lineSpacing = 1.2f;

        string fullContent = "<b>📖 DIARY ENTRIES</b>\n\n";
        if (entries.Count == 0)
        {
            fullContent += "<i>No entries yet. Explore the ruins and speak to Remnants.</i>";
        }
        else
        {
            foreach (var entry in entries)
            {
                fullContent += $"<color=#8888FF>[{entry.timestamp}]</color>\n{entry.content}\n\n";
            }
        }
        textMesh.text = fullContent;

        var layout = content.GetComponent<VerticalLayoutGroup>();
        if (layout == null)
        {
            layout = content.gameObject.AddComponent<VerticalLayoutGroup>();
            layout.childControlHeight = true;
            layout.childControlWidth = true;
            layout.childForceExpandHeight = false;
            layout.childForceExpandWidth = true;
            layout.padding = new RectOffset(10, 10, 10, 10);
            layout.spacing = 10;
        }

        var fitter = content.GetComponent<ContentSizeFitter>();
        if (fitter == null)
        {
            fitter = content.gameObject.AddComponent<ContentSizeFitter>();
            fitter.verticalFit = ContentSizeFitter.FitMode.PreferredSize;
        }
    }

    private void TryInteract()
    {
        Debug.Log("Interact [E] pressed");
    }

    private void EnsureReferences()
    {
        if (notificationPanel == null || notificationPanel.gameObject == null || notificationText == null || notificationText.gameObject == null)
        {
            var canvas = GameObject.Find("DialogueCanvas");
            if (canvas == null) canvas = GameObject.Find("UI_Canvas");
            if (canvas != null)
            {
                var prompt = canvas.transform.Find("InteractionPrompt");
                if (prompt == null) prompt = canvas.transform.Find("NotificationPanel");
                
                if (prompt != null)
                {
                    notificationPanel = prompt.GetComponent<CanvasGroup>();
                    if (notificationPanel == null) notificationPanel = prompt.gameObject.AddComponent<CanvasGroup>();
                    notificationText = prompt.GetComponentInChildren<TextMeshProUGUI>();
                }
            }
        }
    }

    // Show notification
    public void ShowNotification(string text)
    {
        EnsureReferences();
        if (notificationText == null || notificationPanel == null) return;
        
        notificationText.text = text;
        StopAllCoroutines();
        StartCoroutine(FadeNotificationRoutine());
    }

    public void SetNotificationActive(string text, bool active)
    {
        EnsureReferences();
        if (notificationText == null || notificationPanel == null) return;
        notificationText.text = text;
        notificationPanel.alpha = active ? 1f : 0f;
    }

    private IEnumerator FadeNotificationRoutine()
    {
        // Fade in
        yield return StartCoroutine(FadeCanvasGroup(notificationPanel, 1f, 0.1f));
        // Wait 3s
        yield return new WaitForSeconds(3f);
        // Fade out
        yield return StartCoroutine(FadeCanvasGroup(notificationPanel, 0f, 1f));
    }

    private IEnumerator FadeCanvasGroup(CanvasGroup cg, float targetAlpha, float duration)
    {
        float startAlpha = cg.alpha;
        float time = 0;
        while (time < duration)
        {
            time += Time.deltaTime;
            cg.alpha = Mathf.Lerp(startAlpha, targetAlpha, time / duration);
            yield return null;
        }
        cg.alpha = targetAlpha;
    }

    // Trigger system events
    public void TriggerSystemEvent(string eventName)
    {
        switch(eventName)
        {
            case "give_device":
                ShowNotification("??? Obtained. Press [C] to access Codex.");
                break;
            case "diary_update":
                ShowNotification("Diary updated. Press [N] to access.");
                break;
            case "codex_entry_unlock":
                ShowNotification("Codex Updated: Pattern Recognition unlocked.");
                break;
            case "truth_echo_unlock":
                ShowNotification("Codex Updated: Truth Echo unlocked.");
                break;
            case "story_scroll_acquire":
                ShowNotification("Story Scroll Acquired.");
                break;
            case "encounter_complete":
                ShowNotification("Encounter Complete: Saori's Remnants updated.");
                break;
        }
    }
}
