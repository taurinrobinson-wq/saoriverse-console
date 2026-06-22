using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

public class VelinorGameplaySetup
{
    [MenuItem("Velinor/Setup Gameplay Scene (Third Person)")]
    public static void SetupGameplayScene()
    {
        // Open GamplayScene
        Scene scene = EditorSceneManager.OpenScene("Assets/Scenes/GamplayScene.unity", OpenSceneMode.Single);

        // Clean up existing objects
        GameObject[] existingObjects = scene.GetRootGameObjects();
        foreach (GameObject obj in existingObjects)
        {
            if (obj.name == "Player" || obj.name == "Ground" || obj.name == "PlayerCamera" || 
                obj.name == "UICanvas" || obj.name == "Saori")
            {
                Object.DestroyImmediate(obj);
                Debug.Log($"✓ Cleaned up {obj.name}");
            }
        }

        // ===== STEP 1: Create Ground =====
        GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = "Ground";
        ground.transform.localScale = new Vector3(20, 1, 20);
        ground.transform.position = Vector3.zero;

        // Material for ground
        Renderer groundRenderer = ground.GetComponent<Renderer>();
        Material groundMat = new Material(Shader.Find("Standard"));
        groundMat.color = new Color(0.8f, 0.7f, 0.5f, 1f); // Tan/brown for ruins
        groundRenderer.material = groundMat;

        Object.DestroyImmediate(ground.GetComponent<Collider>());
        BoxCollider groundCollider = ground.AddComponent<BoxCollider>();
        groundCollider.size = new Vector3(20, 0.1f, 20);

        // ===== STEP 2: Set up Player with StarterAssets ThirdPersonController =====
        GameObject player = new GameObject("Player");
        player.tag = "Player";
        player.transform.position = new Vector3(0, 1f, 0);

        // Add CharacterController (required by ThirdPersonController)
        CharacterController charController = player.AddComponent<CharacterController>();
        charController.height = 1.8f;
        charController.radius = 0.5f;
        charController.center = new Vector3(0, 0.9f, 0);

        // Add ThirdPersonController script
        StarterAssets.ThirdPersonController thirdPersonController = player.AddComponent<StarterAssets.ThirdPersonController>();
        thirdPersonController.MoveSpeed = 3f;
        thirdPersonController.SprintSpeed = 5.5f;
        thirdPersonController.RotationSmoothTime = 0.12f;
        thirdPersonController.SpeedChangeRate = 10f;
        thirdPersonController.JumpHeight = 1.2f;
        thirdPersonController.Gravity = -15f;
        thirdPersonController.GroundedOffset = -0.14f;
        thirdPersonController.GroundedRadius = 0.5f;
        thirdPersonController.GroundLayers = LayerMask.GetMask("Default");
        thirdPersonController.TopClamp = 70f;
        thirdPersonController.BottomClamp = -30f;

        // Create simple capsule for player visual
        GameObject playerVisual = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        playerVisual.name = "PlayerVisual";
        playerVisual.transform.SetParent(player.transform);
        playerVisual.transform.localPosition = Vector3.zero;
        playerVisual.transform.localScale = Vector3.one;

        Object.DestroyImmediate(playerVisual.GetComponent<Collider>());

        Renderer playerRenderer = playerVisual.GetComponent<Renderer>();
        Material playerMat = new Material(Shader.Find("Standard"));
        playerMat.color = new Color(0.2f, 0.4f, 0.6f, 1f); // Blue
        playerRenderer.material = playerMat;

        // ===== STEP 3: Create Camera =====
        GameObject cameraObj = new GameObject("PlayerCamera");
        cameraObj.transform.SetParent(player.transform);
        cameraObj.transform.localPosition = new Vector3(0, 1f, 0);
        
        Camera cam = cameraObj.AddComponent<Camera>();
        cam.tag = "MainCamera";
        cam.nearClipPlane = 0.3f;
        cam.farClipPlane = 1000f;
        
        cameraObj.AddComponent<AudioListener>();

        // Set as cinemachine target
        GameObject cinemachineTarget = new GameObject("CinemachineCameraTarget");
        cinemachineTarget.transform.SetParent(player.transform);
        cinemachineTarget.transform.localPosition = new Vector3(0, 0.6f, 0);

        thirdPersonController.CinemachineCameraTarget = cinemachineTarget;

        // ===== STEP 4: Create Input Manager =====
        StarterAssets.StarterAssetsInputs inputManager = player.AddComponent<StarterAssets.StarterAssetsInputs>();

        // ===== STEP 5: Create Saori NPC =====
        GameObject saoriObj = new GameObject("Saori");
        saoriObj.transform.position = new Vector3(5, 0.5f, 3);
        saoriObj.tag = "NPC";

        // Saori visual
        GameObject saoriVisual = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        saoriVisual.name = "SaoriVisual";
        saoriVisual.transform.SetParent(saoriObj.transform);
        saoriVisual.transform.localPosition = Vector3.zero;
        saoriVisual.transform.localScale = new Vector3(0.6f, 1.2f, 0.6f);

        Object.DestroyImmediate(saoriVisual.GetComponent<Collider>());
        
        Renderer saoriRenderer = saoriVisual.GetComponent<Renderer>();
        Material saoriMat = new Material(Shader.Find("Standard"));
        saoriMat.color = new Color(0.3f, 0.4f, 0.5f, 1f); // Grayish-blue
        saoriRenderer.material = saoriMat;

        // Add Saori intro script
        SaoriIntro saoriIntro = saoriObj.AddComponent<SaoriIntro>();

        // ===== STEP 6: Create UI Canvas for Codex Device =====
        GameObject canvasObj = new GameObject("UICanvas");
        Canvas canvas = canvasObj.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;

        CanvasScaler canvasScaler = canvasObj.AddComponent<CanvasScaler>();
        canvasScaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        canvasScaler.referenceResolution = new Vector2(1920, 1080);

        GraphicRaycaster raycaster = canvasObj.AddComponent<GraphicRaycaster>();

        // Create Codex device container
        GameObject deviceContainer = new GameObject("CodexDeviceContainer");
        RectTransform deviceRect = deviceContainer.AddComponent<RectTransform>();
        deviceContainer.transform.SetParent(canvasObj.transform, false);
        
        deviceRect.anchorMin = Vector2.zero;
        deviceRect.anchorMax = new Vector2(0.3f, 1f);
        deviceRect.offsetMin = Vector2.zero;
        deviceRect.offsetMax = Vector2.zero;

        CanvasGroup deviceCanvasGroup = deviceContainer.AddComponent<CanvasGroup>();
        CodexDevice codexDevice = deviceContainer.AddComponent<CodexDevice>();

        // Assign references to CodexDevice
        Image deviceImage = deviceContainer.AddComponent<Image>();
        deviceImage.color = new Color(1, 1, 1, 0.8f);
        
        // Set serialized fields through reflection
        var deviceImageField = typeof(CodexDevice).GetField("deviceImage", 
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
        deviceImageField?.SetValue(codexDevice, deviceImage);

        var deviceCanvasField = typeof(CodexDevice).GetField("deviceCanvasGroup",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
        deviceCanvasField?.SetValue(codexDevice, deviceCanvasGroup);

        var deviceRectField = typeof(CodexDevice).GetField("deviceRect",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
        deviceRectField?.SetValue(codexDevice, deviceRect);

        // ===== STEP 7: Create Input Manager for UI =====
        PlayerInput playerInput = player.GetComponent<PlayerInput>();
        if (playerInput == null)
        {
            playerInput = player.AddComponent<PlayerInput>();
        }

        // ===== STEP 8: Create Lighting =====
        GameObject lightObj = new GameObject("DirectionalLight");
        Light light = lightObj.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.2f;
        light.color = new Color(1f, 0.95f, 0.8f, 1f); // Warm sunlight
        lightObj.transform.rotation = Quaternion.Euler(50, -30, 0);

        // ===== STEP 9: Save Scene =====
        EditorSceneManager.SaveScene(scene);
        Debug.Log("✅ Gameplay Scene setup complete!");
        Debug.Log("🎮 Player: Position (0, 1, 0) - BLUE Capsule");
        Debug.Log("👤 Saori: Position (5, 0.5, 3) - Will trigger intro dialogue");
        Debug.Log("📱 Codex Device: Press 'G' to open device overlay");
        Debug.Log("⚠️  Movement: WASD | Sprint: Shift | Jump: Space | Look: Mouse");
        Debug.Log("🔮 Codex: Left/A = Prev Page | Right/D = Next Page | Enter = Select");
    }

    [MenuItem("Velinor/Setup Title Scene")]
    public static void SetupTitleScene()
    {
        Scene scene = EditorSceneManager.OpenScene("Assets/Scenes/TitleScene.unity", OpenSceneMode.Single);
        
        Debug.Log("✅ Title Scene is ready to edit!");
        Debug.Log("📝 Add background images and customize title screen UI");
    }
}
