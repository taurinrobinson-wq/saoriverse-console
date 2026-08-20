using UnityEngine;
using UnityEngine.UI;
using UnityEditor;
using TMPro;
using Velinor.Core;
using System.IO;

namespace Velinor.Editor
{
    /// <summary>
    /// Editor script to auto-generate the GlyphTestingPanel prefab with all toggles and wiring.
    /// Run from menu: Velinor → Setup → Create Testing Panel Prefab
    /// </summary>
    public class GlyphTestingPanelSetup
    {
        private static readonly string PrefabPath = "Assets/Resources/Prefabs/GlyphTestingPanel.prefab";
        private static readonly string PrefabsFolder = "Assets/Resources/Prefabs";

        [MenuItem("Velinor/Setup/Create Testing Panel Prefab")]
        public static void CreateTestingPanelPrefab()
        {
            // Ensure folder exists
            if (!AssetDatabase.IsValidFolder(PrefabsFolder))
            {
                AssetDatabase.CreateFolder("Assets/Resources", "Prefabs");
            }

            // Create root panel
            GameObject panelGO = new GameObject("GlyphTestingPanel");
            RectTransform panelRect = panelGO.AddComponent<RectTransform>();
            Image panelImage = panelGO.AddComponent<Image>();
            VerticalLayoutGroup layoutGroup = panelGO.AddComponent<VerticalLayoutGroup>();

            // Configure panel
            panelRect.anchorMin = new Vector2(0, 0);
            panelRect.anchorMax = new Vector2(0, 0);
            panelRect.offsetMin = Vector2.zero;
            panelRect.offsetMax = new Vector2(220, 350);
            panelImage.color = new Color(0, 0, 0, 0.8f);

            layoutGroup.padding = new RectOffset(10, 10, 10, 10);
            layoutGroup.spacing = 8;
            layoutGroup.childForceExpandHeight = false;
            layoutGroup.childForceExpandWidth = false;

            // Add title text
            GameObject titleGO = new GameObject("Title");
            titleGO.transform.SetParent(panelGO.transform);
            TextMeshProUGUI titleText = titleGO.AddComponent<TextMeshProUGUI>();
            RectTransform titleRect = titleGO.GetComponent<RectTransform>();
            titleText.text = "Glyph Testing";
            titleText.fontSize = 30;
            titleText.alignment = TextAlignmentOptions.TopLeft;
            titleRect.sizeDelta = new Vector2(200, 40);

            // Create toggles for each glyph
            CreateGlyphToggle(panelGO.transform, "Sorrow", 0);
            CreateGlyphToggle(panelGO.transform, "Remembrance", 1);
            CreateGlyphToggle(panelGO.transform, "Legacy", 2);

            // Add GlyphTestingController script
            GlyphTestingController controller = panelGO.AddComponent<GlyphTestingController>();

            // Try to auto-wire references
            AutoWireReferences(panelGO, controller);

            // Save as prefab
            if (PrefabUtility.SaveAsPrefabAsset(panelGO, PrefabPath))
            {
                Debug.Log($"✓ Testing Panel Prefab created: {PrefabPath}");
                EditorUtility.DisplayDialog("Success",
                    $"GlyphTestingPanel prefab created!\n\nLocation: {PrefabPath}\n\n" +
                    "You can now drag it into your scene.\n" +
                    "Verify references in Inspector if auto-wiring didn't complete.",
                    "OK");
            }
            else
            {
                Debug.LogError($"✗ Failed to create prefab: {PrefabPath}");
            }

            // Clean up temporary GameObject
            Object.DestroyImmediate(panelGO);
        }

