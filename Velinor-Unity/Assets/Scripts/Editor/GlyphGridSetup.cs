using UnityEngine;
using UnityEditor;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;
using Velinor.Core;

public class GlyphGridSetup : MonoBehaviour
{
    [MenuItem("Tools/Setup Glyph Grid Pagination")]
    public static void SetupGlyphGrid()
    {
        // Find GlyphGrid in the scene
        GameObject glyphGridObj = GameObject.Find("GlyphGrid");
        if (glyphGridObj == null)
        {
            EditorUtility.DisplayDialog("Error", "GlyphGrid not found in scene!", "OK");
            return;
        }

        RectTransform glyphGridRect = glyphGridObj.GetComponent<RectTransform>();
        if (glyphGridRect == null)
        {
            EditorUtility.DisplayDialog("Error", "GlyphGrid doesn't have a RectTransform!", "OK");
            return;
        }

        Debug.Log("[Glyph Setup] Starting pagination setup...");

        // Create or get Page1 and Page2
        Transform page1Transform = glyphGridObj.transform.Find("Page1");
        Transform page2Transform = glyphGridObj.transform.Find("Page2");

        if (page1Transform == null)
        {
            GameObject page1 = new GameObject("Page1");
            page1.transform.SetParent(glyphGridObj.transform, false);
            page1Transform = page1.transform;
            RectTransform page1Rect = page1.AddComponent<RectTransform>();
            page1Rect.anchorMin = Vector2.zero;
            page1Rect.anchorMax = Vector2.one;
            page1Rect.offsetMin = Vector2.zero;
            page1Rect.offsetMax = Vector2.zero;
            Debug.Log("[Glyph Setup] Created Page1");
        }

        if (page2Transform == null)
        {
            GameObject page2 = new GameObject("Page2");
            page2.transform.SetParent(glyphGridObj.transform, false);
            page2Transform = page2.transform;
            RectTransform page2Rect = page2.AddComponent<RectTransform>();
            page2Rect.anchorMin = Vector2.zero;
            page2Rect.anchorMax = Vector2.one;
            page2Rect.offsetMin = Vector2.zero;
            page2Rect.offsetMax = Vector2.zero;
            Debug.Log("[Glyph Setup] Created Page2");
        }

        // Create 9 slots in Page1
        CreateSlotsForPage(page1Transform, 0, 9);

        // Create 9 slots in Page2
        CreateSlotsForPage(page2Transform, 9, 9);

        Debug.Log("[Glyph Setup] Created all slots with GlyphSlot components");

        // Find CodexController and populate slot references
        CodexController codexController = FindAnyObjectByType<CodexController>();
        if (codexController != null)
        {
            PopulateCodexControllerSlots(codexController, page1Transform, page2Transform);
            Debug.Log("[Glyph Setup] Populated CodexController slot references");
        }
        else
        {
            Debug.LogWarning("[Glyph Setup] CodexController not found. Please manually assign slot lists.");
        }

        EditorUtility.DisplayDialog("Success", "Glyph Grid pagination setup complete!\n\n" +
            "- Page1 and Page2 created\n" +
            "- 18 slots created (9 per page)\n" +
            "- GlyphSlot components added\n" +
            "- CodexController slot lists populated (if found)",
            "OK");

        Debug.Log("[Glyph Setup] ✅ Glyph Grid setup complete!");
    }

