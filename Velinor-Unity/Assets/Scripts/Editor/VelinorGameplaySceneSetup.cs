using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using StarterAssets;

public class VelinorGameplaySceneSetup
{
    [MenuItem("Velinor/Setup Gameplay Scene")]
    public static void SetupGameplayScene()
    {
        // Open GamplayScene
        Scene scene = EditorSceneManager.OpenScene("Assets/Scenes/GamplayScene.unity", OpenSceneMode.Single);
        
        // Clean up existing objects to prevent duplicates
        GameObject[] existingObjects = scene.GetRootGameObjects();
        foreach (GameObject obj in existingObjects)
        {
            if (obj.name == "Player" || obj.name == "Ground" || obj.name == "NPC_Tala" || obj.name == "Pedestal" || obj.name == "PromptCanvas")
            {
                Object.DestroyImmediate(obj);
                Debug.Log($"Cleaned up existing {obj.name}");
            }
        }
        
        // Get or create Main Camera
        GameObject cameraObj = GameObject.Find("Main Camera");
        if (cameraObj == null)
        {
            cameraObj = new GameObject("Main Camera");
            cameraObj.tag = "MainCamera";
            cameraObj.AddComponent<Camera>();
            cameraObj.AddComponent<AudioListener>();
        }

        // ===== STEP 1: Create Ground Plane =====
        GameObject plane = GameObject.CreatePrimitive(PrimitiveType.Plane);
        plane.name = "Ground";
        plane.transform.position = Vector3.zero;
        plane.transform.localScale = new Vector3(20, 1, 20);
        
        Object.DestroyImmediate(plane.GetComponent<Collider>());
        BoxCollider groundCollider = plane.AddComponent<BoxCollider>();
        groundCollider.isTrigger = false;

        // ===== STEP 2: Create Player =====
        GameObject player = new GameObject("Player");
        player.transform.position = new Vector3(0, 0, 0);
        player.tag = "Player";

        // CharacterController (like tutorial)
        CharacterController cc = player.AddComponent<CharacterController>();
        cc.height = 1.8f;
        cc.radius = 0.28f;
        cc.center = new Vector3(0, 0.93f, 0);
        cc.slopeLimit = 45f;
        cc.stepOffset = 0.25f;

        // Capsule collider for interaction detection
        CapsuleCollider capCollider = player.AddComponent<CapsuleCollider>();
        capCollider.height = 1.84f;
        capCollider.radius = 0.25f;

        // Input handling
        StarterAssetsInputs inputs = player.AddComponent<StarterAssetsInputs>();
        inputs.analogMovement = false;

        // Movement controller
        VelinorPlayerController playerController = player.AddComponent<VelinorPlayerController>();
        playerController.MoveSpeed = 2f;
        playerController.GroundLayers = LayerMask.GetMask("Default");
        playerController.GroundedOffset = -0.5f;
        playerController.GroundedRadius = 0.2f;

        // Visual representation (white cube)
        GameObject playerVisual = GameObject.CreatePrimitive(PrimitiveType.Cube);
        playerVisual.name = "Visual";
        playerVisual.transform.SetParent(player.transform);
        playerVisual.transform.localPosition = new Vector3(0, 0.5f, 0);
        playerVisual.transform.localScale = new Vector3(0.4f, 1f, 0.4f);
        Object.DestroyImmediate(playerVisual.GetComponent<Collider>());
        
        Renderer visualRenderer = playerVisual.GetComponent<Renderer>();
        Material visualMat = new Material(Shader.Find("Standard"));
        visualMat.color = Color.white;
        visualRenderer.material = visualMat;

        // ===== STEP 3: Setup Camera with Cinemachine-like positioning =====
        cameraObj.transform.position = new Vector3(2f, 2f, -3f);
        cameraObj.transform.rotation = Quaternion.Euler(20f, 0f, 0f);
        
        // Create camera target (what camera looks at)
        GameObject cameraTarget = new GameObject("CameraTarget");
        cameraTarget.transform.SetParent(player.transform);
        cameraTarget.transform.localPosition = new Vector3(0, 0.93f, 0);
        playerController.CinemachineCameraTarget = cameraTarget;

        // ===== STEP 4: Create Managers =====
        GameObject codexManager = new GameObject("CodexManager");
        codexManager.AddComponent<Velinor.Core.CodexManager>();

        // ===== STEP 5: Create UI Canvas for prompts =====
        GameObject canvasGO = new GameObject("PromptCanvas");
        Canvas canvas = canvasGO.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        
        CanvasScaler scaler = canvasGO.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920, 1080);

