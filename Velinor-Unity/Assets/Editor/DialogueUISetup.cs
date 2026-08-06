using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using TMPro;
using UnityEngine.UI;
using System.Linq;

public class DialogueUISetup : EditorWindow
{
    [MenuItem("Tools/Setup Dialogue UI in Current Scene")]
    public static void SetupDialogueUI()
    {
        TMP_FontAsset liberationFont = LoadLiberationSansFont();
        if (liberationFont == null)
        {
            EditorUtility.DisplayDialog("Error", "Could not load LiberationSans SDF font!", "OK");
            return;
        }

        // Find or create all UI elements
        DialogueManager dialogueManager = FindAnyObjectByType<DialogueManager>();
        if (dialogueManager == null)
        {
            EditorUtility.DisplayDialog("Error", "DialogueManager not found in scene!", "OK");
            return;
        }

        Canvas dialogueCanvas = dialogueManager.GetComponent<DialogueManager>() != null ? 
            FindObjectsByType<Canvas>()[0] : null;
        if (dialogueCanvas == null)
        {
            EditorUtility.DisplayDialog("Error", "DialogueCanvas not found!", "OK");
            return;
        }

        // Ensure all required UI elements exist
        CreateOrFindUIElement(dialogueCanvas, "SharedBeatText", liberationFont);
        
        Transform choiceContainer = FindObjectsByType<Transform>()
            .FirstOrDefault(t => t.gameObject.name == "ChoiceButtonContainer");
        if (choiceContainer != null)
        {
            CreateOrFindToneButton(choiceContainer, "TrustButton", "Trust", liberationFont);
            CreateOrFindToneButton(choiceContainer, "ObservationButton", "Observation", liberationFont);
            CreateOrFindToneButton(choiceContainer, "NarrativePresenceButton", "Narrative", liberationFont);
            CreateOrFindToneButton(choiceContainer, "EmpathyButton", "Empathy", liberationFont);
        }

        // Assign all fonts
        TextMeshProUGUI[] allTextElements = FindObjectsByType<TextMeshProUGUI>();
        int count = 0;
        foreach (TextMeshProUGUI textElement in allTextElements)
        {
            if (textElement.font == null)
            {
                textElement.font = liberationFont;
                EditorUtility.SetDirty(textElement);
                count++;
            }
        }

        // Wire all references to DialogueManager
        AssignAllReferences(dialogueManager, liberationFont);

        if (!EditorApplication.isPlaying)
        {
            EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
        }
        EditorUtility.DisplayDialog("Success", $"Dialogue UI Setup Complete!\n\nAssigned fonts to {count} text elements.", "OK");
        Debug.Log($"✅ Dialogue UI Setup Complete!");
    }

    private static void CreateOrFindUIElement(Canvas canvas, string name, TMP_FontAsset font)
    {
        Transform existing = canvas.transform.Find(name);
        if (existing != null) return;

        GameObject textGO = new GameObject(name);
        textGO.transform.SetParent(canvas.transform, false);
        RectTransform rt = textGO.AddComponent<RectTransform>();
        rt.anchoredPosition = Vector2.zero;
        rt.sizeDelta = new Vector2(400, 100);

        TextMeshProUGUI textComponent = textGO.AddComponent<TextMeshProUGUI>();
        textComponent.text = name;
        textComponent.font = font;
        textComponent.fontSize = 36;
        textComponent.alignment = TextAlignmentOptions.Center;

        EditorUtility.SetDirty(textGO);
        Debug.Log($"✓ Created {name}");
    }

    private static void CreateOrFindToneButton(Transform container, string buttonName, string label, TMP_FontAsset font)
    {
        Transform existing = container.Find(buttonName);
        if (existing != null) return;

        // Create button GameObject
        GameObject buttonGO = new GameObject(buttonName);
        buttonGO.transform.SetParent(container, false);
        RectTransform buttonRT = buttonGO.AddComponent<RectTransform>();
        buttonRT.anchoredPosition = Vector2.zero;
        buttonRT.sizeDelta = new Vector2(150, 60);

        Image buttonImage = buttonGO.AddComponent<Image>();
        buttonImage.color = new Color(0.8f, 0.8f, 0.8f, 1f);

        Button buttonComponent = buttonGO.AddComponent<Button>();
        ColorBlock colors = buttonComponent.colors;
        colors.normalColor = new Color(0.8f, 0.8f, 0.8f, 1f);
        colors.highlightedColor = new Color(1f, 1f, 1f, 1f);
        colors.pressedColor = new Color(0.6f, 0.6f, 0.6f, 1f);
        buttonComponent.colors = colors;

        // Create text child
        GameObject textGO = new GameObject(label + "Text");
        textGO.transform.SetParent(buttonGO.transform, false);
        RectTransform textRT = textGO.AddComponent<RectTransform>();
        textRT.anchoredPosition = Vector2.zero;
        textRT.offsetMin = Vector2.zero;
        textRT.offsetMax = Vector2.zero;

        TextMeshProUGUI textComponent = textGO.AddComponent<TextMeshProUGUI>();
        textComponent.text = label;
        textComponent.font = font;
        textComponent.fontSize = 24;
        textComponent.alignment = TextAlignmentOptions.Center;
        textComponent.color = Color.black;

        EditorUtility.SetDirty(buttonGO);
        EditorUtility.SetDirty(textGO);
        Debug.Log($"✓ Created {buttonName}");
    }

