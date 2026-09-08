using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using UnityEditor;
using UnityEditor.SceneManagement;
using Velinor.Core;

public class DiagnosticMissingScripts
{
    [MenuItem("Velinor/Diagnostics/Find Missing Script Components")]
    public static void FindMissingScripts()
    {
        Scene activeScene = EditorSceneManager.GetActiveScene();
        GameObject[] allObjects = activeScene.GetRootGameObjects();
        int missingCount = 0;

        Debug.Log($"[DIAGNOSTIC] Scanning {activeScene.name} for missing scripts...");

        foreach (GameObject root in allObjects)
        {
            ScanGameObject(root, ref missingCount);
        }

        if (missingCount == 0)
        {
            Debug.Log("[DIAGNOSTIC] ✅ No missing scripts found!");
        }
        else
        {
            Debug.LogError($"[DIAGNOSTIC] ⚠️ Found {missingCount} objects with missing scripts!");
        }
    }

    private static void ScanGameObject(GameObject obj, ref int missingCount)
    {
        MonoBehaviour[] components = obj.GetComponents<MonoBehaviour>();

        foreach (MonoBehaviour component in components)
        {
            if (component == null)
            {
                Debug.LogError($"[DIAGNOSTIC] MISSING SCRIPT on: {GetFullPath(obj)}", obj);
                missingCount++;
            }
            else if (component.GetType().Name == "Missing")
            {
                Debug.LogError($"[DIAGNOSTIC] CORRUPTED COMPONENT on: {GetFullPath(obj)}", obj);
                missingCount++;
            }
        }

        foreach (Transform child in obj.transform)
        {
            ScanGameObject(child.gameObject, ref missingCount);
        }
    }

    private static string GetFullPath(GameObject obj)
    {
        string path = obj.name;
        Transform current = obj.transform.parent;

        while (current != null)
        {
            path = current.name + "/" + path;
            current = current.parent;
        }

        return path;
    }

    [MenuItem("Velinor/Diagnostics/Check Canvas Status")]
    public static void CheckCanvasStatus()
    {
        Canvas[] allCanvas = Object.FindObjectsByType<Canvas>();

        Debug.Log($"[DIAGNOSTIC] Found {allCanvas.Length} Canvas components in scene");

        foreach (Canvas canvas in allCanvas)
        {
            Debug.Log($"[DIAGNOSTIC] Canvas '{canvas.gameObject.name}':" +
                $"\n  - GameObject Active: {canvas.gameObject.activeSelf}" +
                $"\n  - Component Enabled: {canvas.enabled}" +
                $"\n  - Render Mode: {canvas.renderMode}" +
                $"\n  - Parent: {(canvas.transform.parent != null ? canvas.transform.parent.name : "NONE (root)")}",
                canvas.gameObject);
        }
    }

    [MenuItem("Velinor/Diagnostics/Check CodexController References")]
    public static void CheckCodexController()
    {
        CodexController codex = Object.FindAnyObjectByType<CodexController>();

        if (codex == null)
        {
            Debug.LogError("[DIAGNOSTIC] CodexController not found in scene!");
            return;
        }

        Debug.Log($"[DIAGNOSTIC] CodexController found: {codex.gameObject.name}");

        // Use reflection to check private fields
        var cachedCanvasField = typeof(CodexController).GetField("_cachedCanvas",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);

        if (cachedCanvasField != null)
        {
            Canvas cachedCanvas = (Canvas)cachedCanvasField.GetValue(codex);
            if (cachedCanvas != null)
            {
                Debug.Log($"[DIAGNOSTIC] _cachedCanvas reference:" +
                    $"\n  - GameObject: {cachedCanvas.gameObject.name}" +
                    $"\n  - Active: {cachedCanvas.gameObject.activeSelf}" +
                    $"\n  - Enabled: {cachedCanvas.enabled}",
                    cachedCanvas.gameObject);
            }
            else
            {
                Debug.LogError("[DIAGNOSTIC] _cachedCanvas is NULL!");
            }
        }
    }

    [MenuItem("Velinor/Diagnostics/Deep Inspect Glyph Highlight")]
    public static void DeepInspectGlyphHighlight()
    {
        GlyphUI[] allGlyphs = Object.FindObjectsByType<GlyphUI>();

        // Skip template, find actual grid glyphs
        GlyphUI targetGlyph = null;
        foreach (GlyphUI glyph in allGlyphs)
        {
            if (!glyph.gameObject.name.Contains("Template"))
            {
                targetGlyph = glyph;
                break;
            }
        }

        if (targetGlyph == null)
        {
            Debug.LogError("[DIAGNOSTIC] No actual glyph instances found (only templates)!");
            return;
        }

        Debug.Log($"[DIAGNOSTIC] Inspecting: {targetGlyph.gameObject.name}");

        var glowHighlightField = typeof(GlyphUI).GetField("glowHighlight",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);

        GameObject glowHighlight = (GameObject)glowHighlightField.GetValue(targetGlyph);

        if (glowHighlight == null)
        {
            Debug.LogError($"[DIAGNOSTIC] glowHighlight is NULL on {targetGlyph.gameObject.name}!");
            return;
        }

        // Check Image component
        Image highlightImage = glowHighlight.GetComponent<Image>();
        Debug.Log($"[DIAGNOSTIC] Image Component:" +
            $"\n  - Exists: {highlightImage != null}" +
            $"\n  - Enabled: {highlightImage?.enabled}" +
            $"\n  - Color: {highlightImage?.color}" +
            $"\n  - Sprite: {highlightImage?.sprite?.name ?? "NULL"}" +
            $"\n  - RaycastTarget: {highlightImage?.raycastTarget}");

        // Check RectTransform
        RectTransform highlightRect = glowHighlight.GetComponent<RectTransform>();
        Debug.Log($"[DIAGNOSTIC] RectTransform:" +
            $"\n  - SizeDelta: {highlightRect.sizeDelta}" +
            $"\n  - AnchoredPosition: {highlightRect.anchoredPosition}" +
            $"\n  - LocalScale: {highlightRect.localScale}" +
            $"\n  - Rect.width: {highlightRect.rect.width}" +
            $"\n  - Rect.height: {highlightRect.rect.height}");

        // Check parent hierarchy
        Debug.Log($"[DIAGNOSTIC] Hierarchy:");
        Transform current = glowHighlight.transform;
        int depth = 0;
        while (current != null && depth < 5)
        {
            var canvasGroup = current.GetComponent<CanvasGroup>();
            var canvas = current.GetComponent<Canvas>();
            var image = current.GetComponent<Image>();

            string info = $"{new string(' ', depth * 2)}{current.gameObject.name}";
            if (!current.gameObject.activeSelf) info += " [INACTIVE]";
            if (canvasGroup != null) info += $" [CanvasGroup: alpha={canvasGroup.alpha}]";
            if (canvas != null) info += $" [Canvas: enabled={canvas.enabled}]";
            if (image != null) info += $" [Image: enabled={image.enabled}, color={image.color}]";

            Debug.Log($"[DIAGNOSTIC] {info}");
            current = current.parent;
            depth++;
        }
    }
}
