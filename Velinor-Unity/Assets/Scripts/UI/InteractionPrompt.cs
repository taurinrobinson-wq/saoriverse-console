using UnityEngine;
using TMPro;

/// <summary>
/// UI prompt that shows "Press E to Interact" when player is in interaction zone.
/// </summary>
public class InteractionPrompt : MonoBehaviour
{
    private TextMeshProUGUI _promptText;
    private CanvasGroup _canvasGroup;

    private void Start()
    {
        // Find or create the prompt text
        _promptText = GetComponentInChildren<TextMeshProUGUI>();
        _canvasGroup = GetComponent<CanvasGroup>();

        if (_promptText == null)
        {
            Debug.LogError("InteractionPrompt needs a TextMeshProUGUI child!");
        }

        if (_canvasGroup == null)
        {
            _canvasGroup = gameObject.AddComponent<CanvasGroup>();
        }

        Hide();
    }

    public void Show(string objectName)
    {
        if (_promptText != null)
        {
            _promptText.text = $"Press [E] to interact with {objectName}";
        }
        if (_canvasGroup != null)
        {
            _canvasGroup.alpha = 1f;
        }
    }

    public void Hide()
    {
        if (_canvasGroup != null)
        {
            _canvasGroup.alpha = 0f;
        }
    }
}
