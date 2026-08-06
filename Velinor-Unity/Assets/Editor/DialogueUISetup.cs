using UnityEditor;
using UnityEngine;
using TMPro;
using UnityEngine.UI;

public class DialogueUISetup : EditorWindow
{
    [MenuItem("Tools/Setup Dialogue UI in Current Scene")]
    public static void SetupDialogueUI()
    {
        // Find existing DialogueManager
        DialogueManager dialogueManager = FindObjectOfType<DialogueManager>();
        if (dialogueManager == null)
        {
            EditorUtility.DisplayDialog("Error", "DialogueManager not found in scene!", "OK");
            return;
        }

        Transform dialogueCanvas = dialogueManager.GetType().GetField("dialogueCanvas", 
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            ?.GetValue(dialogueManager) as Canvas;

        if (dialogueCanvas == null)
        {
            EditorUtility.DisplayDialog("Error", "DialogueCanvas not assigned to DialogueManager!", "OK");
            return;
        }

        // Load LiberationSans font asset
        TextMeshProUGUI sampleText = dialogueManager.GetType().GetField("bodyText", 
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            ?.GetValue(dialogueManager) as TextMeshProUGUI;

        TMP_FontAsset liberationFont = Resources.Load<TMP_FontAsset>("Fonts & Materials/LiberationSans SDF");
        if (liberationFont == null)
        {
            Debug.LogWarning("LiberationSans SDF font not found in Resources!");
        }

        // Find or create DialoguePanel
        Transform dialoguePanel = dialogueCanvas.transform.Find("DialoguePanel");
        if (dialoguePanel == null)
        {
            EditorUtility.DisplayDialog("Error", "DialoguePanel not found as child of DialogueCanvas!", "OK");
            return;
        }

        // Create NPC Name Text if missing
        Transform npcNameTransform = dialoguePanel.Find("NPCNameText");
        if (npcNameTransform == null)
        {
            npcNameTransform = CreateTextElement("NPCNameText", dialoguePanel, liberationFont);
            var rectTransform = npcNameTransform as RectTransform;
            rectTransform.anchorMin = new Vector2(0, 1);
            rectTransform.anchorMax = new Vector2(1, 1);
            rectTransform.anchoredPosition = new Vector2(0, -20);
            rectTransform.sizeDelta = new Vector2(-40, 40);
        }

        // Create Shared Beat Text if missing
        Transform sharedBeatTransform = dialoguePanel.Find("SharedBeatText");
        if (sharedBeatTransform == null)
        {
            sharedBeatTransform = CreateTextElement("SharedBeatText", dialoguePanel, liberationFont);
            var rectTransform = sharedBeatTransform as RectTransform;
            rectTransform.anchorMin = new Vector2(0, 0);
            rectTransform.anchorMax = new Vector2(1, 0);
            rectTransform.anchoredPosition = new Vector2(0, 20);
            rectTransform.sizeDelta = new Vector2(-40, 60);
        }

        // Create Choice Buttons Container if missing
        Transform choicesContainer = dialoguePanel.Find("ChoicesContainer");
        if (choicesContainer == null)
        {
            GameObject choicesObj = new GameObject("ChoicesContainer");
            choicesContainer = choicesObj.transform;
            choicesContainer.SetParent(dialoguePanel);
            var choicesRect = choicesObj.AddComponent<RectTransform>();
            choicesRect.anchorMin = new Vector2(0, 0);
            choicesRect.anchorMax = new Vector2(1, 0);
            choicesRect.anchoredPosition = new Vector2(0, 120);
            choicesRect.sizeDelta = new Vector2(-40, 200);

            var layoutGroup = choicesObj.AddComponent<VerticalLayoutGroup>();
            layoutGroup.childForceExpandHeight = false;
            layoutGroup.spacing = 10;
        }

        // Create 4 Tone Buttons
        string[] toneNames = { "Trust", "Observation", "NarrativePresence", "Empathy" };
        Button[] buttons = new Button[4];
        TextMeshProUGUI[] buttonLabels = new TextMeshProUGUI[4];

        for (int i = 0; i < 4; i++)
        {
            Transform buttonTransform = choicesContainer.Find(toneNames[i] + "Button");
            if (buttonTransform == null)
            {
                GameObject buttonObj = new GameObject(toneNames[i] + "Button");
                buttonTransform = buttonObj.transform;
                buttonTransform.SetParent(choicesContainer);

                var rectTransform = buttonObj.AddComponent<RectTransform>();
                rectTransform.sizeDelta = new Vector2(150, 40);

                var image = buttonObj.AddComponent<Image>();
                image.color = new Color(0.3f, 0.3f, 0.3f, 1);

                buttons[i] = buttonObj.AddComponent<Button>();
                buttons[i].targetGraphic = image;

                // Create button label
                GameObject labelObj = new GameObject("Label");
                labelObj.transform.SetParent(buttonTransform);
                var labelRect = labelObj.AddComponent<RectTransform>();
                labelRect.anchorMin = Vector2.zero;
                labelRect.anchorMax = Vector2.one;
                labelRect.offsetMin = Vector2.zero;
                labelRect.offsetMax = Vector2.zero;

                buttonLabels[i] = labelObj.AddComponent<TextMeshProUGUI>();
                buttonLabels[i].text = toneNames[i];
                buttonLabels[i].fontSize = 24;
                buttonLabels[i].alignment = TextAlignmentOptions.Center;
                buttonLabels[i].color = Color.white;
                if (liberationFont != null)
                {
                    buttonLabels[i].font = liberationFont;
                }
            }
            else
            {
                buttons[i] = buttonTransform.GetComponent<Button>();
                buttonLabels[i] = buttonTransform.Find("Label")?.GetComponent<TextMeshProUGUI>();
            }
        }

        // Assign all references to DialogueManager via reflection
        var dialogueManagerType = dialogueManager.GetType();

        dialogueManagerType.GetField("npcNameText", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            ?.SetValue(dialogueManager, npcNameTransform.GetComponent<TextMeshProUGUI>());

        dialogueManagerType.GetField("sharedBeatText", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            ?.SetValue(dialogueManager, sharedBeatTransform.GetComponent<TextMeshProUGUI>());

        dialogueManagerType.GetField("choiceButtonContainer", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            ?.SetValue(dialogueManager, choicesContainer);

        dialogueManagerType.GetField("btnT", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            ?.SetValue(dialogueManager, buttons[0]);

        dialogueManagerType.GetField("btnO", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            ?.SetValue(dialogueManager, buttons[1]);

        dialogueManagerType.GetField("btnN", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            ?.SetValue(dialogueManager, buttons[2]);

        dialogueManagerType.GetField("btnE", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            ?.SetValue(dialogueManager, buttons[3]);

        dialogueManagerType.GetField("txtT", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            ?.SetValue(dialogueManager, buttonLabels[0]);

        dialogueManagerType.GetField("txtO", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            ?.SetValue(dialogueManager, buttonLabels[1]);

        dialogueManagerType.GetField("txtN", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            ?.SetValue(dialogueManager, buttonLabels[2]);

        dialogueManagerType.GetField("txtE", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
            ?.SetValue(dialogueManager, buttonLabels[3]);

        // Mark scene as dirty
        EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());

        EditorUtility.DisplayDialog("Success", "Dialogue UI setup complete!\n\nAll missing UI elements created and wired up.", "OK");
        Debug.Log("✅ Dialogue UI Setup Complete!");
    }

    private static Transform CreateTextElement(string name, Transform parent, TMP_FontAsset font)
    {
        GameObject textObj = new GameObject(name);
        textObj.transform.SetParent(parent);

        var rectTransform = textObj.AddComponent<RectTransform>();
        var textMesh = textObj.AddComponent<TextMeshProUGUI>();

        textMesh.text = name;
        textMesh.fontSize = 20;
        textMesh.color = Color.white;
        textMesh.alignment = TextAlignmentOptions.Center;

        if (font != null)
        {
            textMesh.font = font;
        }

        return textObj.transform;
    }
}
