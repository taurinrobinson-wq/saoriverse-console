using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using TMPro;
using UnityEngine.UI;

public class SetupVelinorNarrativeScene
{
    [MenuItem("Velinor/Create Narrative Test Scene")]
    public static void CreateNarrativeTestScene()
    {
        // Create new scene
        var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects);
        scene.name = "VelinorNarrativeTest";

        // Get the main camera from default setup
        Camera mainCamera = Camera.main;
        if (mainCamera != null)
        {
            mainCamera.transform.position = new Vector3(0, 2, -8);
            mainCamera.transform.rotation = Quaternion.identity;
        }

        // ===== STEP 0: Create Ground =====
        GameObject groundObj = new GameObject("Ground");
        GameObject groundMesh = GameObject.CreatePrimitive(PrimitiveType.Plane);
        groundMesh.name = "GroundMesh";
        groundMesh.transform.SetParent(groundObj.transform);
        groundMesh.transform.localPosition = Vector3.zero;
        groundMesh.transform.localScale = new Vector3(20, 1, 20);

        // Remove physics collider (we'll use the plane collider that's already there)
        Collider groundCollider = groundMesh.GetComponent<Collider>();
        if (groundCollider != null)
            groundCollider.isTrigger = false; // Keep it solid for player walking

        // Color the ground
        Renderer groundRenderer = groundMesh.GetComponent<Renderer>();
        Material groundMat = new Material(Shader.Find("Standard"));
        groundMat.color = new Color(0.3f, 0.3f, 0.3f, 1f);
        groundRenderer.material = groundMat;

        Debug.Log("✅ Created Ground");

        // ===== STEP 1: Create StatManager =====
        GameObject statManagerObj = new GameObject("StatManager");
        statManagerObj.AddComponent<StatManager>();
        Debug.Log("✅ Created StatManager singleton");

        // ===== STEP 2: Create DialogueManager =====
        GameObject dialogueManagerObj = new GameObject("DialogueManager");
        DialogueManager dialogueManager = dialogueManagerObj.AddComponent<DialogueManager>();
        Debug.Log("✅ Created DialogueManager singleton");

        // ===== STEP 3: Create DialogueCanvas =====
        GameObject canvasObj = new GameObject("DialogueCanvas");
        Canvas canvas = canvasObj.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        
        RectTransform canvasRect = canvasObj.GetComponent<RectTransform>();
        canvasRect.anchorMin = Vector2.zero;
        canvasRect.anchorMax = Vector2.one;
        canvasRect.offsetMin = Vector2.zero;
        canvasRect.offsetMax = Vector2.zero;

        canvasObj.AddComponent<GraphicRaycaster>();
        canvasObj.AddComponent<CanvasGroup>();

