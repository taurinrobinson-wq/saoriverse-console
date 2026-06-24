using UnityEngine;
using UnityEngine.EventSystems;
using UnityEditor;
using UnityEditor.SceneManagement;
using TMPro;
using UnityEngine.UI;

public class CreateMarketplaceBlockA
{
    [MenuItem("Velinor/Create Marketplace Block A Scene")]
    public static void CreateScene()
    {
        Debug.Log("🏪 Starting fresh Marketplace Block A scene creation...");
        
        // Create completely new scene
        var newScene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects);
        Debug.Log($"✅ Created new scene: {newScene.name}");
        
        // Now populate the fresh scene
        Debug.Log("🏪 Populating Marketplace Block A scene...");

        // === GROUND ===
        CreateGround();

        // === MARKET STALLS (Left & Right Barriers) ===
        CreateLeftStallBarrier();
        CreateRightStallBarrier();

        // === LIGHTING ===
        CreateLighting();

        // === UI SYSTEM ===
        CreateEventSystem();
        CreateInteractionUI();
        CreateDialogueUI();

        // === PLAYER ===
        CreatePlayer();

        // === NPCs ===
        CreateNPCs();

        // === GLYPH ===
        CreateGlyph();

        // === FORWARD EXIT TRIGGER ===
        CreateExitTrigger();

        // === BACK BARRIER ===
        CreateBackBarrier();

