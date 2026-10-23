using UnityEngine;
using UnityEditor;
using UnityEngine.UI;

/// <summary>
/// Editor menu for setting up Velinor screen sequences and projector interactions
/// Automatically creates all necessary GameObjects, components, and wiring
/// </summary>
public class VelinorScreenSetupMenu
{
    private const string MENU_ROOT = "Velinor/Screen Setup/";

    [MenuItem(MENU_ROOT + "Setup Screen Sequence System")]
    public static void SetupScreenSequence()
    {
        Debug.Log("[Velinor Setup] Starting Screen Sequence System setup...");

        // Find or create root container
        GameObject screenRoot = FindOrCreateGameObject("ScreenSequences", null);

        // Create ScreenInteractionTrigger
        GameObject triggerObj = FindOrCreateGameObject("ScreenInteractionTrigger", screenRoot.transform);
        
        // Add BoxCollider2D
        BoxCollider2D collider2D = triggerObj.GetComponent<BoxCollider2D>();
        if (collider2D == null)
        {
            collider2D = triggerObj.AddComponent<BoxCollider2D>();
            collider2D.isTrigger = true;
            collider2D.size = new Vector2(5f, 3f);
            Debug.Log("[Velinor Setup] Added BoxCollider2D (trigger) to ScreenInteractionTrigger");
        }

        // Add ScreenSequenceController
        ScreenSequenceController controller = triggerObj.GetComponent<ScreenSequenceController>();
        if (controller == null)
        {
            controller = triggerObj.AddComponent<ScreenSequenceController>();
            Debug.Log("[Velinor Setup] Added ScreenSequenceController script");
        }

        // Assign the collider to the controller
        if (controller != null)
        {
            SerializedObject controllerSO = new SerializedObject(controller);
            SerializedProperty colliderProp = controllerSO.FindProperty("screenAccessCollider");
            if (colliderProp != null)
            {
                colliderProp.objectReferenceValue = collider2D;
                controllerSO.ApplyModifiedProperties();
                Debug.Log("[Velinor Setup] Assigned BoxCollider2D to ScreenSequenceController.screenAccessCollider");
            }
        }

        // NOTE: Mind Log UI is already in UI_Canvas prefab (MindLogPrimaryContainer)
        // Controller will reference it via Inspector assignment
        Debug.Log("[Velinor Setup] Mind Log UI already exists in UI_Canvas prefab - assign MindLogPrimaryContainer to controller");

        // Create ScreenImagePanel with sample structure
        GameObject screenImagePanel = FindOrCreateGameObject("ScreenImagePanel", screenRoot.transform);
        Canvas imageCanvas = screenImagePanel.GetComponent<Canvas>();
        if (imageCanvas == null)
        {
            imageCanvas = screenImagePanel.AddComponent<Canvas>();
            imageCanvas.renderMode = RenderMode.ScreenSpaceOverlay;
            Debug.Log("[Velinor Setup] Added Canvas to ScreenImagePanel");
        }
        CanvasGroup imageCanvasGroup = screenImagePanel.GetComponent<CanvasGroup>();
        if (imageCanvasGroup == null)
        {
            imageCanvasGroup = screenImagePanel.AddComponent<CanvasGroup>();
            Debug.Log("[Velinor Setup] Added CanvasGroup to ScreenImagePanel");
        }
        screenImagePanel.SetActive(false);

        // Create BackgroundImage (RawImage)
        GameObject bgImage = FindOrCreateGameObject("BackgroundImage", screenImagePanel.transform);
        RawImage rawImage = bgImage.GetComponent<RawImage>();
        if (rawImage == null)
        {
            rawImage = bgImage.AddComponent<RawImage>();
            rawImage.color = new Color(1, 1, 1, 1);
            Debug.Log("[Velinor Setup] Added RawImage to BackgroundImage");
        }
        RectTransform bgRect = bgImage.GetComponent<RectTransform>();
        bgRect.anchorMin = Vector2.zero;
        bgRect.anchorMax = Vector2.one;
        bgRect.offsetMin = Vector2.zero;
        bgRect.offsetMax = Vector2.zero;

        // Create sample hotspot structure
        GameObject hotspotsFolder = FindOrCreateGameObject("Hotspots", screenImagePanel.transform);
        
        for (int i = 1; i <= 3; i++)
        {
            GameObject hotspot = FindOrCreateGameObject($"Hotspot_{i:00}", hotspotsFolder.transform);
            
            // Add Image component for visual
            Image hotspotImage = hotspot.GetComponent<Image>();
            if (hotspotImage == null)
            {
                hotspotImage = hotspot.AddComponent<Image>();
                hotspotImage.color = new Color(1, 1, 1, 0.3f);
            }

            // Add ScreenHotspot script
            ScreenHotspot hotspotScript = hotspot.GetComponent<ScreenHotspot>();
            if (hotspotScript == null)
            {
                hotspotScript = hotspot.AddComponent<ScreenHotspot>();
                Debug.Log($"[Velinor Setup] Added ScreenHotspot to Hotspot_{i:00}");
            }

            // Position hotspots in a row
            RectTransform hotspotRect = hotspot.GetComponent<RectTransform>();
            hotspotRect.anchoredPosition = new Vector2(-400 + (i * 200), 0);
            hotspotRect.sizeDelta = new Vector2(150, 150);

            // Create highlight graphic
            GameObject highlightObj = FindOrCreateGameObject("Highlight", hotspot.transform);
            Image highlightImage = highlightObj.GetComponent<Image>();
            if (highlightImage == null)
            {
                highlightImage = highlightObj.AddComponent<Image>();
                highlightImage.color = new Color(1, 1, 0.5f, 0.2f);
            }
            RectTransform highlightRect = highlightObj.GetComponent<RectTransform>();
            highlightRect.anchorMin = Vector2.zero;
            highlightRect.anchorMax = Vector2.one;
            highlightRect.offsetMin = Vector2.zero;
            highlightRect.offsetMax = Vector2.zero;
            highlightObj.SetActive(false);

            // Create animation panel (child that will animate)
            GameObject animPanel = FindOrCreateGameObject($"AnimPanel_{i:00}", screenImagePanel.transform);
            Image panelImage = animPanel.GetComponent<Image>();
            if (panelImage == null)
            {
                panelImage = animPanel.AddComponent<Image>();
                panelImage.color = new Color(0.8f, 0.8f, 1, 0.9f);
            }

            ScreenPanelAnimator animator = animPanel.GetComponent<ScreenPanelAnimator>();
            if (animator == null)
            {
                animator = animPanel.AddComponent<ScreenPanelAnimator>();
                Debug.Log($"[Velinor Setup] Added ScreenPanelAnimator to AnimPanel_{i:00}");
            }

            RectTransform panelRect = animPanel.GetComponent<RectTransform>();
            panelRect.anchoredPosition = new Vector2(-400 + (i * 200), -150);
            panelRect.sizeDelta = new Vector2(150, 150);
            animPanel.SetActive(false);
        }

        Debug.Log("[Velinor Setup] Screen Sequence System setup complete!");
        Debug.Log("[Velinor Setup] Next steps:");
        Debug.Log("  1. Assign CodexController reference to ScreenSequenceController");
        Debug.Log("  2. Assign ScreenImagePanel reference to ScreenSequenceController");
        Debug.Log("  3. Customize hotspot positions and animations");
        Debug.Log("  4. Add your screen image texture to BackgroundImage");
        Debug.Log("  NOTE: Mind Log UI uses existing UI_Canvas/MindLogPrimaryContainer - no separate setup needed");
    }