        // Create prompt text
        GameObject promptTextGO = new GameObject("PromptText");
        promptTextGO.transform.SetParent(canvasGO.transform);
        RectTransform promptRect = promptTextGO.AddComponent<RectTransform>();
        promptRect.anchorMin = new Vector2(0.5f, 0.1f);
        promptRect.anchorMax = new Vector2(0.5f, 0.1f);
        promptRect.offsetMin = Vector2.zero;
        promptRect.offsetMax = Vector2.zero;
        promptRect.sizeDelta = new Vector2(400, 100);

        TMPro.TextMeshProUGUI promptText = promptTextGO.AddComponent<TMPro.TextMeshProUGUI>();
        promptText.text = "";
        promptText.fontSize = 36;
        promptText.alignment = TMPro.TextAlignmentOptions.Center;
        promptText.color = Color.yellow;

        // Add InteractionPrompt script
        InteractionPrompt promptScript = canvasGO.AddComponent<InteractionPrompt>();

        // ===== STEP 6: Create DialogueManager =====
        GameObject dialogueManagerGO = new GameObject("DialogueManager");
        Velinor.Core.DialogueManager dm = dialogueManagerGO.AddComponent<Velinor.Core.DialogueManager>();

        // Create dialogue UI
        GameObject dialogueCanvasGO = new GameObject("DialogueCanvas");
        dialogueCanvasGO.transform.SetParent(dialogueManagerGO.transform);
        Canvas dialogueCanvas = dialogueCanvasGO.AddComponent<Canvas>();
        dialogueCanvas.renderMode = RenderMode.ScreenSpaceOverlay;
        
        CanvasScaler dialogueScaler = dialogueCanvasGO.AddComponent<CanvasScaler>();
        dialogueScaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;

        GameObject dialoguePanel = new GameObject("DialoguePanel");
        dialoguePanel.transform.SetParent(dialogueCanvasGO.transform);
        RectTransform panelRect = dialoguePanel.AddComponent<RectTransform>();
        panelRect.anchorMin = new Vector2(0, 0);
        panelRect.anchorMax = new Vector2(1, 0.3f);
        panelRect.offsetMin = Vector2.zero;
        panelRect.offsetMax = Vector2.zero;

        Image panelImage = dialoguePanel.AddComponent<Image>();
        panelImage.color = new Color(0, 0, 0, 0.8f);

        // Speaker name
        GameObject speakerGO = new GameObject("SpeakerName");
        speakerGO.transform.SetParent(dialoguePanel.transform);
        RectTransform speakerRect = speakerGO.AddComponent<RectTransform>();
        speakerRect.anchorMin = new Vector2(0.1f, 0.7f);
        speakerRect.anchorMax = new Vector2(0.9f, 1);
        speakerRect.offsetMin = Vector2.zero;
        speakerRect.offsetMax = Vector2.zero;

        TMPro.TextMeshProUGUI speakerText = speakerGO.AddComponent<TMPro.TextMeshProUGUI>();
        speakerText.text = "Speaker";
        speakerText.fontSize = 36;
        speakerText.alignment = TMPro.TextAlignmentOptions.TopLeft;

        // Dialogue text
        GameObject dialogueTextGO = new GameObject("DialogueText");
        dialogueTextGO.transform.SetParent(dialoguePanel.transform);
        RectTransform dialogueTextRect = dialogueTextGO.AddComponent<RectTransform>();
        dialogueTextRect.anchorMin = new Vector2(0.1f, 0.1f);
        dialogueTextRect.anchorMax = new Vector2(0.9f, 0.7f);
        dialogueTextRect.offsetMin = Vector2.zero;
        dialogueTextRect.offsetMax = Vector2.zero;

        TMPro.TextMeshProUGUI dialogueText = dialogueTextGO.AddComponent<TMPro.TextMeshProUGUI>();
        dialogueText.text = "Dialogue text appears here...";
        dialogueText.fontSize = 28;
        dialogueText.alignment = TMPro.TextAlignmentOptions.TopLeft;

        // Choices container
        GameObject choicesGO = new GameObject("ChoicesContainer");
        choicesGO.transform.SetParent(dialoguePanel.transform);
        RectTransform choicesRect = choicesGO.AddComponent<RectTransform>();
        choicesRect.anchorMin = Vector2.zero;
        choicesRect.anchorMax = Vector2.one;
        choicesRect.offsetMin = Vector2.zero;
        choicesRect.offsetMax = Vector2.zero;

        // Assign dialogue UI references
        dm.dialogueUIPanel = dialoguePanel;
        dm.speakerNameText = speakerText;
        dm.dialogueText = dialogueText;
        dm.choicesContainer = choicesGO.transform;