    private static TMP_FontAsset LoadLiberationSansFont()
    {
        string[] possiblePaths = new string[]
        {
            "Assets/TextMesh Pro/Resources/Fonts & Materials/LiberationSans SDF.asset",
            "Assets/TextMesh Pro/Fonts & Materials/LiberationSans SDF.asset",
            "Packages/com.unity.textmeshpro/Fonts & Materials/LiberationSans SDF.asset"
        };

        foreach (string path in possiblePaths)
        {
            TMP_FontAsset font = AssetDatabase.LoadAssetAtPath<TMP_FontAsset>(path);
            if (font != null)
            {
                Debug.Log("Loaded font from: " + path);
                return font;
            }
        }

        string[] guids = AssetDatabase.FindAssets("LiberationSans SDF t:TMP_FontAsset");
        if (guids.Length > 0)
        {
            string fontPath = AssetDatabase.GUIDToAssetPath(guids[0]);
            return AssetDatabase.LoadAssetAtPath<TMP_FontAsset>(fontPath);
        }

        return null;
    }

    private static void AssignAllReferences(DialogueManager dialogueManager, TMP_FontAsset font)
    {
        var dmType = dialogueManager.GetType();
        var flags = System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance;

        // Main text elements
        AssignField(dmType, dialogueManager, flags, "bodyText", "DialogueBodyText");
        AssignField(dmType, dialogueManager, flags, "npcNameText", "NPCNameText");
        AssignField(dmType, dialogueManager, flags, "sharedBeatText", "SharedBeatText");

        // Tone choice buttons
        AssignField(dmType, dialogueManager, flags, "btnT", "TrustButton");
        AssignField(dmType, dialogueManager, flags, "btnO", "ObservationButton");
        AssignField(dmType, dialogueManager, flags, "btnN", "NarrativePresenceButton");
        AssignField(dmType, dialogueManager, flags, "btnE", "EmpathyButton");

        // Tone choice labels (TextMeshProUGUI inside buttons)
        AssignTextField(dmType, dialogueManager, flags, "txtT", "TrustButtonTrustText");
        AssignTextField(dmType, dialogueManager, flags, "txtO", "ObservationButtonObservationText");
        AssignTextField(dmType, dialogueManager, flags, "txtN", "NarrativePresenceButtonNarrativeText");
        AssignTextField(dmType, dialogueManager, flags, "txtE", "EmpathyButtonEmpathyText");

        EditorUtility.SetDirty(dialogueManager);
        Debug.Log("✓ All DialogueManager references assigned");
    }

    private static void AssignField(System.Type type, DialogueManager dm, System.Reflection.BindingFlags flags, 
        string fieldName, string gameObjectName)
    {
        Button button = FindButtonByName(gameObjectName);
        if (button != null)
        {
            type.GetField(fieldName, flags)?.SetValue(dm, button);
            EditorUtility.SetDirty(button.gameObject);
        }
    }

    private static void AssignTextField(System.Type type, DialogueManager dm, System.Reflection.BindingFlags flags,
        string fieldName, string gameObjectName)
    {
        TextMeshProUGUI text = FindTextElementByName(gameObjectName);
        if (text != null)
        {
            type.GetField(fieldName, flags)?.SetValue(dm, text);
            EditorUtility.SetDirty(text.gameObject);
        }
    }

    private static TextMeshProUGUI FindTextElementByName(string name)
    {
        TextMeshProUGUI[] elements = FindObjectsByType<TextMeshProUGUI>();
        foreach (TextMeshProUGUI element in elements)
        {
            if (element.gameObject.name == name)
                return element;
        }
        return null;
    }

    private static Button FindButtonByName(string name)
    {
        Button[] buttons = FindObjectsByType<Button>();
        foreach (Button button in buttons)
        {
            if (button.gameObject.name == name)
                return button;
        }
        return null;
    }
}

