using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using TMPro;

/// <summary>
/// SetupMalrikElenyaTestScene: Creates a test scene with both Malrik and Elenya for testing gate-based dialogue.
/// </summary>
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
        
        // Create new scene
        Scene scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
        scene.name = "MalrikElenyaTest";

        // Create ground
        CreateGround();

        // Create lighting
        CreateLighting();

        // Create event system
        CreateEventSystem();

        // Create UI canvases
        CreateInteractionCanvas();
        CreateDialogueCanvas();

        // Create stat display UI
        CreateStatDisplayUI();

        // Create player
        CreatePlayer();

        // Create NPCs - Malrik and Elenya
        CreateMalrik();
        CreateElenya();

        Debug.Log("✅ Scene created: Malrik & Elenya Test Scene");
        Debug.Log("🎮 Use WASD to move, Space to jump, Right-mouse to look, E to talk");
        Debug.Log("🎭 Position: Player at origin, Malrik at (0, 0.66, 5), Elenya at (0, 0.66, -5)");
    }

    static void CreateGround()
    {
        GameObject ground = new GameObject("Ground");
        Mesh planeMesh = Resources.GetBuiltinResource<Mesh>("Quad.fbx");
        MeshFilter meshFilter = ground.AddComponent<MeshFilter>();
        meshFilter.mesh = planeMesh;
        MeshCollider meshCollider = ground.AddComponent<MeshCollider>();
        
        MeshRenderer meshRenderer = ground.AddComponent<MeshRenderer>();
        Material groundMaterial = new Material(Shader.Find("Standard"));
        groundMaterial.color = new Color(0.6f, 0.4f, 0.2f); // Brown
        meshRenderer.material = groundMaterial;

        ground.transform.localScale = new Vector3(20, 1, 20);
        ground.transform.position = Vector3.zero;
    }

    static void CreateLighting()
    {
        RenderSettings.ambientLight = new Color(0.5f, 0.5f, 0.5f);

        GameObject dirLight = new GameObject("Directional Light");
        Light light = dirLight.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1f;
        dirLight.transform.eulerAngles = new Vector3(50, -30, 0);
    }

    static void CreateEventSystem()
    {
        GameObject eventSystemObj = new GameObject("EventSystem");
        EventSystem eventSystem = eventSystemObj.AddComponent<EventSystem>();
        StandaloneInputModule inputModule = eventSystemObj.AddComponent<StandaloneInputModule>();
    }

    static void CreateInteractionCanvas()
    {
        GameObject canvasObj = new GameObject("InteractionCanvas");
        Canvas canvas = canvasObj.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        CanvasScaler scaler = canvasObj.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920, 1080);
        
        GraphicRaycaster raycaster = canvasObj.AddComponent<GraphicRaycaster>();

        // Create prompt text
        GameObject promptObj = new GameObject("PromptText");
        promptObj.transform.SetParent(canvasObj.transform, false);
        RectTransform promptRect = promptObj.AddComponent<RectTransform>();
        promptRect.anchorMin = new Vector2(0.5f, 1f);
        promptRect.anchorMax = new Vector2(0.5f, 1f);
        promptRect.offsetMin = new Vector2(-200, -50);
        promptRect.offsetMax = new Vector2(200, 0);

        TextMeshProUGUI promptText = promptObj.AddComponent<TextMeshProUGUI>();
        promptText.text = "Press E to talk";
        promptText.alignment = TextAlignmentOptions.TopCenter;
        promptText.fontSize = 36;
    }

    static void CreateDialogueCanvas()
    {
        GameObject canvasObj = new GameObject("DialogueCanvas");
        Canvas canvas = canvasObj.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.sortingOrder = 10;
        CanvasScaler scaler = canvasObj.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920, 1080);

        // Create dialogue panel
        GameObject panelObj = new GameObject("DialoguePanel");
        panelObj.transform.SetParent(canvasObj.transform, false);
        RectTransform panelRect = panelObj.AddComponent<RectTransform>();
        panelRect.anchorMin = Vector2.zero;
        panelRect.anchorMax = Vector2.one;
        panelRect.offsetMin = Vector2.zero;
        panelRect.offsetMax = Vector2.zero;

        Image panelImage = panelObj.AddComponent<Image>();
        panelImage.color = new Color(0.1f, 0.1f, 0.1f, 0.9f);
        panelObj.SetActive(false);

        // NPC Name Text
        GameObject nameObj = new GameObject("NPCNameText");
        nameObj.transform.SetParent(panelObj.transform, false);
        RectTransform nameRect = nameObj.AddComponent<RectTransform>();
        nameRect.anchorMin = new Vector2(0, 1);
        nameRect.anchorMax = new Vector2(1, 1);
        nameRect.offsetMin = new Vector2(20, -60);
        nameRect.offsetMax = new Vector2(-20, -20);

        TextMeshProUGUI nameText = nameObj.AddComponent<TextMeshProUGUI>();
        nameText.text = "???";
        nameText.alignment = TextAlignmentOptions.TopLeft;
        nameText.fontSize = 48;

        // Dialogue Body Text
        GameObject bodyObj = new GameObject("DialogueBodyText");
        bodyObj.transform.SetParent(panelObj.transform, false);
        RectTransform bodyRect = bodyObj.AddComponent<RectTransform>();
        bodyRect.anchorMin = new Vector2(0, 0.5f);
        bodyRect.anchorMax = new Vector2(1, 0.9f);
        bodyRect.offsetMin = new Vector2(30, 0);
        bodyRect.offsetMax = new Vector2(-30, 0);

        TextMeshProUGUI bodyText = bodyObj.AddComponent<TextMeshProUGUI>();
        bodyText.text = "Dialogue goes here";
        bodyText.alignment = TextAlignmentOptions.TopLeft;
        bodyText.fontSize = 32;
        bodyText.textWrappingMode = TextWrappingModes.Normal;

        // Choice Button Container
        GameObject containerObj = new GameObject("ChoiceButtonContainer");
        containerObj.transform.SetParent(panelObj.transform, false);
        RectTransform containerRect = containerObj.AddComponent<RectTransform>();
        containerRect.anchorMin = new Vector2(0, 0);
        containerRect.anchorMax = new Vector2(1, 0.35f);
        containerRect.offsetMin = new Vector2(30, 20);
        containerRect.offsetMax = new Vector2(-30, -20);

        VerticalLayoutGroup layoutGroup = containerObj.AddComponent<VerticalLayoutGroup>();
        layoutGroup.spacing = 5;
        layoutGroup.childForceExpandHeight = false;
        layoutGroup.childForceExpandWidth = true;

        ContentSizeFitter sizeFitter = containerObj.AddComponent<ContentSizeFitter>();
        sizeFitter.verticalFit = ContentSizeFitter.FitMode.PreferredSize;

        // Create 4 choice buttons
        for (int i = 0; i < 4; i++)
        {
            CreateChoiceButton(containerObj, i);
        }
    }

    static void CreateChoiceButton(GameObject container, int index)
    {
        GameObject btnObj = new GameObject($"ChoiceButton{index + 1}");
        btnObj.transform.SetParent(container.transform, false);

        RectTransform btnRect = btnObj.AddComponent<RectTransform>();
        LayoutElement layoutElement = btnObj.AddComponent<LayoutElement>();
        layoutElement.preferredHeight = 35;
        layoutElement.preferredWidth = 350;

        Button button = btnObj.AddComponent<Button>();
        Image btnImage = btnObj.AddComponent<Image>();
        btnImage.color = new Color(0.2f, 0.2f, 0.2f, 1f);

        ColorBlock colors = button.colors;
        colors.normalColor = new Color(0.2f, 0.2f, 0.2f, 1f);
        colors.highlightedColor = new Color(0.3f, 0.3f, 0.3f, 1f);
        colors.pressedColor = new Color(0.1f, 0.1f, 0.1f, 1f);
        button.colors = colors;

        // Button text
        GameObject textObj = new GameObject("Text");
        textObj.transform.SetParent(btnObj.transform, false);
        RectTransform textRect = textObj.AddComponent<RectTransform>();
        textRect.anchorMin = Vector2.zero;
        textRect.anchorMax = Vector2.one;
        textRect.offsetMin = new Vector2(5, 5);
        textRect.offsetMax = new Vector2(-5, -5);

        TextMeshProUGUI buttonText = textObj.AddComponent<TextMeshProUGUI>();
        buttonText.text = $"({(char)('T' + index)}) Choice text";
        buttonText.alignment = TextAlignmentOptions.Center;
        buttonText.fontSize = 14;
        buttonText.textWrappingMode = TextWrappingModes.Normal;
    }

    static void CreateStatDisplayUI()
    {
        GameObject canvasObj = new GameObject("StatDisplayUI");
        Canvas canvas = canvasObj.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.sortingOrder = 100;

        GameObject statDisplayObj = new GameObject("StatDisplay");
        statDisplayObj.transform.SetParent(canvasObj.transform, false);
        
        StatDisplayUI statDisplay = statDisplayObj.AddComponent<StatDisplayUI>();
        
        Debug.Log("✅ Stat display UI created");
    }

    static void CreatePlayer()
    {
        // Player body (blue capsule)
        GameObject playerObj = new GameObject("Player");
        playerObj.tag = "Player";
        playerObj.transform.position = new Vector3(0, 0.66f, -5f);

        // Visual capsule (scaled 0.66)
        GameObject capsuleObj = new GameObject("Capsule");
        capsuleObj.transform.SetParent(playerObj.transform);
        capsuleObj.transform.localPosition = Vector3.zero;
        capsuleObj.transform.localScale = new Vector3(0.66f, 0.66f, 0.66f);

        CapsuleCollider capsuleCollider = capsuleObj.AddComponent<CapsuleCollider>();
        capsuleCollider.height = 1.8f;
        capsuleCollider.radius = 0.3f;
        capsuleCollider.center = new Vector3(0, 0.33f, 0);

        MeshFilter meshFilter = capsuleObj.AddComponent<MeshFilter>();
        meshFilter.mesh = Resources.GetBuiltinResource<Mesh>("Capsule.fbx");
        MeshRenderer meshRenderer = capsuleObj.AddComponent<MeshRenderer>();
        Material playerMat = new Material(Shader.Find("Standard"));
        playerMat.color = new Color(0.2f, 0.2f, 0.8f); // Blue
        meshRenderer.material = playerMat;

        // Actual collider (unscaled)
        CharacterController charController = playerObj.AddComponent<CharacterController>();
        charController.height = 1.8f;
        charController.radius = 0.3f;
        charController.center = new Vector3(0, 0.33f, 0);

        // Camera
        GameObject cameraObj = new GameObject("Camera");
        cameraObj.transform.SetParent(playerObj.transform);
        cameraObj.transform.localPosition = new Vector3(0, 1.03f, -1.65f);
        Camera camera = cameraObj.AddComponent<Camera>();

        // Scripts
        playerObj.AddComponent<SimplePlayerController>();
        playerObj.AddComponent<PlayerStats>();

        Debug.Log("✅ Player created at (0, 0.66, -5)");
    }

    static void CreateMalrik()
    {
        GameObject npcObj = new GameObject("Malrik");
        npcObj.transform.position = new Vector3(0, 0.66f, 5f);

        // Visual capsule (purple)
        GameObject capsuleObj = new GameObject("Capsule");
        capsuleObj.transform.SetParent(npcObj.transform);
        capsuleObj.transform.localPosition = Vector3.zero;
        capsuleObj.transform.localScale = new Vector3(0.66f, 0.66f, 0.66f);

        CapsuleCollider capsuleCollider = capsuleObj.AddComponent<CapsuleCollider>();
        capsuleCollider.height = 1.8f;
        capsuleCollider.radius = 0.3f;

        MeshFilter meshFilter = capsuleObj.AddComponent<MeshFilter>();
        meshFilter.mesh = Resources.GetBuiltinResource<Mesh>("Capsule.fbx");
        MeshRenderer meshRenderer = capsuleObj.AddComponent<MeshRenderer>();
        Material npcMat = new Material(Shader.Find("Standard"));
        npcMat.color = new Color(0.7f, 0.2f, 0.7f); // Purple
        meshRenderer.material = npcMat;

        // Trigger collider (unscaled)
        SphereCollider triggerCollider = npcObj.AddComponent<SphereCollider>();
        triggerCollider.radius = 0.5f;
        triggerCollider.isTrigger = false;

        // Scripts
        NPCInteraction npcInteraction = npcObj.AddComponent<NPCInteraction>();
        npcInteraction.GetType().GetField("npcId", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.SetValue(npcInteraction, "Malrik");

        npcObj.AddComponent<MalrikDialogueSequence>();
        npcObj.AddComponent<DialogueGateEvaluator>();

        Debug.Log("✅ Malrik created at (0, 0.66, 5)");
    }

    static void CreateElenya()
    {
        GameObject npcObj = new GameObject("Elenya");
        npcObj.transform.position = new Vector3(-3, 0.66f, 0f);

        // Visual capsule (cyan)
        GameObject capsuleObj = new GameObject("Capsule");
        capsuleObj.transform.SetParent(npcObj.transform);
        capsuleObj.transform.localPosition = Vector3.zero;
        capsuleObj.transform.localScale = new Vector3(0.66f, 0.66f, 0.66f);

        CapsuleCollider capsuleCollider = capsuleObj.AddComponent<CapsuleCollider>();
        capsuleCollider.height = 1.8f;
        capsuleCollider.radius = 0.3f;

        MeshFilter meshFilter = capsuleObj.AddComponent<MeshFilter>();
        meshFilter.mesh = Resources.GetBuiltinResource<Mesh>("Capsule.fbx");
        MeshRenderer meshRenderer = capsuleObj.AddComponent<MeshRenderer>();
        Material npcMat = new Material(Shader.Find("Standard"));
        npcMat.color = new Color(0.2f, 0.8f, 0.8f); // Cyan
        meshRenderer.material = npcMat;

        // Trigger collider (unscaled)
        SphereCollider triggerCollider = npcObj.AddComponent<SphereCollider>();
        triggerCollider.radius = 0.5f;
        triggerCollider.isTrigger = false;

        // Scripts
        NPCInteraction npcInteraction = npcObj.AddComponent<NPCInteraction>();
        npcInteraction.GetType().GetField("npcId", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.SetValue(npcInteraction, "Elenya");

        npcObj.AddComponent<VelinorGame.Core.ElenyaDialogueSequence>();
        npcObj.AddComponent<DialogueGateEvaluator>();

        Debug.Log("✅ Elenya created at (-3, 0.66, 0)");
    }
}