        // ===== STEP 7: Create NPC_Tala (6 units away) =====
        GameObject npc = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        npc.name = "NPC_Tala";
        npc.transform.position = new Vector3(5f, 0.5f, 5f);  // 6.7 units from origin
        npc.transform.localScale = new Vector3(0.5f, 1.2f, 0.5f);

        Object.DestroyImmediate(npc.GetComponent<Collider>());
        
        // Interaction trigger
        SphereCollider npcTrigger = npc.AddComponent<SphereCollider>();
        npcTrigger.radius = 1.5f;
        npcTrigger.isTrigger = true;

        // Visual: hot pink
        Renderer npcRenderer = npc.GetComponent<Renderer>();
        Material npcMat = new Material(Shader.Find("Standard"));
        npcMat.color = new Color(1f, 0.1f, 0.8f, 1f);
        npcRenderer.material = npcMat;

        // Interaction script
        InteractionZone npcZone = npc.AddComponent<InteractionZone>();

        // NPC dialogue
        SimpleNPC simpleNpc = npc.AddComponent<SimpleNPC>();
        simpleNpc.npcName = "Tala";

        // Add bobbing animation
        AddBobbingAnimation(npc);

        // ===== STEP 8: Create Pedestal (8 units away, opposite side) =====
        GameObject pedestal = GameObject.CreatePrimitive(PrimitiveType.Cube);
        pedestal.name = "Pedestal";
        pedestal.transform.position = new Vector3(-5f, 0.5f, 5f);
        pedestal.transform.localScale = new Vector3(0.8f, 1.2f, 0.8f);

        Object.DestroyImmediate(pedestal.GetComponent<Collider>());
        
        // Interaction trigger
        SphereCollider pedestalTrigger = pedestal.AddComponent<SphereCollider>();
        pedestalTrigger.radius = 1.5f;
        pedestalTrigger.isTrigger = true;

        // Visual: bright cyan
        Renderer pedestalRenderer = pedestal.GetComponent<Renderer>();
        Material pedestalMat = new Material(Shader.Find("Standard"));
        pedestalMat.color = new Color(0.1f, 1f, 1f, 1f);
        pedestalRenderer.material = pedestalMat;

        // Interaction script
        InteractionZone pedestalZone = pedestal.AddComponent<InteractionZone>();

        // Pedestal logic
        Velinor.Core.Pedestal pedestalScript = pedestal.AddComponent<Velinor.Core.Pedestal>();
        pedestalScript.pedestalId = "pedestal_test_001";
        pedestalScript.linkedGlyphId = "glyph_test_001";
        pedestalScript.requiredTags = new System.Collections.Generic.List<string> { "Grief" };
        pedestalScript.activationRadius = 5f;

        // Light
        Light light = pedestal.AddComponent<Light>();
        light.type = LightType.Point;
        light.range = 5f;
        light.intensity = 0.5f;
        pedestalScript.pedestalLight = light;

        // Particle system
        ParticleSystem ps = pedestal.AddComponent<ParticleSystem>();
        pedestalScript.activationParticles = ps;

        // Add bobbing animation
        AddBobbingAnimation(pedestal);

        // ===== Save Scene =====
        EditorSceneManager.SaveScene(scene);
        Debug.Log("✅ Gameplay Scene setup complete!");
        Debug.Log("🎮 NPC_Tala: Position (5, 0.5, 5) - HOT PINK cylinder");
        Debug.Log("🔮 Pedestal: Position (-5, 0.5, 5) - CYAN cube");
        Debug.Log("Walk close and press E to interact!");
    }

    static void AddBobbingAnimation(GameObject obj)
    {
        // Simple bobbing via a coroutine-like effect using animation
        // For now, just add a note - could extend with actual animation
        var bobbingComponent = obj.AddComponent<BobbingAnimation>();
        bobbingComponent.bobbingAmount = 0.1f;
        bobbingComponent.bobbingSpeed = 1f;
    }
}

/// <summary>
/// Simple bobbing animation for interactive objects.
/// </summary>
public class BobbingAnimation : MonoBehaviour
{
    public float bobbingAmount = 0.1f;
    public float bobbingSpeed = 1f;
    private Vector3 startPos;

    private void Start()
    {
        startPos = transform.position;
    }

    private void Update()
    {
        float newY = startPos.y + Mathf.Sin(Time.time * bobbingSpeed * Mathf.PI) * bobbingAmount;
        transform.position = new Vector3(startPos.x, newY, startPos.z);
    }
}
