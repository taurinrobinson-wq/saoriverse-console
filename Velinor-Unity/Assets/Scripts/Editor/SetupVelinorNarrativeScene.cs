using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.EventSystems;
using TMPro;
using UnityEngine.UI;

public class SetupVelinorNarrativeScene
{
    [MenuItem("Velinor/Create Narrative Test Scene")]
    public static void CreateNarrativeTestScene()
    {
        Debug.Log("🎭 Creating Velinor Narrative Test Scene (based on Marketplace Block A)...");
        
        // Create completely new scene
        var newScene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects);
        Debug.Log($"✅ Created new scene: {newScene.name}");

        // Populate the scene using Marketplace Block A structure
        CreateGround();
        CreateLighting();
        CreateEventSystem();
        CreateDialogueUI();
        CreatePlayer();
        CreateNPCs();

        // Save the new scene
        EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(), "Assets/Scenes/VelinorNarrativeTest.unity");
        Debug.Log("✅ Velinor Narrative Test scene created and saved successfully!");

        Debug.Log("\n" +
            "═══════════════════════════════════════════════════════════\n" +
            "🎭 VELINOR NARRATIVE TEST SCENE CREATED\n" +
            "═══════════════════════════════════════════════════════════\n" +
            "✅ Ground (20×20 walkable area)\n" +
            "✅ Player with CharacterController (third-person camera)\n" +
            "✅ 2 Test NPCs: Ravi and Nima (purple capsules)\n" +
            "✅ DialogueCanvas with UI hierarchy\n" +
            "✅ StatManager + DialogueManager singletons\n" +
            "✅ Proper lighting\n" +
            "\n" +
            "🎮 CONTROLS:\n" +
            "  - WASD: Move\n" +
            "  - Mouse: Look around\n" +
            "  - E: Interact with NPCs (when close)\n" +
            "\n" +
            "📋 BEFORE PLAYING:\n" +
            "1. Select NPC_Ravi in Hierarchy\n" +
            "   - Set NPCInteraction npcId = \"Ravi\"\n" +
            "   - Set startingPassageId = \"ravi_dialogue\"\n" +
            "2. Select NPC_Nima in Hierarchy\n" +
            "   - Set NPCInteraction npcId = \"Nima\"\n" +
            "   - Set startingPassageId = \"nima_dialogue\"\n" +
            "3. Press Play!\n" +
            "═══════════════════════════════════════════════════════════");
    }

    static void CreateGround()
    {
        GameObject groundObj = new GameObject("Ground");
        groundObj.transform.position = new Vector3(10, 0, 10);

        // Create ground plane (20×20)
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

        BoxCollider groundCollider = groundObj.AddComponent<BoxCollider>();
        groundCollider.size = new Vector3(20, 0.1f, 20);
        groundCollider.center = Vector3.zero;

        Rigidbody groundRb = groundObj.AddComponent<Rigidbody>();
        groundRb.isKinematic = true;
        groundRb.useGravity = false;

        Debug.Log("✅ Created Ground");
    }

    static void CreateLighting()
    {
        RenderSettings.ambientLight = new Color(0.5f, 0.5f, 0.5f, 1f);
        
        GameObject lightObj = new GameObject("DirectionalLight");
        Light light = lightObj.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1f;
        lightObj.transform.rotation = Quaternion.Euler(50f, -30f, 0f);

        Debug.Log("✅ Added Lighting");
    }

    static void CreateEventSystem()
    {
        // EventSystem for UI interaction
        GameObject esObj = new GameObject("EventSystem");
        esObj.AddComponent<EventSystem>();
        esObj.AddComponent<StandaloneInputModule>();

        Debug.Log("✅ Created EventSystem");
    }

    static void CreateDialogueUI()
    {
        // DialogueCanvas
        GameObject canvasObj = new GameObject("DialogueCanvas");
        Canvas canvas = canvasObj.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        
        RectTransform canvasRect = canvasObj.GetComponent<RectTransform>();
        canvasRect.anchorMin = Vector2.zero;
        canvasRect.anchorMax = Vector2.one;
        canvasRect.offsetMin = Vector2.zero;
        canvasRect.offsetMax = Vector2.zero;

        canvasObj.AddComponent<GraphicRaycaster>();
        CanvasGroup canvasGroup = canvasObj.AddComponent<CanvasGroup>();

        CanvasScaler scaler = canvasObj.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920, 1080);

        // DialoguePanel (bottom 30%)
        GameObject panelObj = new GameObject("DialoguePanel");
        panelObj.transform.SetParent(canvasObj.transform, false);
        Image panelImage = panelObj.AddComponent<Image>();
        panelImage.color = new Color(0, 0, 0, 0.8f);

        RectTransform panelRect = panelObj.GetComponent<RectTransform>();
        panelRect.anchorMin = new Vector2(0, 0);
        panelRect.anchorMax = new Vector2(1, 0.3f);
        panelRect.offsetMin = Vector2.zero;
        panelRect.offsetMax = Vector2.zero;

        // NPCNameText
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

        // DialogueBodyText
        GameObject bodyTextObj = new GameObject("DialogueBodyText");
        bodyTextObj.transform.SetParent(panelObj.transform, false);
        TextMeshProUGUI bodyText = bodyTextObj.AddComponent<TextMeshProUGUI>();
        bodyText.text = "[Dialogue will appear here]";
        bodyText.fontSize = 32;
        bodyText.alignment = TextAlignmentOptions.TopLeft;
        bodyText.color = Color.white;
        bodyText.wordWrappingRatios = 0.3f;

        RectTransform bodyRect = bodyTextObj.GetComponent<RectTransform>();
        bodyRect.anchorMin = new Vector2(0, 1);
        bodyRect.anchorMax = new Vector2(1, 1);
        bodyRect.pivot = new Vector2(0, 1);
        bodyRect.anchoredPosition = new Vector2(40, -140);
        bodyRect.sizeDelta = new Vector2(-80, 400);

        // ChoiceButtonContainer
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

        // ChoiceButtonPrefab
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

        buttonPrefabObj.SetActive(false);

        // Create StatManager and DialogueManager
        GameObject statManagerObj = new GameObject("StatManager");
        statManagerObj.AddComponent<StatManager>();

        GameObject dialogueManagerObj = new GameObject("DialogueManager");
        DialogueManager dialogueManager = dialogueManagerObj.AddComponent<DialogueManager>();
        
        // Wire DialogueManager
        dialogueManager.NpcNameText = nameText;
        dialogueManager.BodyText = bodyText;
        dialogueManager.ChoiceButtonContainer = containerObj.transform;
        dialogueManager.ChoiceButtonPrefab = buttonPrefabObj;
        dialogueManager.DialogueCanvasGroup = canvasGroup;
        dialogueManager.DialogueCanvas = canvas;

        Debug.Log("✅ Created DialogueUI and wired DialogueManager");
    }

    static void CreatePlayer()
    {
        GameObject playerObj = new GameObject("Player");
        playerObj.tag = "Player";
        playerObj.transform.position = new Vector3(10, 0, 0);
        playerObj.transform.localScale = new Vector3(0.66f, 0.66f, 0.66f);

        // Character controller
        CharacterController charController = playerObj.AddComponent<CharacterController>();
        charController.height = 1.8f;
        charController.radius = 0.25f;
        charController.center = new Vector3(0, 0.9f, 0);

        // Visual (blue capsule)
        GameObject visualObj = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        visualObj.name = "Visual";
        visualObj.transform.SetParent(playerObj.transform);
        visualObj.transform.localPosition = Vector3.zero;
        visualObj.transform.localScale = new Vector3(1, 1, 1);

        Object.DestroyImmediate(visualObj.GetComponent<Collider>());

        Material playerMat = new Material(Shader.Find("Standard"));
        playerMat.color = Color.blue;
        visualObj.GetComponent<MeshRenderer>().material = playerMat;

        // Rigidbody
        Rigidbody rb = playerObj.AddComponent<Rigidbody>();
        rb.isKinematic = true;
        rb.useGravity = false;

        // Camera
        GameObject cameraObj = new GameObject("MainCamera");
        cameraObj.tag = "MainCamera";
        cameraObj.transform.SetParent(playerObj.transform);
        cameraObj.transform.localPosition = new Vector3(0, 0.79f, -1.65f);

        Camera cam = cameraObj.AddComponent<Camera>();
        cam.clearFlags = CameraClearFlags.Skybox;

        Debug.Log("✅ Created Player");
    }

    static void CreateNPCs()
    {
        Vector3[] npcPositions = new Vector3[]
        {
            new Vector3(10, 0.66f, 8),
            new Vector3(10, 0.66f, 13)
        };

        string[] npcNames = { "Ravi", "Nima" };

        for (int i = 0; i < npcPositions.Length; i++)
        {
            CreateNPC(npcPositions[i], npcNames[i]);
        }
    }

    static void CreateNPC(Vector3 position, string npcName)
    {
        GameObject npcObj = new GameObject($"NPC_{npcName}");
        npcObj.transform.position = position;
        npcObj.transform.localScale = new Vector3(0.66f, 0.66f, 0.66f);

        // Visual (purple capsule)
        GameObject visualObj = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        visualObj.name = "Visual";
        visualObj.transform.SetParent(npcObj.transform);
        visualObj.transform.localPosition = Vector3.zero;
        visualObj.transform.localScale = new Vector3(1, 1, 1);

        Object.DestroyImmediate(visualObj.GetComponent<Collider>());

        Material npcMat = new Material(Shader.Find("Standard"));
        npcMat.color = new Color(0.7f, 0.3f, 0.9f, 1f);
        visualObj.GetComponent<MeshRenderer>().material = npcMat;

        // Solid collider (blocks movement)
        CapsuleCollider solidCollider = npcObj.AddComponent<CapsuleCollider>();
        solidCollider.isTrigger = false;
        solidCollider.radius = 0.25f;
        solidCollider.height = 1.8f;
        solidCollider.center = new Vector3(0, 0.9f, 0);

        // Trigger collider (detects interaction)
        GameObject triggerObj = new GameObject("InteractionTrigger");
        triggerObj.transform.SetParent(npcObj.transform);
        triggerObj.transform.localPosition = Vector3.zero;

        CapsuleCollider triggerCollider = triggerObj.AddComponent<CapsuleCollider>();
        triggerCollider.isTrigger = true;
        triggerCollider.radius = 0.5f;
        triggerCollider.height = 1.8f;
        triggerCollider.center = new Vector3(0, 0.9f, 0);

        // Rigidbody
        Rigidbody rb = npcObj.AddComponent<Rigidbody>();
        rb.isKinematic = true;
        rb.useGravity = false;

        // NPC interaction script
        NPCInteraction npcInteraction = npcObj.AddComponent<NPCInteraction>();

        Debug.Log($"✅ Created NPC: {npcName} at {position}");
    }
}
