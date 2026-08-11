using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

/// <summary>
/// Editor utility to automatically wire up DialogueManager UI elements.
/// Finds and assigns Canvas, TextMeshPro fields, and Button components.
/// </summary>
public class DialogueManagerSetup : EditorWindow
{
    [MenuItem("Tools/Setup DialogueManager UI")]
    public static void SetupDialogueManagerUI()
    {
        // Find DialogueManager in the current scene
        DialogueManager dialogueManager = FindAnyObjectByType<DialogueManager>();
        
        if (dialogueManager == null)
        {
            EditorUtility.DisplayDialog("Error", 
                "DialogueManager not found in scene!\n\n" +
                "Make sure DialogueManager GameObject exists and has the DialogueManager component.", 
                "OK");
            return;
        }

        // Try to find DialogueCanvas - look for Canvas tagged as "DialogueCanvas"
        Canvas dialogueCanvas = FindAnyObjectByType<Canvas>();
        if (dialogueCanvas == null || dialogueCanvas.gameObject.name != "DialogueCanvas")
        {
            dialogueCanvas = FindCanvasByName("DialogueCanvas");
            if (dialogueCanvas == null)
            {
                EditorUtility.DisplayDialog("Warning", 
                    "Could not find DialogueCanvas in scene.\n\n" +
                    "Please create a Canvas GameObject named 'DialogueCanvas' with the following children:\n" +
                    "• DialogueBodyText (TextMeshProUGUI)\n" +
                    "• NPCLineText (TextMeshProUGUI)\n" +
                    "• SharedBeatText (TextMeshProUGUI)\n" +
                    "• ChoiceButton_T (Button with text child)\n" +
                    "• ChoiceButton_O (Button with text child)\n" +
                    "• ChoiceButton_N (Button with text child)\n" +
                    "• ChoiceButton_E (Button with text child)", 
                    "OK");
                return;
            }
        }

        // Get all components from the hierarchy
        bool success = true;
        int assignedCount = 0;

        // Assign dialogueCanvas using reflection
        var canvasField = typeof(DialogueManager).GetField("dialogueCanvas",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
        if (canvasField != null && dialogueCanvas != null)
        {
            canvasField.SetValue(dialogueManager, dialogueCanvas);
            assignedCount++;
            Debug.Log($"✓ Assigned dialogueCanvas to {dialogueCanvas.gameObject.name}");
        }

        // Find and assign TextMeshProUGUI fields
        TextMeshProUGUI bodyText = FindTextMeshProByName(dialogueCanvas, "DialogueBodyText");
        if (bodyText != null)
        {
            var bodyField = typeof(DialogueManager).GetField("bodyText",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            bodyField?.SetValue(dialogueManager, bodyText);
            assignedCount++;
            Debug.Log($"✓ Assigned bodyText");
        }
        else
        {
            Debug.LogWarning("⚠️  Could not find DialogueBodyText TextMeshProUGUI");
            success = false;
        }

        TextMeshProUGUI npcNameText = FindTextMeshProByName(dialogueCanvas, "NPCLineText");
        if (npcNameText != null)
        {
            var npcField = typeof(DialogueManager).GetField("npcNameText",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            npcField?.SetValue(dialogueManager, npcNameText);
            assignedCount++;
            Debug.Log($"✓ Assigned npcNameText");
        }
        else
        {
            Debug.LogWarning("⚠️  Could not find NPCLineText TextMeshProUGUI");
            success = false;
        }

        TextMeshProUGUI sharedBeatText = FindTextMeshProByName(dialogueCanvas, "SharedBeatText");
        if (sharedBeatText != null)
        {
            var sharedBeatField = typeof(DialogueManager).GetField("sharedBeatText",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            sharedBeatField?.SetValue(dialogueManager, sharedBeatText);
            assignedCount++;
            Debug.Log($"✓ Assigned sharedBeatText");
        }
        else
        {
            Debug.LogWarning("⚠️  Could not find SharedBeatText TextMeshProUGUI");
            success = false;
        }

        // Find and assign Choice Buttons (Trust, Observation, Narrative, Empathy)
        Button btnT = FindButtonByName(dialogueCanvas, "ChoiceButton_T");
        if (btnT != null)
        {
            var btnTField = typeof(DialogueManager).GetField("btnT",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            btnTField?.SetValue(dialogueManager, btnT);
            assignedCount++;
            Debug.Log($"✓ Assigned btnT (Trust)");
        }
        else
        {
            Debug.LogWarning("⚠️  Could not find ChoiceButton_T Button");
            success = false;
        }

        Button btnO = FindButtonByName(dialogueCanvas, "ChoiceButton_O");
        if (btnO != null)
        {
            var btnOField = typeof(DialogueManager).GetField("btnO",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            btnOField?.SetValue(dialogueManager, btnO);
            assignedCount++;
            Debug.Log($"✓ Assigned btnO (Observation)");
        }
        else
        {
            Debug.LogWarning("⚠️  Could not find ChoiceButton_O Button");
            success = false;
        }

        Button btnN = FindButtonByName(dialogueCanvas, "ChoiceButton_N");
        if (btnN != null)
        {
            var btnNField = typeof(DialogueManager).GetField("btnN",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            btnNField?.SetValue(dialogueManager, btnN);
            assignedCount++;
            Debug.Log($"✓ Assigned btnN (NarrativePresence)");
        }
        else
        {
            Debug.LogWarning("⚠️  Could not find ChoiceButton_N Button");
            success = false;
        }

        Button btnE = FindButtonByName(dialogueCanvas, "ChoiceButton_E");
        if (btnE != null)
        {
            var btnEField = typeof(DialogueManager).GetField("btnE",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            btnEField?.SetValue(dialogueManager, btnE);
            assignedCount++;
            Debug.Log($"✓ Assigned btnE (Empathy)");
        }
        else
        {
            Debug.LogWarning("⚠️  Could not find ChoiceButton_E Button");
            success = false;
        }

        // Find and assign Button Labels (text children of buttons)
        TextMeshProUGUI txtT = FindTextMeshProInChild(btnT, "Text");
        if (txtT != null)
        {
            var txtTField = typeof(DialogueManager).GetField("txtT",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            txtTField?.SetValue(dialogueManager, txtT);
            assignedCount++;
            Debug.Log($"✓ Assigned txtT (Trust label)");
        }
        else if (btnT != null)
        {
            Debug.LogWarning("⚠️  Could not find text child in ChoiceButton_T");
            success = false;
        }

        TextMeshProUGUI txtO = FindTextMeshProInChild(btnO, "Text");
        if (txtO != null)
        {
            var txtOField = typeof(DialogueManager).GetField("txtO",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            txtOField?.SetValue(dialogueManager, txtO);
            assignedCount++;
            Debug.Log($"✓ Assigned txtO (Observation label)");
        }
        else if (btnO != null)
        {
            Debug.LogWarning("⚠️  Could not find text child in ChoiceButton_O");
            success = false;
        }

        TextMeshProUGUI txtN = FindTextMeshProInChild(btnN, "Text");
        if (txtN != null)
        {
            var txtNField = typeof(DialogueManager).GetField("txtN",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            txtNField?.SetValue(dialogueManager, txtN);
            assignedCount++;
            Debug.Log($"✓ Assigned txtN (NarrativePresence label)");
        }
        else if (btnN != null)
        {
            Debug.LogWarning("⚠️  Could not find text child in ChoiceButton_N");
            success = false;
        }

        TextMeshProUGUI txtE = FindTextMeshProInChild(btnE, "Text");
        if (txtE != null)
        {
            var txtEField = typeof(DialogueManager).GetField("txtE",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            txtEField?.SetValue(dialogueManager, txtE);
            assignedCount++;
            Debug.Log($"✓ Assigned txtE (Empathy label)");
        }
        else if (btnE != null)
        {
            Debug.LogWarning("⚠️  Could not find text child in ChoiceButton_E");
            success = false;
        }

        // Mark the scene as dirty so changes are saved
        EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
        AssetDatabase.SaveAssets();

        // Show result
        if (success)
        {
            EditorUtility.DisplayDialog("Success",
                $"✅ DialogueManager setup complete!\n\n" +
                $"Assigned {assignedCount} UI elements.",
                "OK");
            Debug.Log($"✅ DialogueManager UI setup successful! ({assignedCount} elements assigned)");
        }
        else
        {
            EditorUtility.DisplayDialog("Partial Success",
                $"⚠️  DialogueManager setup partially complete.\n\n" +
                $"Assigned {assignedCount} elements. Check the console for warnings about missing elements.\n\n" +
                $"Make sure all required UI GameObjects exist in the hierarchy with the correct names.",
                "OK");
            Debug.LogWarning($"⚠️  DialogueManager setup partially complete ({assignedCount} elements assigned)");
        }
    }

    private static Canvas FindCanvasByName(string name)
    {
        Canvas[] allCanvases = FindObjectsByType<Canvas>();
        foreach (Canvas canvas in allCanvases)
        {
            if (canvas.gameObject.name == name)
                return canvas;
        }
        return null;
    }

    private static TextMeshProUGUI FindTextMeshProByName(Canvas root, string name)
    {
        foreach (TextMeshProUGUI text in root.GetComponentsInChildren<TextMeshProUGUI>())
        {
            if (text.gameObject.name == name)
                return text;
        }
        return null;
    }

    private static Button FindButtonByName(Canvas root, string name)
    {
        foreach (Button btn in root.GetComponentsInChildren<Button>())
        {
            if (btn.gameObject.name == name)
                return btn;
        }
        return null;
    }

    private static TextMeshProUGUI FindTextMeshProInChild(Button button, string childName)
    {
        if (button == null)
            return null;

        foreach (TextMeshProUGUI text in button.GetComponentsInChildren<TextMeshProUGUI>())
        {
            if (text.gameObject.name == childName || text.transform.parent == button.transform)
                return text;
        }

        // If not found by name, just get the first TextMeshProUGUI child
        TextMeshProUGUI[] textChildren = button.GetComponentsInChildren<TextMeshProUGUI>();
        return textChildren.Length > 0 ? textChildren[0] : null;
    }
}
