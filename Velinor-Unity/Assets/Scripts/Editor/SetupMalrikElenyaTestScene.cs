using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.EventSystems;
using TMPro;
using UnityEngine.UI;

public class SetupMalrikElenyaTestScene
{
    [MenuItem("Velinor/Create Malrik & Elenya Test Scene")]
    public static void CreateTestScene()
    {
        // Prevent scene creation during play mode
        if (EditorApplication.isPlaying)
        {
            EditorUtility.DisplayDialog("Cannot Create Scene", "Scene creation is disabled during play mode. Please exit play mode first.", "OK");
            return;
        }
        
        Debug.Log("🎭 Creating Malrik & Elenya test scene...");
        
        // Create completely new scene
        var newScene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects);
        
        CreateGround();
        CreateLighting();
        CreateEventSystem();
        CreateInteractionUI();
        CreateDialogueUI();
        CreateStatDisplay();
        CreatePlayer();
        CreateMalrik();
        CreateElenya();

        // Save scene
        EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(), "Assets/Scenes/MalrikElenyaTestScene.unity");
        Debug.Log("✅ Malrik & Elenya Test Scene created successfully!");
        
        Debug.Log("\n" +
            "═══════════════════════════════════════════════════════════\n" +
            "🎭 MALRIK & ELENYA TEST SCENE READY\n" +
            "═══════════════════════════════════════════════════════════\n" +
            "✅ Ground (20×20 walkable area)\n" +
            "✅ Player with CharacterController\n" +
            "✅ 2 Test NPCs: Malrik and Elenya\n" +
            "✅ Gate-Based Dialogue System\n" +
            "✅ TONE Stats & Dialogue Gates\n" +
            "\n" +
            "🎮 CONTROLS:\n" +
            "  - WASD: Move\n" +
            "  - Mouse: Look around\n" +
            "  - E: Talk to NPCs (when close)\n" +
            "\n" +
            "📍 LAYOUT:\n" +
            "  - Player: Center (0, 0.66, 0)\n" +
            "  - Malrik: Behind (0, 0.66, 5) - purple\n" +
            "  - Elenya: Ahead (0, 0.66, -5) - cyan\n" +
            "═══════════════════════════════════════════════════════════");
    }

    static void CreateGround()
    {
        GameObject groundObj = new GameObject("Ground");
        groundObj.transform.position = new Vector3(0, 0, 0);

        // Create ground mesh (20×20)
        MeshFilter mf = groundObj.AddComponent<MeshFilter>();
        MeshRenderer mr = groundObj.AddComponent<MeshRenderer>();
        
        Mesh groundMesh = new Mesh();
        groundMesh.vertices = new Vector3[]
        {
            new Vector3(-10, 0, -10),
            new Vector3(10, 0, -10),
            new Vector3(10, 0, 10),
            new Vector3(-10, 0, 10)
        };
        groundMesh.triangles = new int[] { 0, 2, 1, 0, 3, 2 };
        groundMesh.RecalculateNormals();
        mf.mesh = groundMesh;

        Material groundMat = new Material(Shader.Find("Standard"));
        groundMat.color = new Color(0.6f, 0.5f, 0.4f, 1f);
        mr.material = groundMat;

        // Collider positioned slightly above ground to prevent z-fighting
        BoxCollider groundCollider = groundObj.AddComponent<BoxCollider>();
        groundCollider.size = new Vector3(20, 0.01f, 20);
        groundCollider.center = new Vector3(0, -0.005f, 0);

        Rigidbody groundRb = groundObj.AddComponent<Rigidbody>();
        groundRb.isKinematic = true;
        groundRb.useGravity = false;
    }

    static void CreateLighting()
    {
        RenderSettings.ambientLight = new Color(0.5f, 0.5f, 0.5f, 1f);
        
        GameObject lightObj = new GameObject("DirectionalLight");
        Light light = lightObj.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1f;
        lightObj.transform.rotation = Quaternion.Euler(50f, -30f, 0f);
    }

    static void CreateEventSystem()
    {
        GameObject esObj = new GameObject("EventSystem");
        esObj.AddComponent<EventSystem>();
        esObj.AddComponent<StandaloneInputModule>();
    }

    static void CreateInteractionUI()
    {
        GameObject canvasObj = new GameObject("InteractionCanvas");
        Canvas canvas = canvasObj.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        
        RectTransform canvasRect = canvasObj.GetComponent<RectTransform>();
        canvasRect.anchorMin = Vector2.zero;
        canvasRect.anchorMax = Vector2.one;
        canvasRect.offsetMin = Vector2.zero;
        canvasRect.offsetMax = Vector2.zero;

        canvasObj.AddComponent<GraphicRaycaster>();
        CanvasScaler scaler = canvasObj.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920, 1080);

        // Prompt text (top center)
        GameObject promptObj = new GameObject("PromptText");
        promptObj.transform.SetParent(canvasObj.transform, false);
        TextMeshProUGUI promptText = promptObj.AddComponent<TextMeshProUGUI>();
        promptText.text = "";
        promptText.fontSize = 36;
        promptText.alignment = TextAlignmentOptions.Top;
        promptText.color = Color.white;

        RectTransform promptRect = promptObj.GetComponent<RectTransform>();
        promptRect.anchorMin = new Vector2(0.5f, 1);
        promptRect.anchorMax = new Vector2(0.5f, 1);
        promptRect.pivot = new Vector2(0.5f, 1);
        promptRect.anchoredPosition = new Vector2(0, -40);
        promptRect.sizeDelta = new Vector2(600, 100);

        // Tag it for retrieval
        canvasObj.name = "InteractionCanvas";
    }

    static void CreateDialogueUI()
    {
        // DialogueCanvas (bottom 30% of screen)
        GameObject canvasObj = new GameObject("DialogueCanvas");
        Canvas canvas = canvasObj.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        
        RectTransform canvasRect = canvasObj.GetComponent<RectTransform>();
        canvasRect.anchorMin = Vector2.zero;
        canvasRect.anchorMax = Vector2.one;
        canvasRect.offsetMin = Vector2.zero;
        canvasRect.offsetMax = Vector2.zero;

        canvasObj.AddComponent<GraphicRaycaster>();
        CanvasScaler scaler = canvasObj.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920, 1080);

        // DialoguePanel (bottom 25% - starts hidden)
        GameObject panelObj = new GameObject("DialoguePanel");
        panelObj.transform.SetParent(canvasObj.transform, false);
        panelObj.SetActive(false);  // START HIDDEN
        Image panelImage = panelObj.AddComponent<Image>();
        panelImage.color = new Color(0, 0, 0, 0.8f);

        RectTransform panelRect = panelObj.GetComponent<RectTransform>();
        panelRect.anchorMin = new Vector2(0, 0);
        panelRect.anchorMax = new Vector2(1, 0.25f);
        panelRect.offsetMin = Vector2.zero;
        panelRect.offsetMax = Vector2.zero;

        // NPCNameText (smaller)
        GameObject nameTextObj = new GameObject("NPCNameText");
        nameTextObj.transform.SetParent(panelObj.transform, false);
        TextMeshProUGUI nameText = nameTextObj.AddComponent<TextMeshProUGUI>();
        nameText.text = "[NPC Name]";
        nameText.fontSize = 36;
        nameText.alignment = TextAlignmentOptions.TopLeft;
        nameText.color = Color.white;

        RectTransform nameRect = nameTextObj.GetComponent<RectTransform>();
        nameRect.anchorMin = new Vector2(0, 1);
        nameRect.anchorMax = new Vector2(0, 1);
        nameRect.pivot = new Vector2(0, 1);
        nameRect.anchoredPosition = new Vector2(20, -15);
        nameRect.sizeDelta = new Vector2(300, 50);

        // DialogueBodyText (smaller)
        GameObject bodyTextObj = new GameObject("DialogueBodyText");
        bodyTextObj.transform.SetParent(panelObj.transform, false);
        TextMeshProUGUI bodyText = bodyTextObj.AddComponent<TextMeshProUGUI>();
        bodyText.text = "[Dialogue will appear here]";
        bodyText.fontSize = 24;
        bodyText.alignment = TextAlignmentOptions.TopLeft;
        bodyText.color = Color.white;

        RectTransform bodyRect = bodyTextObj.GetComponent<RectTransform>();
        bodyRect.anchorMin = new Vector2(0, 1);
        bodyRect.anchorMax = new Vector2(1, 1);
        bodyRect.pivot = new Vector2(0, 1);
        bodyRect.anchoredPosition = new Vector2(20, -65);
        bodyRect.sizeDelta = new Vector2(-40, 100);

        // ChoiceButtonContainer
        GameObject containerObj = new GameObject("ChoiceButtonContainer");
        containerObj.transform.SetParent(panelObj.transform, false);

        VerticalLayoutGroup layoutGroup = containerObj.AddComponent<VerticalLayoutGroup>();
        layoutGroup.spacing = 5;
        layoutGroup.childForceExpandHeight = false;
        layoutGroup.childForceExpandWidth = true;
        layoutGroup.padding = new RectOffset(0, 0, 0, 0);

        ContentSizeFitter contentSizeFitter = containerObj.AddComponent<ContentSizeFitter>();
        contentSizeFitter.horizontalFit = ContentSizeFitter.FitMode.PreferredSize;
        contentSizeFitter.verticalFit = ContentSizeFitter.FitMode.PreferredSize;

        RectTransform containerRect = containerObj.GetComponent<RectTransform>();
        containerRect.anchorMin = new Vector2(0, 0);
        containerRect.anchorMax = Vector2.one;
        containerRect.pivot = new Vector2(0, 0);
        containerRect.anchoredPosition = new Vector2(20, 10);
        containerRect.sizeDelta = new Vector2(-40, 150);  // Increased height for 4 buttons

        // Create four dialogue option buttons (one for each TONE: T/O/N/E)
        CreateDialogueButton(containerObj, "OptionButton1");
        CreateDialogueButton(containerObj, "OptionButton2");
        CreateDialogueButton(containerObj, "OptionButton3");
        CreateDialogueButton(containerObj, "OptionButton4");
    }

    static void CreateDialogueButton(GameObject parent, string buttonName)
    {
        GameObject buttonObj = new GameObject(buttonName);
        buttonObj.transform.SetParent(parent.transform, false);

        Image btnImage = buttonObj.AddComponent<Image>();
        btnImage.color = new Color(0.2f, 0.2f, 0.2f, 1f);

        Button btn = buttonObj.AddComponent<Button>();
        ColorBlock colors = btn.colors;
        colors.normalColor = new Color(0.2f, 0.2f, 0.2f, 1f);
        colors.highlightedColor = new Color(0.3f, 0.3f, 0.3f, 1f);
        colors.pressedColor = new Color(0.1f, 0.1f, 0.1f, 1f);
        btn.colors = colors;

        RectTransform btnRect = buttonObj.GetComponent<RectTransform>();
        btnRect.sizeDelta = new Vector2(350, 35);

        LayoutElement layoutElement = buttonObj.AddComponent<LayoutElement>();
        layoutElement.preferredWidth = 350;
        layoutElement.preferredHeight = 35;

        GameObject btnTextObj = new GameObject("Text");
        btnTextObj.transform.SetParent(buttonObj.transform, false);
        TextMeshProUGUI btnText = btnTextObj.AddComponent<TextMeshProUGUI>();
        btnText.text = "[Choice Text]";
        btnText.fontSize = 14;  // Reduced from 20 for better fit
        btnText.alignment = TextAlignmentOptions.Center;
        btnText.color = Color.white;
        btnText.textWrappingMode = TextWrappingModes.Normal;  // Enable text wrapping
        btnText.horizontalMapping = TextureMappingOptions.Character;
        btnText.verticalMapping = TextureMappingOptions.Character;
        btnText.overflowMode = TextOverflowModes.Truncate;  // Truncate if text too long

        RectTransform btnTextRect = btnTextObj.GetComponent<RectTransform>();
        btnTextRect.anchorMin = Vector2.zero;
        btnTextRect.anchorMax = Vector2.one;
        btnTextRect.offsetMin = new Vector2(5, 5);  // Padding
        btnTextRect.offsetMax = new Vector2(-5, -5);

        buttonObj.SetActive(true);
    }

    static void CreateStatDisplay()
    {
        // Create stat display game object
        GameObject statDisplayObj = new GameObject("StatDisplayUI");
        statDisplayObj.AddComponent<StatDisplayUI>();
        Debug.Log("✅ Stat display UI created");
    }

    static void CreatePlayer()
    {
        GameObject playerObj = new GameObject("Player");
        playerObj.tag = "Player";
        // Root stays at scale (1,1,1) - never scale the root!
        playerObj.transform.position = new Vector3(0, 0.66f, 0f);
        playerObj.transform.localScale = Vector3.one;

        // Character controller - use standard unscaled dimensions
        CharacterController charController = playerObj.AddComponent<CharacterController>();
        charController.height = 1.8f;      // Standard unscaled capsule height
        charController.radius = 0.3f;      // Standard unscaled capsule radius
        charController.center = new Vector3(0, 0.33f, 0);  // Lowered center to keep character grounded

        // Add player movement script
        playerObj.AddComponent<SimplePlayerController>();        
        // Add player stats tracking
        playerObj.AddComponent<PlayerStats>();
        
        // Visual (blue capsule) - scaled child, root stays 1,1,1
        GameObject visualObj = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        visualObj.name = "Visual";
        visualObj.transform.SetParent(playerObj.transform);
        visualObj.transform.localPosition = Vector3.zero;
        visualObj.transform.localScale = new Vector3(0.66f, 0.66f, 0.66f);  // Only scale the visual

        Object.DestroyImmediate(visualObj.GetComponent<Collider>());
        Material playerMat = new Material(Shader.Find("Standard"));
        playerMat.color = Color.blue;
        visualObj.GetComponent<MeshRenderer>().material = playerMat;

        // Rigidbody
        Rigidbody rb = playerObj.AddComponent<Rigidbody>();
        rb.isKinematic = true;
        rb.useGravity = false;

        // Camera (offset behind player, at eye height)
        GameObject cameraObj = new GameObject("MainCamera");
        cameraObj.tag = "MainCamera";
        cameraObj.transform.SetParent(playerObj.transform);
        cameraObj.transform.localPosition = new Vector3(0, 1.03f, -1.65f);  // Adjusted for raised root
        Camera cam = cameraObj.AddComponent<Camera>();
        cam.clearFlags = CameraClearFlags.Skybox;
    }

    static void CreateMalrik()
    {
        GameObject malrikObj = new GameObject("NPC_Malrik");
        // Root stays at scale (1,1,1) - never scale the root!
        malrikObj.transform.position = new Vector3(0, 0.66f, 5f);  // Behind player
        malrikObj.transform.localScale = Vector3.one;

        // Visual (purple capsule) - scaled child only
        GameObject visualObj = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        visualObj.name = "Visual";
        visualObj.transform.SetParent(malrikObj.transform);
        visualObj.transform.localPosition = Vector3.zero;
        visualObj.transform.localScale = new Vector3(0.66f, 0.66f, 0.66f);  // Only scale the visual

        Object.DestroyImmediate(visualObj.GetComponent<Collider>());
        Material malrikMat = new Material(Shader.Find("Standard"));
        malrikMat.color = new Color(0.7f, 0.3f, 0.9f, 1f);  // Purple
        visualObj.GetComponent<MeshRenderer>().material = malrikMat;

        // Solid collider (BLOCKS movement - use standard unscaled dimensions)
        CapsuleCollider solidCollider = malrikObj.AddComponent<CapsuleCollider>();
        solidCollider.isTrigger = false;  // NOT a trigger - blocks movement
        solidCollider.radius = 0.3f;      // Standard unscaled radius
        solidCollider.height = 1.8f;      // Standard unscaled height
        solidCollider.center = new Vector3(0, 0.33f, 0);  // Lowered center to keep NPC grounded

        // Separate trigger collider (detects interaction - use child GameObject)
        GameObject triggerObj = new GameObject("InteractionTrigger");
        triggerObj.transform.SetParent(malrikObj.transform);
        triggerObj.transform.localPosition = Vector3.zero;

        CapsuleCollider triggerCollider = triggerObj.AddComponent<CapsuleCollider>();
        triggerCollider.isTrigger = true;  // This IS a trigger - just for detection
        triggerCollider.radius = 0.3f;     // Match solid collider
        triggerCollider.height = 1.8f;     // Match solid collider
        triggerCollider.center = new Vector3(0, 0.33f, 0);  // Match solid collider

        // Rigidbody
        Rigidbody rb = malrikObj.AddComponent<Rigidbody>();
        rb.isKinematic = true;
        rb.useGravity = false;

        // NPC interaction script
        NPCInteraction npcInteraction = malrikObj.AddComponent<NPCInteraction>();
        npcInteraction.GetType().GetField("npcId", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.SetValue(npcInteraction, "Malrik");

        // Add dialogue sequences
        malrikObj.AddComponent<MalrikDialogueSequence>();
        malrikObj.AddComponent<DialogueGateEvaluator>();

        Debug.Log("✅ Malrik created at (0, 0.66, 5)");
    }

    static void CreateElenya()
    {
        GameObject elenyaObj = new GameObject("NPC_Elenya");
        // Root stays at scale (1,1,1) - never scale the root!
        elenyaObj.transform.position = new Vector3(0, 0.66f, -5f);  // Ahead of player
        elenyaObj.transform.localScale = Vector3.one;

        // Visual (cyan capsule) - scaled child only
        GameObject visualObj = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        visualObj.name = "Visual";
        visualObj.transform.SetParent(elenyaObj.transform);
        visualObj.transform.localPosition = Vector3.zero;
        visualObj.transform.localScale = new Vector3(0.66f, 0.66f, 0.66f);  // Only scale the visual

        Object.DestroyImmediate(visualObj.GetComponent<Collider>());
        Material elenyaMat = new Material(Shader.Find("Standard"));
        elenyaMat.color = new Color(0.2f, 0.8f, 0.8f, 1f);  // Cyan
        visualObj.GetComponent<MeshRenderer>().material = elenyaMat;

        // Solid collider (BLOCKS movement - use standard unscaled dimensions)
        CapsuleCollider solidCollider = elenyaObj.AddComponent<CapsuleCollider>();
        solidCollider.isTrigger = false;  // NOT a trigger - blocks movement
        solidCollider.radius = 0.3f;      // Standard unscaled radius
        solidCollider.height = 1.8f;      // Standard unscaled height
        solidCollider.center = new Vector3(0, 0.33f, 0);  // Lowered center to keep NPC grounded

        // Separate trigger collider (detects interaction - use child GameObject)
        GameObject triggerObj = new GameObject("InteractionTrigger");
        triggerObj.transform.SetParent(elenyaObj.transform);
        triggerObj.transform.localPosition = Vector3.zero;

        CapsuleCollider triggerCollider = triggerObj.AddComponent<CapsuleCollider>();
        triggerCollider.isTrigger = true;  // This IS a trigger - just for detection
        triggerCollider.radius = 0.3f;     // Match solid collider
        triggerCollider.height = 1.8f;     // Match solid collider
        triggerCollider.center = new Vector3(0, 0.33f, 0);  // Match solid collider

        // Rigidbody
        Rigidbody rb = elenyaObj.AddComponent<Rigidbody>();
        rb.isKinematic = true;
        rb.useGravity = false;

        // NPC interaction script
        NPCInteraction npcInteraction = elenyaObj.AddComponent<NPCInteraction>();
        npcInteraction.GetType().GetField("npcId", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.SetValue(npcInteraction, "Elenya");

        // Add dialogue sequences
        elenyaObj.AddComponent<VelinorGame.Core.ElenyaDialogueSequence>();
        elenyaObj.AddComponent<DialogueGateEvaluator>();

        Debug.Log("✅ Elenya created at (0, 0.66, -5)");
    }
}