        // Save the new scene
        EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(), "Assets/Scenes/MarketplaceBlockA.unity");
        Debug.Log("✅ Marketplace Block A scene created and saved successfully!");
    }

    static void CreateGround()
    {
        GameObject groundObj = new GameObject("Ground");
        groundObj.transform.position = new Vector3(10, 0, 10);

        // Create ground plane (20×20)
        MeshFilter mf = groundObj.AddComponent<MeshFilter>();
        MeshRenderer mr = groundObj.AddComponent<MeshRenderer>();
        
        // Simple quad for ground
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

        // Create material for ground (brown/dirt color)
        Material groundMat = new Material(Shader.Find("Standard"));
        groundMat.color = new Color(0.6f, 0.5f, 0.4f, 1f);
        mr.material = groundMat;

        // Add collider
        BoxCollider groundCollider = groundObj.AddComponent<BoxCollider>();
        groundCollider.size = new Vector3(20, 0.1f, 20);
        groundCollider.center = Vector3.zero;

        // Add rigidbody
        Rigidbody groundRb = groundObj.AddComponent<Rigidbody>();
        groundRb.isKinematic = true;
        groundRb.useGravity = false;
    }

    static void CreateLeftStallBarrier()
    {
        // Create 8 stalls along x=2, z=0→20
        float[] zPositions = { 1.5f, 4f, 6.5f, 9f, 11.5f, 14f, 16.5f, 19f };

        foreach (float z in zPositions)
        {
            CreateStall("LeftStall", new Vector3(2, 0.165f, z));
        }
    }

    static void CreateRightStallBarrier()
    {
        // Create 8 stalls along x=18, z=0→20
        float[] zPositions = { 1.5f, 4f, 6.5f, 9f, 11.5f, 14f, 16.5f, 19f };

        foreach (float z in zPositions)
        {
            CreateStall("RightStall", new Vector3(18, 0.165f, z));
        }
    }

    static void CreateStall(string name, Vector3 position)
    {
        GameObject stallObj = new GameObject(name);
        stallObj.transform.position = position;

        // Create visual mesh (simple cube for now)
        GameObject visual = GameObject.CreatePrimitive(PrimitiveType.Cube);
        visual.name = "Visual";
        visual.transform.SetParent(stallObj.transform);
        visual.transform.localPosition = Vector3.zero;
        // SCALE: Half the player's height (0.66 base × 0.5 = 0.33 on Y)
        visual.transform.localScale = new Vector3(0.66f, 0.33f, 0.66f);

        // Remove primitive collider
        Object.DestroyImmediate(visual.GetComponent<Collider>());

        // Create material (wooden stall color)
        Material stallMat = new Material(Shader.Find("Standard"));
        stallMat.color = new Color(0.7f, 0.6f, 0.4f, 1f);
        visual.GetComponent<MeshRenderer>().material = stallMat;

        // Add collider for blocking - scaled to match visual
        BoxCollider stallCollider = stallObj.AddComponent<BoxCollider>();
        stallCollider.size = new Vector3(0.66f, 0.33f, 0.66f);

        // Add rigidbody
        Rigidbody stallRb = stallObj.AddComponent<Rigidbody>();
        stallRb.isKinematic = true;
        stallRb.useGravity = false;
    }

    static void CreateLighting()
    {
        GameObject lightObj = new GameObject("DirectionalLight");
        Light light = lightObj.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.3f;
        light.color = new Color(1f, 0.95f, 0.7f); // Warm, dusty tone
        lightObj.transform.rotation = Quaternion.Euler(45, -30, 0);
    }

    static void CreateEventSystem()
    {
        GameObject esObj = new GameObject("EventSystem");
        esObj.AddComponent<EventSystem>();
        GraphicRaycaster raycaster = esObj.AddComponent<GraphicRaycaster>();
        StandaloneInputModule inputModule = esObj.AddComponent<StandaloneInputModule>();
    }

    static void CreateInteractionUI()
    {
        GameObject canvasObj = new GameObject("InteractionCanvas");
        Canvas canvas = canvasObj.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;

        CanvasScaler scaler = canvasObj.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;

        InteractionUI interactionUI = canvasObj.AddComponent<InteractionUI>();
    }

    static void CreateDialogueUI()
    {
        GameObject canvasObj = new GameObject("DialogueCanvas");
        Canvas canvas = canvasObj.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;

        CanvasScaler scaler = canvasObj.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;

        // Create dialogue panel
        GameObject panelObj = new GameObject("DialoguePanel");
        panelObj.transform.SetParent(canvasObj.transform);
        RectTransform panelRect = panelObj.AddComponent<RectTransform>();
        panelRect.anchoredPosition = new Vector2(0, -150);
        panelRect.sizeDelta = new Vector2(700, 200);

        // Panel background
        Image panelImage = panelObj.AddComponent<Image>();
        panelImage.color = new Color(0.1f, 0.1f, 0.15f, 0.95f);

        // Dialogue text
        GameObject textObj = new GameObject("DialogueText");
        textObj.transform.SetParent(panelObj.transform);
        RectTransform textRect = textObj.AddComponent<RectTransform>();
        textRect.anchoredPosition = new Vector2(-300, 80);
        textRect.sizeDelta = new Vector2(650, 150);

        TextMeshProUGUI dialogueText = textObj.AddComponent<TextMeshProUGUI>();
        dialogueText.text = "Dialogue text";
        dialogueText.fontSize = 32;
        dialogueText.color = Color.white;
        dialogueText.alignment = TextAlignmentOptions.TopLeft;

        // Button 1 (green)
        GameObject button1Obj = CreateDialogueButton("OptionButton1", panelObj.transform, new Vector2(-100, -60), Color.green);
        TextMeshProUGUI button1Text = button1Obj.GetComponentInChildren<TextMeshProUGUI>();
        button1Text.text = "Option 1";

        // Button 2 (red)
        GameObject button2Obj = CreateDialogueButton("OptionButton2", panelObj.transform, new Vector2(100, -60), new Color(1, 0, 0, 1));
        TextMeshProUGUI button2Text = button2Obj.GetComponentInChildren<TextMeshProUGUI>();
        button2Text.text = "Option 2";

        panelObj.SetActive(false);
    }

    static GameObject CreateDialogueButton(string name, Transform parent, Vector2 position, Color color)
    {
        GameObject buttonObj = new GameObject(name);
        buttonObj.transform.SetParent(parent);

        RectTransform buttonRect = buttonObj.AddComponent<RectTransform>();
        buttonRect.anchoredPosition = position;
        buttonRect.sizeDelta = new Vector2(150, 60);

        Image buttonImage = buttonObj.AddComponent<Image>();
        buttonImage.color = color;

        Button button = buttonObj.AddComponent<Button>();
        Navigation nav = button.navigation;
        nav.mode = Navigation.Mode.None;
        button.navigation = nav;

        // Add text to button
        GameObject textObj = new GameObject("Text");
        textObj.transform.SetParent(buttonObj.transform);
        RectTransform textRect = textObj.AddComponent<RectTransform>();
        textRect.anchoredPosition = Vector2.zero;
        textRect.sizeDelta = Vector2.zero;

        TextMeshProUGUI buttonText = textObj.AddComponent<TextMeshProUGUI>();
        buttonText.text = name;
        buttonText.fontSize = 28;
        buttonText.color = Color.white;
        buttonText.alignment = TextAlignmentOptions.Center;

        return buttonObj;
    }

    static void CreatePlayer()
    {
        GameObject playerObj = new GameObject("Player");
        playerObj.tag = "Player";
        playerObj.transform.position = new Vector3(10, 0.66f, 3);
        // SCALE: Reduce player by 1/3 for proper proportions
        playerObj.transform.localScale = new Vector3(0.66f, 0.66f, 0.66f);

        // Character controller - sized for scaled player
        CharacterController cc = playerObj.AddComponent<CharacterController>();
        cc.height = 1.32f;  // 2 × 0.66 scale
        cc.radius = 0.33f;  // 0.5 × 0.66 scale
        cc.center = new Vector3(0, -0.21f, 0);  // CRITICAL: Positions capsule bottom above ground
        cc.skinWidth = 0.08f;
        cc.stepOffset = 0.3f;
        cc.slopeLimit = 45f;

        // Add player script
        playerObj.AddComponent<SimplePlayerMovement>();

        // Add visual (blue cylinder)
        GameObject visualObj = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        visualObj.name = "Visual";
        visualObj.transform.SetParent(playerObj.transform);
        visualObj.transform.localPosition = Vector3.zero;
        visualObj.transform.localScale = new Vector3(1, 1, 1);  // Already scaled via parent

        // Remove primitive collider
        Object.DestroyImmediate(visualObj.GetComponent<Collider>());

        // Create blue material
        Material playerMat = new Material(Shader.Find("Standard"));
        playerMat.color = new Color(0.2f, 0.5f, 1f, 1f);
        visualObj.GetComponent<MeshRenderer>().material = playerMat;

        // Interaction trigger collider
        CapsuleCollider triggerCollider = playerObj.AddComponent<CapsuleCollider>();
        triggerCollider.isTrigger = true;
        triggerCollider.radius = 0.33f;  // 0.5 × 0.66 scale
        triggerCollider.height = 1.32f;  // 2 × 0.66 scale
        triggerCollider.center = new Vector3(0, 0.66f, 0);  // 1 × 0.66 scale

        // Camera as child
        GameObject cameraObj = new GameObject("MainCamera");
        cameraObj.tag = "MainCamera";
        cameraObj.transform.SetParent(playerObj.transform);
        cameraObj.transform.localPosition = new Vector3(0, 0.79f, -1.65f);  // Scaled position (1.2 × 0.66, -2.5 × 0.66)

        Camera cam = cameraObj.AddComponent<Camera>();
        cam.clearFlags = CameraClearFlags.Skybox;
        // Note: AudioListener already exists in default scene setup - do not add another
    }

    static void CreateNPCs()
    {
        Vector3[] npcPositions = new Vector3[]
        {
            new Vector3(10, 0.66f, 8),
            new Vector3(7, 0.66f, 10),
            new Vector3(13, 0.66f, 10),
            new Vector3(10, 0.66f, 13),
            new Vector3(10, 0.66f, 16)
        };

        string[] npcNames = { "Merchant", "Blacksmith", "Healer", "Bard", "Sage" };

        for (int i = 0; i < npcPositions.Length; i++)
        {
            CreateNPC(npcPositions[i], npcNames[i]);
        }
    }

    static void CreateNPC(Vector3 position, string npcName)
    {
        GameObject npcObj = new GameObject($"NPC_{npcName}");
        npcObj.transform.position = position;
        // SCALE: Match player height (0.66)
        npcObj.transform.localScale = new Vector3(0.66f, 0.66f, 0.66f);

        // Visual (purple capsule)
        GameObject visualObj = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        visualObj.name = "Visual";
        visualObj.transform.SetParent(npcObj.transform);
        visualObj.transform.localPosition = Vector3.zero;
        visualObj.transform.localScale = new Vector3(1, 1, 1);  // Already scaled via parent

        // Remove primitive collider
        Object.DestroyImmediate(visualObj.GetComponent<Collider>());

        // Create purple material
        Material npcMat = new Material(Shader.Find("Standard"));
        npcMat.color = new Color(0.7f, 0.3f, 0.9f, 1f);
        visualObj.GetComponent<MeshRenderer>().material = npcMat;

        // Solid collider (blocks movement) - SCALED FOR PLAYER SIZE
        CapsuleCollider solidCollider = npcObj.AddComponent<CapsuleCollider>();
        solidCollider.isTrigger = false;
        solidCollider.radius = 0.25f;   // 0.5 × 0.5 (0.5 base scaled)
        solidCollider.height = 1.8f;    // Scaled appropriately
        solidCollider.center = new Vector3(0, 0.9f, 0);

        // Trigger collider (detects interaction)
        GameObject triggerObj = new GameObject("InteractionTrigger");
        triggerObj.transform.SetParent(npcObj.transform);
        triggerObj.transform.localPosition = Vector3.zero;

        CapsuleCollider triggerCollider = triggerObj.AddComponent<CapsuleCollider>();
        triggerCollider.isTrigger = true;
        triggerCollider.radius = 0.5f;  // Larger radius for interaction range
        triggerCollider.height = 1.8f;
        triggerCollider.center = new Vector3(0, 0.9f, 0);

        // Rigidbody
        Rigidbody rb = npcObj.AddComponent<Rigidbody>();
        rb.isKinematic = true;
        rb.useGravity = false;

        // NPC interaction script
        NPCInteraction npcInteraction = npcObj.AddComponent<NPCInteraction>();
        Debug.Log($"✅ Added NPCInteraction to {npcName}");
        npcInteraction.npcName = npcName;
        
        // Set per-NPC dialogue content
        SetNPCDialogue(npcInteraction, npcName);

        // Find dialogue canvas by name
        Canvas[] canvases = Object.FindObjectsByType<Canvas>();
        Canvas dialogueCanvas = null;
        foreach (Canvas c in canvases)
        {
            if (c.name == "DialogueCanvas")
            {
                dialogueCanvas = c;
                break;
            }
        }
        if (dialogueCanvas != null)
            npcInteraction.dialogueCanvas = dialogueCanvas;

        // Find dialogue text specifically (DialoguePanel -> DialogueText)
        if (dialogueCanvas != null)
        {
            Transform panelTransform = dialogueCanvas.transform.Find("DialoguePanel");
            if (panelTransform != null)
            {
                Transform textTransform = panelTransform.Find("DialogueText");
                if (textTransform != null)
                {
                    TextMeshProUGUI dialogueText = textTransform.GetComponent<TextMeshProUGUI>();
                    npcInteraction.dialogueText = dialogueText;
                }
            }
        }

        // Find buttons by searching under DialoguePanel
        if (dialogueCanvas != null)
        {
            Transform panelTransform = dialogueCanvas.transform.Find("DialoguePanel");
            if (panelTransform != null)
            {
                Button[] buttons = panelTransform.GetComponentsInChildren<Button>();
                foreach (Button btn in buttons)
                {
                    if (btn.name == "OptionButton1")
                        npcInteraction.optionButton1 = btn.gameObject;
                    else if (btn.name == "OptionButton2")
                        npcInteraction.optionButton2 = btn.gameObject;
                }
            }
        }
    }

    static void CreateGlyph()
    {
        GameObject glyphObj = new GameObject("Glyph");
        glyphObj.transform.position = new Vector3(10, 0.5f, 6);

        // Visual (cyan sphere)
        GameObject visualObj = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        visualObj.name = "Visual";
        visualObj.transform.SetParent(glyphObj.transform);
        visualObj.transform.localPosition = Vector3.zero;
        visualObj.transform.localScale = new Vector3(0.67f, 0.67f, 0.67f);

        // Remove primitive collider
        Object.DestroyImmediate(visualObj.GetComponent<Collider>());

        // Create glowing cyan material
        Material glyphMat = new Material(Shader.Find("Standard"));
        glyphMat.color = new Color(0, 0.9f, 1f, 1f);
        glyphMat.SetFloat("_Glossiness", 0.8f);
        visualObj.GetComponent<MeshRenderer>().material = glyphMat;

        // PHYSICAL COLLIDER (blocks movement)
        SphereCollider physicalCollider = glyphObj.AddComponent<SphereCollider>();
        physicalCollider.isTrigger = false;
        physicalCollider.radius = 0.3f;

        // INTERACTION TRIGGER (larger range for detection)
        SphereCollider triggerCollider = glyphObj.AddComponent<SphereCollider>();
        triggerCollider.isTrigger = true;
        triggerCollider.radius = 1.0f;

        // Glyph script
        GlyphObject glyphScript = glyphObj.AddComponent<GlyphObject>();
    }

    static void CreateExitTrigger()
    {
        GameObject exitObj = new GameObject("ExitTrigger_BlockB");
        exitObj.transform.position = new Vector3(10, 1, 20);

        // Large trigger area for exit
        BoxCollider exitCollider = exitObj.AddComponent<BoxCollider>();
        exitCollider.isTrigger = true;
        exitCollider.size = new Vector3(6, 3, 1);
        exitCollider.center = Vector3.zero;

        // Visual indicator (semi-transparent plane)
        GameObject visualObj = GameObject.CreatePrimitive(PrimitiveType.Cube);
        visualObj.name = "Visual";
        visualObj.transform.SetParent(exitObj.transform);
        visualObj.transform.localPosition = Vector3.zero;
        visualObj.transform.localScale = new Vector3(6, 3, 0.5f);

        // Remove primitive collider
        Object.DestroyImmediate(visualObj.GetComponent<Collider>());

        // Create semi-transparent material
        Material exitMat = new Material(Shader.Find("Standard"));
        exitMat.color = new Color(1, 1, 0, 0.3f);
        visualObj.GetComponent<MeshRenderer>().material = exitMat;
    }

    static void CreateBackBarrier()
    {
        GameObject barrierObj = new GameObject("BackBarrier");
        barrierObj.transform.position = new Vector3(10, 2.5f, 0);

        // Invisible wall to prevent falling off back edge
        BoxCollider barrierCollider = barrierObj.AddComponent<BoxCollider>();
        barrierCollider.isTrigger = false;
        barrierCollider.size = new Vector3(50, 5, 1);

        // Rigidbody
        Rigidbody rb = barrierObj.AddComponent<Rigidbody>();
        rb.isKinematic = true;
        rb.useGravity = false;

        Debug.Log("✅ Back barrier created - player cannot fall off back edge");
    }

    static void SetNPCDialogue(NPCInteraction npc, string npcName)
    {
        // Set unique dialogue for each NPC
        switch (npcName)
        {
            case "Merchant":
                npc.npcDialogueLines = new string[]
                {
                    "Welcome to my stall!",
                    "I have the finest wares in the marketplace.",
                    "Would you like to see what I'm selling?"
                };
                npc.npcOptions = new string[] { "Show me your wares", "Not interested" };
                break;

            case "Blacksmith":
                npc.npcDialogueLines = new string[]
                {
                    "The name's Blacksmith.",
                    "I forge the strongest weapons this side of Velinor.",
                    "Bring me rare materials and I'll craft something special."
                };
                npc.npcOptions = new string[] { "Tell me about your craft", "Goodbye" };
                break;

            case "Healer":
                npc.npcDialogueLines = new string[]
                {
                    "Greetings, traveler.",
                    "I mend both wounds and spirits.",
                    "Seek my aid whenever you are troubled."
                };
                npc.npcOptions = new string[] { "I need healing", "I'm fine" };
                break;

            case "Bard":
                npc.npcDialogueLines = new string[]
                {
                    "Ah, a new face in the marketplace!",
                    "I compose tales of adventure and mystery.",
                    "Perhaps I shall write a song about you?"
                };
                npc.npcOptions = new string[] { "Tell me a story", "No thanks" };
                break;

            case "Sage":
                npc.npcDialogueLines = new string[]
                {
                    "Welcome, seeker of knowledge.",
                    "I have studied the ancient ways of Velinor.",
                    "What questions trouble your mind?"
                };
                npc.npcOptions = new string[] { "Teach me something", "I'll be on my way" };
                break;

            default:
                // Generic dialogue if NPC name doesn't match
                npc.npcDialogueLines = new string[]
                {
                    "Hello there.",
                    "What brings you to the marketplace?"
                };
                npc.npcOptions = new string[] { "Just looking around", "Goodbye" };
                break;
        }
    }
}