        // Add Canvas Scaler
        CanvasScaler scaler = canvasObj.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920, 1080);

        Debug.Log("✅ Created DialogueCanvas");

        // ===== STEP 4: Create DialoguePanel (background - bottom 30% of screen) =====
        GameObject panelObj = new GameObject("DialoguePanel");
        panelObj.transform.SetParent(canvasObj.transform, false);
        Image panelImage = panelObj.AddComponent<Image>();
        panelImage.color = new Color(0, 0, 0, 0.8f); // Semi-transparent black

        RectTransform panelRect = panelObj.GetComponent<RectTransform>();
        panelRect.anchorMin = new Vector2(0, 0);      // Bottom-left
        panelRect.anchorMax = new Vector2(1, 0.3f);   // Full width, 30% height
        panelRect.offsetMin = Vector2.zero;
        panelRect.offsetMax = Vector2.zero;

        Debug.Log("✅ Created DialoguePanel");

        // ===== STEP 5: Create NPCNameText =====
        GameObject nameTextObj = new GameObject("NPCNameText");
        nameTextObj.transform.SetParent(panelObj.transform, false);
        TextMeshProUGUI nameText = nameTextObj.AddComponent<TextMeshProUGUI>();
        nameText.text = "[NPC Name]";
        nameText.fontSize = 56;
        nameText.alignment = TextAlignmentOptions.TopLeft;
        nameText.color = Color.white;

        RectTransform nameRect = nameTextObj.GetComponent<RectTransform>();
        nameRect.anchorMin = new Vector2(0, 1);
        nameRect.anchorMax = new Vector2(0, 1);
        nameRect.pivot = new Vector2(0, 1);
        nameRect.anchoredPosition = new Vector2(40, -40);
        nameRect.sizeDelta = new Vector2(400, 80);

        Debug.Log("✅ Created NPCNameText");

        // ===== STEP 6: Create DialogueBody Text =====
        GameObject bodyTextObj = new GameObject("DialogueBodyText");
        bodyTextObj.transform.SetParent(panelObj.transform, false);
        TextMeshProUGUI bodyText = bodyTextObj.AddComponent<TextMeshProUGUI>();
        bodyText.text = "[Dialogue will appear here]";
        bodyText.fontSize = 32;
        bodyText.alignment = TextAlignmentOptions.TopLeft;
        bodyText.color = Color.white;
        bodyText.wordWrappingRatios = 0.3f; // Wrap words naturally

        RectTransform bodyRect = bodyTextObj.GetComponent<RectTransform>();
        bodyRect.anchorMin = new Vector2(0, 1);
        bodyRect.anchorMax = new Vector2(1, 1);
        bodyRect.pivot = new Vector2(0, 1);
        bodyRect.anchoredPosition = new Vector2(40, -140);
        bodyRect.sizeDelta = new Vector2(-80, 400);

        Debug.Log("✅ Created DialogueBodyText");

        // ===== STEP 7: Create ChoiceButtonContainer =====
        GameObject containerObj = new GameObject("ChoiceButtonContainer");
        containerObj.transform.SetParent(panelObj.transform, false);

        VerticalLayoutGroup layoutGroup = containerObj.AddComponent<VerticalLayoutGroup>();
        layoutGroup.spacing = 10;
        layoutGroup.childForceExpandHeight = false;
        layoutGroup.childForceExpandWidth = true;

        RectTransform containerRect = containerObj.GetComponent<RectTransform>();
        containerRect.anchorMin = new Vector2(0, 0);
        containerRect.anchorMax = Vector2.one;
        containerRect.pivot = new Vector2(0, 0);
        containerRect.anchoredPosition = new Vector2(40, 40);
        containerRect.sizeDelta = new Vector2(-80, 150);

        Debug.Log("✅ Created ChoiceButtonContainer");

        // ===== STEP 8: Create Choice Button Prefab =====
        GameObject buttonPrefabObj = new GameObject("ChoiceButtonPrefab");
        buttonPrefabObj.transform.SetParent(containerObj.transform, false);

        Image btnImage = buttonPrefabObj.AddComponent<Image>();
        btnImage.color = new Color(0.2f, 0.2f, 0.2f, 1f);

        Button btn = buttonPrefabObj.AddComponent<Button>();
        ColorBlock colors = btn.colors;
        colors.normalColor = new Color(0.2f, 0.2f, 0.2f, 1f);
        colors.highlightedColor = new Color(0.3f, 0.3f, 0.3f, 1f);
        colors.pressedColor = new Color(0.1f, 0.1f, 0.1f, 1f);
        btn.colors = colors;

        RectTransform btnRect = buttonPrefabObj.GetComponent<RectTransform>();
        btnRect.sizeDelta = new Vector2(0, 50);

        // Add text to button
        GameObject btnTextObj = new GameObject("Text");
        btnTextObj.transform.SetParent(buttonPrefabObj.transform, false);
        TextMeshProUGUI btnText = btnTextObj.AddComponent<TextMeshProUGUI>();
        btnText.text = "[Choice Text]";
        btnText.fontSize = 28;
        btnText.alignment = TextAlignmentOptions.Center;
        btnText.color = Color.white;

        RectTransform btnTextRect = btnTextObj.GetComponent<RectTransform>();
        btnTextRect.anchorMin = Vector2.zero;
        btnTextRect.anchorMax = Vector2.one;
        btnTextRect.offsetMin = Vector2.zero;
        btnTextRect.offsetMax = Vector2.zero;

        // Hide prefab
        buttonPrefabObj.SetActive(false);

        Debug.Log("✅ Created ChoiceButtonPrefab");

        // ===== STEP 9: Wire DialogueManager serialized fields =====
        dialogueManager.NpcNameText = nameText;
        dialogueManager.BodyText = bodyText;
        dialogueManager.ChoiceButtonContainer = containerObj.transform;
        dialogueManager.ChoiceButtonPrefab = buttonPrefabObj;
        dialogueManager.DialogueCanvasGroup = canvasObj.GetComponent<CanvasGroup>();
        dialogueManager.DialogueCanvas = canvas;

        Debug.Log("✅ Wired DialogueManager serialized fields");

        // ===== STEP 10: Create Player =====
        GameObject playerObj = new GameObject("Player");
        playerObj.tag = "Player";
        playerObj.transform.position = new Vector3(0, 1, 0);

        CharacterController charController = playerObj.AddComponent<CharacterController>();
        charController.height = 2f;
        charController.radius = 0.5f;

        // Add simple player controller for movement
        SimplePlayerController playerController = playerObj.AddComponent<SimplePlayerController>();

        // Add a simple body renderer for visualization
        GameObject bodyMesh = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        bodyMesh.name = "PlayerBody";
        bodyMesh.transform.SetParent(playerObj.transform);
        bodyMesh.transform.localPosition = Vector3.zero;
        bodyMesh.transform.localScale = Vector3.one;
        Collider bodyCollider = bodyMesh.GetComponent<Collider>();
        if (bodyCollider != null)
            Object.DestroyImmediate(bodyCollider);

        Renderer bodyRenderer = bodyMesh.GetComponent<Renderer>();
        Material playerMat = new Material(Shader.Find("Standard"));
        playerMat.color = Color.blue;
        bodyRenderer.material = playerMat;

        Debug.Log("✅ Created Player");

        // ===== STEP 11: Add Lighting =====
        RenderSettings.ambientLight = new Color(0.5f, 0.5f, 0.5f, 1f);
        
        GameObject lightObj = new GameObject("DirectionalLight");
        Light light = lightObj.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1f;
        lightObj.transform.rotation = Quaternion.Euler(50f, -30f, 0f);
        
        Debug.Log("✅ Added Lighting");

        // ===== STEP 12: Create NPCs =====
        CreateTestNPC("Ravi", new Vector3(5, 0.5f, 3), "ravi_dialogue");
        CreateTestNPC("Nima", new Vector3(-5, 0.5f, 3), "nima_dialogue");

        Debug.Log("✅ Created NPCs");

        // ===== STEP 13: Save Scene =====
        EditorSceneManager.SaveScene(scene, "Assets/Scenes/VelinorNarrativeTest.unity");
        Debug.Log("✅ Scene saved as VelinorNarrativeTest.unity");

        Debug.Log("\n" +
            "═══════════════════════════════════════════════════════════\n" +
            "🎭 VELINOR NARRATIVE TEST SCENE CREATED\n" +
            "═══════════════════════════════════════════════════════════\n" +
            "✅ Ground plane (20x20 walkable area)\n" +
            "✅ Player with CharacterController + simple movement\n" +
            "✅ 2 Test NPCs: Ravi (green) at (5,0,3), Nima (yellow) at (-5,0,3)\n" +
            "✅ DialogueCanvas (bottom 30% of screen)\n" +
            "✅ StatManager + DialogueManager singletons\n" +
            "✅ Ambient lighting for visibility\n" +
            "\n" +
            "🎮 CONTROLS:\n" +
            "  - WASD: Move around\n" +
            "  - Space: Jump\n" +
            "  - E: Interact with NPCs (when in range, green prompt shows)\n" +
            "\n" +
            "📋 BEFORE PLAYING:\n" +
            "1. Select Ravi in Hierarchy\n" +
            "   - Inspector > NPCInteraction script\n" +
            "   - Set npcId = \"Ravi\"\n" +
            "   - Set startingPassageId = \"ravi_dialogue\"\n" +
            "2. Select Nima in Hierarchy\n" +
            "   - Inspector > NPCInteraction script\n" +
            "   - Set npcId = \"Nima\"\n" +
            "   - Set startingPassageId = \"nima_dialogue\"\n" +
            "3. Press Play and walk toward an NPC!\n" +
            "═══════════════════════════════════════════════════════════");
    }

    static void CreateTestNPC(string npcId, Vector3 position, string startingPassageId)
    {
        GameObject npcObj = new GameObject(npcId);
        npcObj.transform.position = position;

        // Add mesh for visibility - make it bigger (3 units tall)
        GameObject meshObj = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        meshObj.name = "Mesh";
        meshObj.transform.SetParent(npcObj.transform);
        meshObj.transform.localPosition = Vector3.zero;
        meshObj.transform.localScale = new Vector3(0.8f, 1.5f, 0.8f);

        // Remove physics collider, we'll add our own trigger
        Collider meshCollider = meshObj.GetComponent<Collider>();
        if (meshCollider != null)
            Object.DestroyImmediate(meshCollider);

        // Color the NPC - make them distinct
        Renderer meshRenderer = meshObj.GetComponent<Renderer>();
        Material npcMat = new Material(Shader.Find("Standard"));
        npcMat.color = npcId == "Ravi" ? new Color(0.2f, 1f, 0.2f, 1f) : new Color(1f, 1f, 0.2f, 1f); // Bright green or yellow
        meshRenderer.material = npcMat;

        // Add trigger collider (larger radius for easier interaction)
        SphereCollider triggerCollider = npcObj.AddComponent<SphereCollider>();
        triggerCollider.radius = 3f;
        triggerCollider.isTrigger = true;

        // Add rigid body (kinematic, for trigger detection)
        Rigidbody rb = npcObj.AddComponent<Rigidbody>();
        rb.isKinematic = true;
        rb.useGravity = false;

        // Add NPCInteraction script
        NPCInteraction interaction = npcObj.AddComponent<NPCInteraction>();
        // Note: npcId and startingPassageId must be set via Inspector or SerializedProperty

        Debug.Log($"✅ Created NPC: {npcId} at {position}");
    }
}