        private static void CreateGlyphToggle(Transform parent, string glyphName, int index)
        {
            // Create toggle container
            GameObject toggleContainer = new GameObject($"{glyphName}ToggleContainer");
            toggleContainer.transform.SetParent(parent);
            RectTransform containerRect = toggleContainer.AddComponent<RectTransform>();
            containerRect.sizeDelta = new Vector2(200, 30);

            HorizontalLayoutGroup horizontalLayout = toggleContainer.AddComponent<HorizontalLayoutGroup>();
            horizontalLayout.spacing = 5;
            horizontalLayout.childForceExpandHeight = true;
            horizontalLayout.childForceExpandWidth = false;

            // Create toggle
            GameObject toggleGO = new GameObject($"{glyphName}Toggle");
            toggleGO.transform.SetParent(toggleContainer.transform);
            RectTransform toggleRect = toggleGO.AddComponent<RectTransform>();
            Image toggleImage = toggleGO.AddComponent<Image>();
            Toggle toggle = toggleGO.AddComponent<Toggle>();

            toggleRect.sizeDelta = new Vector2(30, 30);
            toggleImage.color = new Color(0.5f, 0.5f, 0.5f, 1);

            // Create toggle background
            GameObject bgGO = new GameObject("Background");
            bgGO.transform.SetParent(toggleGO.transform);
            RectTransform bgRect = bgGO.AddComponent<RectTransform>();
            Image bgImage = bgGO.AddComponent<Image>();
            bgRect.anchorMin = Vector2.zero;
            bgRect.anchorMax = Vector2.one;
            bgRect.offsetMin = Vector2.zero;
            bgRect.offsetMax = Vector2.zero;
            bgImage.color = new Color(0.3f, 0.3f, 0.3f, 1);

            // Create checkmark
            GameObject checkmarkGO = new GameObject("Checkmark");
            checkmarkGO.transform.SetParent(toggleGO.transform);
            RectTransform checkmarkRect = checkmarkGO.GetComponent<RectTransform>();
            if (checkmarkRect == null) checkmarkRect = checkmarkGO.AddComponent<RectTransform>();
            Image checkmarkImage = checkmarkGO.AddComponent<Image>();
            checkmarkRect.anchorMin = Vector2.zero;
            checkmarkRect.anchorMax = Vector2.one;
            checkmarkRect.offsetMin = Vector2.zero;
            checkmarkRect.offsetMax = Vector2.zero;
            checkmarkImage.color = new Color(0.2f, 0.8f, 0.2f, 1);

            // Configure toggle
            toggle.targetGraphic = toggleImage;
            toggle.isOn = false;

            // Create label
            GameObject labelGO = new GameObject("Label");
            labelGO.transform.SetParent(toggleContainer.transform);
            TextMeshProUGUI labelText = labelGO.AddComponent<TextMeshProUGUI>();
            RectTransform labelRect = labelGO.GetComponent<RectTransform>();
            labelText.text = glyphName;
            labelText.fontSize = 24;
            labelText.alignment = TextAlignmentOptions.MiddleLeft;
            labelRect.sizeDelta = new Vector2(150, 30);

            // Rename for clarity
            toggleGO.name = $"{glyphName}Toggle";
        }

        private static void AutoWireReferences(GameObject panelGO, GlyphTestingController controller)
        {
            // Find toggles in children
            Transform sorrowToggle = panelGO.transform.Find("SorrowToggleContainer/SorrowToggle");
            Transform rememToggle = panelGO.transform.Find("RemembranceToggleContainer/RemembranceToggle");
            Transform legacyToggle = panelGO.transform.Find("LegacyToggleContainer/LegacyToggle");

            if (sorrowToggle != null)
                controller.sorrowToggle = sorrowToggle.GetComponent<Toggle>();
            if (rememToggle != null)
                controller.remembranceToggle = rememToggle.GetComponent<Toggle>();
            if (legacyToggle != null)
                controller.legacyToggle = legacyToggle.GetComponent<Toggle>();

            // Load glyph data assets
            GlyphData sorrowData = AssetDatabase.LoadAssetAtPath<GlyphData>("Assets/Resources/Glyphs/GlyphOfSorrow.asset");
            GlyphData rememData = AssetDatabase.LoadAssetAtPath<GlyphData>("Assets/Resources/Glyphs/GlyphOfRemembrance.asset");
            GlyphData legacyData = AssetDatabase.LoadAssetAtPath<GlyphData>("Assets/Resources/Glyphs/GlyphOfLegacy.asset");

            controller.sorrowData = sorrowData;
            controller.remembranceData = rememData;
            controller.legacyData = legacyData;

            // Note: CodexController reference will need to be wired in-scene via inspector or FindAnyObjectByType
            Debug.Log("Auto-wired references for GlyphTestingPanel. Verify in Inspector.");
        }

        [MenuItem("Velinor/Setup/Delete Testing Panel Prefab")]
        public static void DeleteTestingPanelPrefab()
        {
            if (EditorUtility.DisplayDialog("Confirm Deletion",
                "Delete GlyphTestingPanel prefab?",
                "Delete", "Cancel"))
            {
                AssetDatabase.DeleteAsset(PrefabPath);
                AssetDatabase.Refresh();
                Debug.Log("Testing panel prefab deleted.");
            }
        }
    }
}