    private static void CreateSlotsForPage(Transform pageParent, int startIndex, int slotCount)
    {
        // Grid layout: 3x3
        // Each slot is approximately 30% width, 30% height within the page
        float slotWidth = 0.28f;  // ~80 pixels in a typical 300px grid
        float slotHeight = 0.28f;
        float spacing = 0.02f;

        int[] gridPositions = new int[] { 0, 1, 2 }; // 3x3 grid

        for (int i = 0; i < slotCount; i++)
        {
            int row = i / 3;
            int col = i % 3;

            // Calculate anchor positions for 3x3 grid
            float xStart = 0.05f + (col * (slotWidth + spacing));
            float yStart = 0.95f - (row * (slotHeight + spacing)) - slotHeight;

            // Check if slot already exists
            Transform existingSlot = pageParent.Find($"Slot_{startIndex + i}");
            if (existingSlot != null)
            {
                Debug.Log($"[Glyph Setup] Slot_{startIndex + i} already exists, skipping creation");
                continue;
            }

            // Create slot GameObject
            GameObject slotObj = new GameObject($"Slot_{startIndex + i}");
            slotObj.layer = LayerMask.NameToLayer("UI");
            slotObj.transform.SetParent(pageParent, false);

            // Add RectTransform
            RectTransform slotRect = slotObj.AddComponent<RectTransform>();
            slotRect.anchorMin = new Vector2(xStart, yStart);
            slotRect.anchorMax = new Vector2(xStart + slotWidth, yStart + slotHeight);
            slotRect.offsetMin = Vector2.zero;
            slotRect.offsetMax = Vector2.zero;

            // Add Image component (for visual representation)
            Image slotImage = slotObj.AddComponent<Image>();
            slotImage.color = new Color(0.2f, 0.2f, 0.3f, 0.7f); // Dark slot color

            // Add Button component (for interactivity)
            Button slotButton = slotObj.AddComponent<Button>();
            slotButton.targetGraphic = slotImage;

            // Add GlyphSlot script component
            GlyphSlot glyphSlot = slotObj.AddComponent<GlyphSlot>();

            Debug.Log($"[Glyph Setup] Created Slot_{startIndex + i}");
        }
    }

    private static void PopulateCodexControllerSlots(CodexController codexController, Transform page1, Transform page2)
    {
        // Use reflection to set the private fields
        System.Reflection.FieldInfo slotsPage1Field = typeof(CodexController).GetField("slotsPage1",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
        System.Reflection.FieldInfo slotsPage2Field = typeof(CodexController).GetField("slotsPage2",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);

        if (slotsPage1Field == null || slotsPage2Field == null)
        {
            Debug.LogWarning("[Glyph Setup] Could not find slotsPage1/slotsPage2 fields via reflection");
            return;
        }

        // Get existing lists or create new ones
        List<GlyphSlot> slotsPage1List = (List<GlyphSlot>)slotsPage1Field.GetValue(codexController);
        List<GlyphSlot> slotsPage2List = (List<GlyphSlot>)slotsPage2Field.GetValue(codexController);

        if (slotsPage1List == null) slotsPage1List = new List<GlyphSlot>();
        if (slotsPage2List == null) slotsPage2List = new List<GlyphSlot>();

        // Clear existing entries
        slotsPage1List.Clear();
        slotsPage2List.Clear();

        // Add Page1 slots (0-8)
        for (int i = 0; i < 9; i++)
        {
            Transform slotTransform = page1.Find($"Slot_{i}");
            if (slotTransform != null)
            {
                GlyphSlot glyphSlot = slotTransform.GetComponent<GlyphSlot>();
                if (glyphSlot != null)
                {
                    slotsPage1List.Add(glyphSlot);
                }
            }
        }

        // Add Page2 slots (9-17)
        for (int i = 9; i < 18; i++)
        {
            Transform slotTransform = page2.Find($"Slot_{i}");
            if (slotTransform != null)
            {
                GlyphSlot glyphSlot = slotTransform.GetComponent<GlyphSlot>();
                if (glyphSlot != null)
                {
                    slotsPage2List.Add(glyphSlot);
                }
            }
        }

        // Set the lists back
        slotsPage1Field.SetValue(codexController, slotsPage1List);
        slotsPage2Field.SetValue(codexController, slotsPage2List);

        Debug.Log($"[Glyph Setup] Assigned {slotsPage1List.Count} slots to Page1");
        Debug.Log($"[Glyph Setup] Assigned {slotsPage2List.Count} slots to Page2");
    }
}
