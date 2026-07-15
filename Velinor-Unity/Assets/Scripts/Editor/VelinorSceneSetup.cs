using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using StarterAssets;

public class VelinorSceneSetup
{
    [MenuItem("Velinor/Setup Quick Start Scene")]
    public static void SetupQuickStartScene()
    {
        // Create or open TestScene
        Scene scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
        EditorSceneManager.SaveScene(scene, "Assets/Scenes/TestScene.unity");

        // Get the scene's root
        GameObject[] roots = scene.GetRootGameObjects();
        Camera mainCamera = null;
        foreach (GameObject root in roots)
        {
            if (root.name == "Main Camera")
            {
                mainCamera = root.GetComponent<Camera>();
                break;
            }
        }

        if (mainCamera == null)
        {
            Debug.LogError("Main Camera not found in scene!");
            return;
        }

        // ===== STEP 1: Create Ground Plane =====
        GameObject plane = GameObject.CreatePrimitive(PrimitiveType.Plane);
        plane.name = "Plane";
        plane.transform.position = Vector3.zero;
        plane.transform.localScale = new Vector3(20, 1, 20);

        // Remove the collider that comes with primitive
        Object.DestroyImmediate(plane.GetComponent<Collider>());

        // Add box collider as solid ground
        BoxCollider groundCollider = plane.AddComponent<BoxCollider>();
        groundCollider.isTrigger = false;

        // ===== STEP 2: Create Player =====
        GameObject player = new GameObject("Player");
        player.transform.position = Vector3.zero;
        player.tag = "Player";

        // Add CharacterController
        CharacterController cc = player.AddComponent<CharacterController>();
        cc.height = 2f;
        cc.radius = 0.4f;
        cc.center = new Vector3(0, 1, 0);

        // Add StarterAssetsInputs
        StarterAssetsInputs inputs = player.AddComponent<StarterAssetsInputs>();
        inputs.analogMovement = false;

        // Add VelinorPlayerController
        VelinorPlayerController playerController = player.AddComponent<VelinorPlayerController>();
        playerController.MoveSpeed = 2f;
        playerController.GroundLayers = LayerMask.GetMask("Default");
        playerController.GroundedOffset = -0.5f;  // More aggressive ground detection
        playerController.GroundedRadius = 0.2f;

        // Create visual cube as child
        GameObject playerCube = GameObject.CreatePrimitive(PrimitiveType.Cube);
        playerCube.name = "PlayerVisual";
        playerCube.transform.SetParent(player.transform);
        playerCube.transform.localPosition = new Vector3(0, 0.5f, 0);
        playerCube.transform.localScale = new Vector3(0.4f, 1, 0.4f);

        // Remove collider from visual cube
        Object.DestroyImmediate(playerCube.GetComponent<Collider>());

        // ===== STEP 3: Setup Camera =====
        mainCamera.transform.position = new Vector3(0, 1, 0);
        mainCamera.gameObject.tag = "MainCamera";

        // Create CinemachineCameraTarget as child of Player
        GameObject cameraTarget = new GameObject("CinemachineCameraTarget");
        cameraTarget.transform.SetParent(player.transform);
        cameraTarget.transform.localPosition = new Vector3(0, 0.6f, 0);
        cameraTarget.transform.localRotation = Quaternion.identity;

        // Note: VelinorPlayerController manages camera internally in first-person mode

        // ===== STEP 4: Create CodexManager (MUST BE FIRST before NPC/Pedestal) =====
        GameObject codexManager = new GameObject("CodexManager");
        codexManager.AddComponent<Velinor.Core.CodexManager>();

        // ===== STEP 5: Create DialogueManager (MUST BE BEFORE NPC) =====
        GameObject dialogueManager = new GameObject("DialogueManager");
        Velinor.Core.DialogueManager dm = dialogueManager.AddComponent<Velinor.Core.DialogueManager>();

        // Create DialoguePanel (UI Panel)
        GameObject canvasGO = new GameObject("Canvas");
        canvasGO.transform.SetParent(dialogueManager.transform);
        Canvas canvas = canvasGO.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        CanvasScaler scaler = canvasGO.AddComponent<CanvasScaler>();

        GameObject dialoguePanel = new GameObject("DialoguePanel");
        dialoguePanel.transform.SetParent(canvasGO.transform);
        RectTransform panelRect = dialoguePanel.AddComponent<RectTransform>();
        panelRect.anchorMin = new Vector2(0, 0);
        panelRect.anchorMax = new Vector2(1, 0.3f);
        panelRect.offsetMin = Vector2.zero;
        panelRect.offsetMax = Vector2.zero;

        Image panelImage = dialoguePanel.AddComponent<Image>();
        panelImage.color = new Color(0, 0, 0, 0.8f);

        // Create SpeakerName text
        GameObject speakerNameGO = new GameObject("SpeakerName");
        speakerNameGO.transform.SetParent(dialoguePanel.transform);
        RectTransform speakerRect = speakerNameGO.AddComponent<RectTransform>();
        speakerRect.anchorMin = new Vector2(0.1f, 0.7f);
        speakerRect.anchorMax = new Vector2(0.9f, 1);
        speakerRect.offsetMin = Vector2.zero;
        speakerRect.offsetMax = Vector2.zero;

        TMPro.TextMeshProUGUI speakerText = speakerNameGO.AddComponent<TMPro.TextMeshProUGUI>();
        speakerText.text = "Speaker";
        speakerText.fontSize = 36;
        speakerText.alignment = TMPro.TextAlignmentOptions.TopLeft;

        // Create DialogueText
        GameObject dialogueTextGO = new GameObject("DialogueText");
        dialogueTextGO.transform.SetParent(dialoguePanel.transform);
        RectTransform dialogueRect = dialogueTextGO.AddComponent<RectTransform>();
        dialogueRect.anchorMin = new Vector2(0.1f, 0.1f);
        dialogueRect.anchorMax = new Vector2(0.9f, 0.7f);
        dialogueRect.offsetMin = Vector2.zero;
        dialogueRect.offsetMax = Vector2.zero;

        TMPro.TextMeshProUGUI dialogueText = dialogueTextGO.AddComponent<TMPro.TextMeshProUGUI>();
        dialogueText.text = "Dialogue text appears here...";
        dialogueText.fontSize = 28;
        dialogueText.alignment = TMPro.TextAlignmentOptions.TopLeft;

        // Create ChoicesContainer
        GameObject choicesContainer = new GameObject("ChoicesContainer");
        choicesContainer.transform.SetParent(dialoguePanel.transform);
        RectTransform choicesRect = choicesContainer.AddComponent<RectTransform>();
        choicesRect.anchorMin = Vector2.zero;
        choicesRect.anchorMax = Vector2.one;
        choicesRect.offsetMin = Vector2.zero;
        choicesRect.offsetMax = Vector2.zero;

        // Assign UI references to DialogueManager
        dm.dialogueUIPanel = dialoguePanel;
        dm.speakerNameText = speakerText;
        dm.dialogueText = dialogueText;
        dm.choicesContainer = choicesContainer.transform;

        // ===== STEP 6: Create NPC_Tala (now managers exist) =====
        GameObject npc = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        npc.name = "NPC_Tala";
        npc.transform.position = new Vector3(1.5f, 0.5f, 1.5f);  // Very close to player
        npc.transform.localScale = new Vector3(0.3f, 0.8f, 0.3f);  // Much smaller

        // Remove primitive collider
        Object.DestroyImmediate(npc.GetComponent<Collider>());

        // Add box collider as trigger
        BoxCollider npcCollider = npc.AddComponent<BoxCollider>();
        npcCollider.isTrigger = true;

        // Make NPC HOT PINK (unmistakable)
        Renderer npcRenderer = npc.GetComponent<Renderer>();
        Material npcMat = new Material(Shader.Find("Standard"));
        npcMat.color = new Color(1f, 0.1f, 0.8f, 1f);  // Hot pink
        npcRenderer.material = npcMat;

        // Add SimpleNPC script
        SimpleNPC simpleNpc = npc.AddComponent<SimpleNPC>();
        // Configure npcId and startingPassageId in the Inspector or via SerializedProperty

        // ===== STEP 7: Create Pedestal =====
        GameObject pedestal = GameObject.CreatePrimitive(PrimitiveType.Cube);
        pedestal.name = "Pedestal";
        pedestal.transform.position = new Vector3(-1.5f, 0.5f, 1.5f);  // Very close, opposite side
        pedestal.transform.localScale = new Vector3(0.6f, 1f, 0.6f);  // Much smaller

        // Remove primitive collider
        Object.DestroyImmediate(pedestal.GetComponent<Collider>());

        // Make Pedestal CYAN (bright and obvious)
        Renderer pedestalRenderer = pedestal.GetComponent<Renderer>();
        Material pedestalMat = new Material(Shader.Find("Standard"));
        pedestalMat.color = new Color(0.1f, 1f, 1f, 1f);  // Bright cyan
        pedestalRenderer.material = pedestalMat;

        // Add box collider
        BoxCollider pedestalCollider = pedestal.AddComponent<BoxCollider>();
        pedestalCollider.isTrigger = false;

        // Add Pedestal script
        Velinor.Core.Pedestal pedestalScript = pedestal.AddComponent<Velinor.Core.Pedestal>();
        pedestalScript.pedestalId = "pedestal_test_001";
        pedestalScript.linkedGlyphId = "glyph_test_001";
        pedestalScript.requiredTags = new System.Collections.Generic.List<string> { "Grief" };
        pedestalScript.activationRadius = 5f;

        // Add Light component
        Light light = pedestal.AddComponent<Light>();
        light.type = LightType.Point;
        light.range = 10f;
        light.intensity = 0.5f;

        pedestalScript.pedestalLight = light;

        // Add Particle System
        ParticleSystem ps = pedestal.AddComponent<ParticleSystem>();
        pedestalScript.activationParticles = ps;

        // ===== Save Scene =====
        EditorSceneManager.SaveScene(scene);
        EditorSceneManager.OpenScene("Assets/Scenes/TestScene.unity", OpenSceneMode.Single);

        Debug.Log("✅ Quick Start scene setup complete!");
        Debug.Log("🎮 NPC_Tala is at position (2, 0, 2) - walk forward-right and press E");
        Debug.Log("🔮 Pedestal is at position (-2, 0, 2) - walk forward-left");
        Debug.Log("Scene saved to: Assets/Scenes/TestScene.unity");
    }
}
