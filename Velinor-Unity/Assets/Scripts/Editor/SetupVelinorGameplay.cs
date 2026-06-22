using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

public class SetupVelinorGameplay
{
    [MenuItem("Velinor/CLEAN SETUP - Gameplay Scene")]
    public static void CleanSetupGameplayScene()
    {
        // Close all scenes and open fresh
        EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
        
        Scene scene = EditorSceneManager.GetActiveScene();
        EditorSceneManager.SaveScene(scene, "Assets/Scenes/GamplayScene.unity");

        // Remove default camera
        GameObject defaultCamera = GameObject.Find("Main Camera");
        if (defaultCamera != null) Object.DestroyImmediate(defaultCamera);

        // ===== GROUND =====
        GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = "Ground";
        ground.transform.position = Vector3.zero;
        ground.transform.localScale = new Vector3(20, 1, 20);
        Object.DestroyImmediate(ground.GetComponent<Collider>());
        ground.AddComponent<BoxCollider>().size = new Vector3(20, 0.1f, 20);
        
        Renderer groundRend = ground.GetComponent<Renderer>();
        Material groundMat = new Material(Shader.Find("Standard"));
        groundMat.color = new Color(0.5f, 0.45f, 0.3f, 1f); // Brown
        groundRend.material = groundMat;

        // ===== PLAYER =====
        GameObject player = new GameObject("Player");
        player.tag = "Player";
        player.transform.position = new Vector3(0, 1.5f, 0);

        CharacterController cc = player.AddComponent<CharacterController>();
        cc.height = 1.8f;
        cc.radius = 0.5f;
        cc.center = new Vector3(0, 0.9f, 0);

        // Player visual
        GameObject capsule = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        capsule.transform.SetParent(player.transform);
        capsule.transform.localPosition = Vector3.zero;
        capsule.transform.localScale = Vector3.one;
        capsule.name = "PlayerVisual";
        Object.DestroyImmediate(capsule.GetComponent<Collider>());
        
        Renderer capsRend = capsule.GetComponent<Renderer>();
        Material capsuleMat = new Material(Shader.Find("Standard"));
        capsuleMat.color = new Color(0.3f, 0.5f, 0.7f, 1f); // Blue
        capsRend.material = capsuleMat;

        // Add third-person controller
        StarterAssets.ThirdPersonController tpc = player.AddComponent<StarterAssets.ThirdPersonController>();
        tpc.MoveSpeed = 3f;
        tpc.SprintSpeed = 5.5f;
        tpc.GroundedRadius = 0.5f;

        // Add input
        player.AddComponent<StarterAssets.StarterAssetsInputs>();

        // ===== CAMERA =====
        GameObject cam = new GameObject("PlayerCamera");
        cam.transform.SetParent(player.transform);
        cam.transform.localPosition = new Vector3(0, 0.6f, 0);
        cam.AddComponent<Camera>();
        cam.AddComponent<AudioListener>();
        cam.tag = "MainCamera";
        
        tpc.CinemachineCameraTarget = cam;

        // ===== SAORI NPC =====
        GameObject saori = new GameObject("Saori");
        saori.transform.position = new Vector3(5, 0.5f, 3);

        GameObject saoriVisual = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        saoriVisual.transform.SetParent(saori.transform);
        saoriVisual.transform.localPosition = Vector3.zero;
        saoriVisual.transform.localScale = new Vector3(0.6f, 1.2f, 0.6f);
        saoriVisual.name = "SaoriVisual";
        Object.DestroyImmediate(saoriVisual.GetComponent<Collider>());
        
        Renderer saoriRend = saoriVisual.GetComponent<Renderer>();
        Material saoriMat = new Material(Shader.Find("Standard"));
        saoriMat.color = new Color(0.5f, 0.3f, 0.6f, 1f); // Purple-ish
        saoriRend.material = saoriMat;

        saori.AddComponent<SaoriIntro>();

        // ===== LIGHT =====
        GameObject light = new GameObject("DirectionalLight");
        Light lightComp = light.AddComponent<Light>();
        lightComp.type = LightType.Directional;
        lightComp.intensity = 1.2f;
        lightComp.color = new Color(1f, 0.95f, 0.8f, 1f);
        light.transform.rotation = Quaternion.Euler(50, -30, 0);

        // ===== UI CANVAS =====
        GameObject canvasObj = new GameObject("UICanvas");
        Canvas canvas = canvasObj.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        
        CanvasScaler scaler = canvasObj.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920, 1080);

        canvasObj.AddComponent<GraphicRaycaster>();

        // Codex device container
        GameObject deviceContainer = new GameObject("CodexDevice");
        RectTransform deviceRect = deviceContainer.AddComponent<RectTransform>();
        deviceContainer.transform.SetParent(canvasObj.transform, false);
        deviceRect.anchorMin = Vector2.zero;
        deviceRect.anchorMax = new Vector2(0.4f, 1f);
        deviceRect.offsetMin = Vector2.zero;
        deviceRect.offsetMax = Vector2.zero;

        CanvasGroup canvasGroup = deviceContainer.AddComponent<CanvasGroup>();
        CodexDevice codex = deviceContainer.AddComponent<CodexDevice>();
        
        Image deviceImage = deviceContainer.AddComponent<Image>();
        deviceImage.color = new Color(0.2f, 0.2f, 0.2f, 0.7f);

        // Hack: Set private fields via reflection
        var imgField = typeof(CodexDevice).GetField("deviceImage", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
        imgField?.SetValue(codex, deviceImage);
        
        var canvasField = typeof(CodexDevice).GetField("deviceCanvasGroup", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
        canvasField?.SetValue(codex, canvasGroup);
        
        var rectField = typeof(CodexDevice).GetField("deviceRect", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
        rectField?.SetValue(codex, deviceRect);

        // Save scene
        EditorSceneManager.SaveScene(scene, "Assets/Scenes/GamplayScene.unity");

        Debug.Log("✅ GAMEPLAY SCENE READY");
        Debug.Log("📍 Player (Blue Capsule): (0, 1.5, 0)");
        Debug.Log("👤 Saori (Purple Cylinder): (5, 0.5, 3) - Will greet player on approach");
        Debug.Log("📱 Press G to toggle Codex Device");
        Debug.Log("🎮 Controls: WASD=Move, Shift=Sprint, Space=Jump");
    }
}