    [MenuItem(MENU_ROOT + "Setup Projector Interaction System")]
    public static void SetupProjectorInteraction()
    {
        Debug.Log("[Velinor Setup] Starting Projector Interaction System setup...");

        // Look for existing Collider_ProjectorBase
        GameObject projectorBase = GameObject.Find("Collider_ProjectorBase");
        if (projectorBase == null)
        {
            // Fallback: create new ProjectorInteractionTrigger
            GameObject projectorRoot = FindOrCreateGameObject("ProjectorInteraction", null);
            projectorBase = FindOrCreateGameObject("ProjectorInteractionTrigger", projectorRoot.transform);

            // Add BoxCollider2D if needed
            Collider2D collider2D = projectorBase.GetComponent<Collider2D>();
            if (collider2D == null)
            {
                collider2D = projectorBase.AddComponent<BoxCollider2D>();
                ((BoxCollider2D)collider2D).size = new Vector2(3f, 3f);
                collider2D.isTrigger = true;
                Debug.Log("[Velinor Setup] Added BoxCollider2D (trigger) to ProjectorInteractionTrigger");
            }
            Debug.Log("[Velinor Setup] Created new ProjectorInteractionTrigger (Collider_ProjectorBase not found in scene)");
        }
        else
        {
            Debug.Log("[Velinor Setup] Found existing Collider_ProjectorBase - using it for projector interaction");
            
            // Ensure it's a trigger
            Collider2D collider = projectorBase.GetComponent<Collider2D>();
            if (collider != null && !collider.isTrigger)
            {
                collider.isTrigger = true;
                Debug.Log("[Velinor Setup] Enabled 'Is Trigger' on Collider_ProjectorBase");
            }
        }

        // Add ProjectorInteractionController
        ProjectorInteractionController projectorController = projectorBase.GetComponent<ProjectorInteractionController>();
        if (projectorController == null)
        {
            projectorController = projectorBase.AddComponent<ProjectorInteractionController>();
            Debug.Log("[Velinor Setup] Added ProjectorInteractionController script to Collider_ProjectorBase");
        }

        Debug.Log("[Velinor Setup] Projector Interaction System setup complete!");
        Debug.Log("[Velinor Setup] Next steps:");
        Debug.Log("  1. Assign CodexController reference");
        Debug.Log("  2. Assign TriglyphMonsterProjector reference");
        Debug.Log("  3. Configure stage and Mind Log texts");
        Debug.Log("  4. Set up glyph collection system");
    }

    [MenuItem(MENU_ROOT + "Setup Both Systems")]
    public static void SetupBothSystems()
    {
        SetupScreenSequence();
        SetupProjectorInteraction();
        Debug.Log("[Velinor Setup] All systems configured!");
    }

    [MenuItem(MENU_ROOT + "Help")]
    public static void ShowHelp()
    {
        EditorUtility.DisplayDialog(
            "Velinor Screen Setup Help",
            "This menu creates all necessary GameObjects and components for:\n\n" +
            "• Screen Sequence System: Interactive comic-strip sequences with hotspots, animations, and Mind Logs\n" +
            "• Projector Interaction System: Multi-stage projector reveal with glyph collection\n\n" +
            "After setup:\n" +
            "1. Wire up references (CodexController, TriglyphMonsterProjector, etc.)\n" +
            "2. Configure stage-specific settings\n" +
            "3. Add your images and customize animations\n\n" +
            "See SCREEN_SEQUENCE_ARCHITECTURE.md for detailed documentation.",
            "OK"
        );
    }

    private static GameObject FindOrCreateGameObject(string name, Transform parent)
    {
        // Try to find existing
        Transform existing = parent != null 
            ? parent.Find(name) 
            : null;
        
        if (existing != null)
            return existing.gameObject;

        // Create new
        GameObject newObj = new GameObject(name);
        if (parent != null)
            newObj.transform.SetParent(parent, false);
        
        return newObj;
    }
}
