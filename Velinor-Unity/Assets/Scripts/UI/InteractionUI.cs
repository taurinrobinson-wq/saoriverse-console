using UnityEngine;
using TMPro;

public class InteractionUI : MonoBehaviour
{
    public static InteractionUI Instance { get; private set; }

    private TextMeshProUGUI promptText;
    private CanvasGroup canvasGroup;

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
        }
        else
        {
            Destroy(gameObject);
        }
    }

    void Start()
    {
        // Find or create the prompt text
        promptText = GetComponentInChildren<TextMeshProUGUI>();
        if (promptText == null)
        {
            // Create prompt text if it doesn't exist
            GameObject promptGO = new GameObject("PromptText");
            promptGO.transform.SetParent(transform);
            promptText = promptGO.AddComponent<TextMeshProUGUI>();
            
            RectTransform rect = promptGO.GetComponent<RectTransform>();
            rect.anchoredPosition = Vector2.zero;
            rect.sizeDelta = new Vector2(400, 100);
            
            promptText.text = "";
            promptText.fontSize = 36;
            promptText.alignment = TextAlignmentOptions.Center;
            promptText.color = Color.yellow;
        }

        canvasGroup = GetComponent<CanvasGroup>();
        if (canvasGroup == null)
        {
            canvasGroup = gameObject.AddComponent<CanvasGroup>();
        }

        HidePrompt();
    }

    public void ShowPrompt(string text)
    {
        promptText.text = text;
        canvasGroup.alpha = 1f;
    }

    public void HidePrompt()
    {
        canvasGroup.alpha = 0f;
    }
}
