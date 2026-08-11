using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

/// <summary>
/// SetupInteractionUI - Creates and configures the interaction prompt UI in the scene.
/// </summary>
public class SetupInteractionUI
{
    [MenuItem("Velinor/Setup Interaction UI")]
    public static void SetupUI()
    {
        Debug.Log("=== Setting Up Interaction UI ===\n");

        // Try to find existing Canvas
        Canvas canvas = Object.FindAnyObjectByType<Canvas>();
        if (canvas == null)
        {
            Debug.LogError("❌ No Canvas found in scene. Please create a Canvas first.");
            return;
        }

        Debug.Log("✓ Found Canvas in scene");

        // Check if InteractionPromptUI already exists
        var existingPrompt = canvas.GetComponentInChildren<StarterAssets.InteractionPromptUI>();
        if (existingPrompt != null)
        {
            Debug.Log("✓ InteractionPromptUI already exists in scene");
            return;
        }

        // Create InteractionPrompt GameObject
        GameObject promptGO = new GameObject("InteractionPrompt");
        promptGO.transform.SetParent(canvas.transform);
        promptGO.transform.localPosition = Vector3.zero;

        var promptUI = promptGO.AddComponent<StarterAssets.InteractionPromptUI>();
        Debug.Log("✓ Created InteractionPromptUI component");

        // Create TextMeshPro text
        GameObject textGO = new GameObject("PromptText");
        textGO.transform.SetParent(promptGO.transform);
        textGO.transform.localPosition = Vector3.zero;

        TMPro.TextMeshProUGUI promptText = textGO.AddComponent<TMPro.TextMeshProUGUI>();
        promptText.text = "Press E to Interact";
        promptText.alignment = TMPro.TextAlignmentOptions.Center;
        promptText.fontSize = 36;
        promptText.enabled = false;

        RectTransform rectTransform = textGO.GetComponent<RectTransform>();
        rectTransform.sizeDelta = new Vector2(400, 100);
        rectTransform.anchoredPosition = new Vector2(0, -300);

        Debug.Log("✓ Created PromptText with TextMeshProUGUI");

        // Assign the text to the InteractionPromptUI
        var reflectionField = typeof(StarterAssets.InteractionPromptUI).GetField("promptText", 
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
        if (reflectionField != null)
        {
            reflectionField.SetValue(promptUI, promptText);
            Debug.Log("✓ Assigned text to InteractionPromptUI");
        }

        EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());

        Debug.Log("\n✅ Interaction UI Setup Complete!");
        Debug.Log("\n📋 How it works:");
        Debug.Log("  • When player looks at an IInteractable object");
        Debug.Log("  • 'Press E to Interact' prompt appears on screen");
        Debug.Log("  • Player presses E to trigger interaction");
    }
}
