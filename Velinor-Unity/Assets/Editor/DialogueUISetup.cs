using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using TMPro;
using UnityEngine.UI;

public class DialogueUISetup : EditorWindow
{
    [MenuItem("Tools/Setup Dialogue UI in Current Scene")]
    public static void SetupDialogueUI()
    {
        // Find all TextMeshProUGUI elements and assign font
        TMP_FontAsset liberationFont = LoadLiberationSansFont();
        if (liberationFont == null)
        {
            EditorUtility.DisplayDialog("Error", "Could not load LiberationSans SDF font!\n\nSearching for it in project...", "OK");
            // Try to find it manually
            string[] fontGuids = AssetDatabase.FindAssets("LiberationSans SDF t:TMP_FontAsset");
            if (fontGuids.Length > 0)
            {
                string fontPath = AssetDatabase.GUIDToAssetPath(fontGuids[0]);
                liberationFont = AssetDatabase.LoadAssetAtPath<TMP_FontAsset>(fontPath);
                Debug.Log("Found font at: " + fontPath);
            }
            else
            {
                EditorUtility.DisplayDialog("Error", "LiberationSans SDF font not found in project!", "OK");
                return;
            }
        }

        // Find all TextMeshPro UI elements and assign font
        TextMeshProUGUI[] allTextElements = FindObjectsByType<TextMeshProUGUI>();
        int count = 0;
        foreach (TextMeshProUGUI textElement in allTextElements)
        {
            if (textElement.font == null)
            {
                textElement.font = liberationFont;
                EditorUtility.SetDirty(textElement);  // Serialize the change
                count++;
                Debug.Log($"✓ Assigned font to {textElement.gameObject.name}");
            }
        }

        // Find DialogueManager and assign UI references if they're missing
        DialogueManager dialogueManager = FindAnyObjectByType<DialogueManager>();
        if (dialogueManager != null)
        {
            AssignDialogueManagerReferences(dialogueManager, liberationFont);
        }

        // Mark scene as dirty only in edit mode
        if (!EditorApplication.isPlaying)
        {
            EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
        }
        EditorUtility.DisplayDialog("Success", $"Dialogue UI Setup Complete!\n\nAssigned fonts to {count} text elements.", "OK");
        Debug.Log($"✅ Dialogue UI Setup Complete! Assigned fonts to {count} elements.");
    }

    private static TMP_FontAsset LoadLiberationSansFont()
    {
        // Try multiple possible paths
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

        // Last resort: search by name
        string[] guids = AssetDatabase.FindAssets("LiberationSans SDF t:TMP_FontAsset");
        if (guids.Length > 0)
        {
            string fontPath = AssetDatabase.GUIDToAssetPath(guids[0]);
            return AssetDatabase.LoadAssetAtPath<TMP_FontAsset>(fontPath);
        }

        return null;
    }

    private static void AssignDialogueManagerReferences(DialogueManager dialogueManager, TMP_FontAsset font)
    {
        var dialogueManagerType = dialogueManager.GetType();
        var flags = System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance;
        bool anyChanges = false;

        // Try to find and assign existing UI elements
        TextMeshProUGUI bodyText = FindTextElementByName("DialogueBodyText");
        if (bodyText != null)
        {
            dialogueManagerType.GetField("bodyText", flags)?.SetValue(dialogueManager, bodyText);
            if (bodyText.font == null) bodyText.font = font;
            EditorUtility.SetDirty(bodyText);
            anyChanges = true;
        }

        TextMeshProUGUI npcNameText = FindTextElementByName("NPCNameText");
        if (npcNameText != null)
        {
            dialogueManagerType.GetField("npcNameText", flags)?.SetValue(dialogueManager, npcNameText);
            if (npcNameText.font == null) npcNameText.font = font;
            EditorUtility.SetDirty(npcNameText);
            anyChanges = true;
        }

        TextMeshProUGUI npcLineText = FindTextElementByName("NPCLineText");
        if (npcLineText != null)
        {
            dialogueManagerType.GetField("npcNameText", flags)?.SetValue(dialogueManager, npcLineText);
            if (npcLineText.font == null) npcLineText.font = font;
            EditorUtility.SetDirty(npcLineText);
            anyChanges = true;
        }

        TextMeshProUGUI sharedBeatText = FindTextElementByName("SharedBeatText");
        if (sharedBeatText != null)
        {
            dialogueManagerType.GetField("sharedBeatText", flags)?.SetValue(dialogueManager, sharedBeatText);
            if (sharedBeatText.font == null) sharedBeatText.font = font;
            EditorUtility.SetDirty(sharedBeatText);
            anyChanges = true;
        }

        // Find choice buttons
        Button trustBtn = FindButtonByName("TrustButton");
        if (trustBtn != null) dialogueManagerType.GetField("btnT", flags)?.SetValue(dialogueManager, trustBtn);

        Button obsBtn = FindButtonByName("ObservationButton");
        if (obsBtn != null) dialogueManagerType.GetField("btnO", flags)?.SetValue(dialogueManager, obsBtn);

        Button narrativeBtn = FindButtonByName("NarrativePresenceButton");
        if (narrativeBtn != null) dialogueManagerType.GetField("btnN", flags)?.SetValue(dialogueManager, narrativeBtn);

        Button empathyBtn = FindButtonByName("EmpathyButton");
        if (empathyBtn != null) dialogueManagerType.GetField("btnE", flags)?.SetValue(dialogueManager, empathyBtn);

        // Serialize DialogueManager changes
        EditorUtility.SetDirty(dialogueManager);

        Debug.Log("✓ DialogueManager references assigned");
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

