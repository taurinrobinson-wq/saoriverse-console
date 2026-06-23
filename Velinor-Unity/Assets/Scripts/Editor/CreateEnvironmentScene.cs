using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class CreateEnvironmentScene
{
    [MenuItem("Velinor/Create Environment Scene")]
    public static void Create()
    {
        // Create fresh scene
        Scene scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);

        // Delete default camera
        GameObject defaultCam = GameObject.Find("Main Camera");
        if (defaultCam != null) Object.DestroyImmediate(defaultCam);

        // ===== CREATE CAMERA =====
        GameObject camObj = new GameObject("Main Camera");
        Camera cam = camObj.AddComponent<Camera>();
        cam.tag = "MainCamera";
        cam.backgroundColor = new Color(0.3f, 0.5f, 0.7f, 1f);
        camObj.AddComponent<AudioListener>();

        // ===== CREATE GROUND =====
        GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Cube);
        ground.name = "Ground";
        ground.transform.position = new Vector3(0, -0.5f, 0);
        ground.transform.localScale = new Vector3(50, 1, 50);
        
        // Use existing collider from primitive and scale it to match the visual size
        BoxCollider groundCollider = ground.GetComponent<BoxCollider>();
        groundCollider.isTrigger = false;  // Explicitly set to NOT trigger
        groundCollider.size = new Vector3(50, 1, 50);  // Match the visual scale
        
        Renderer groundRenderer = ground.GetComponent<Renderer>();
        Material groundMat = new Material(Shader.Find("Standard"));
        groundMat.color = new Color(0.4f, 0.4f, 0.4f, 1f);
        groundRenderer.material = groundMat;

        // ===== CREATE BUILDING (Large Cube with Door) =====
        GameObject building = GameObject.CreatePrimitive(PrimitiveType.Cube);
        building.name = "Building";
        building.transform.position = new Vector3(-8, 1.75f, 0);
        building.transform.localScale = new Vector3(6, 3.5f, 6);
        
        Object.DestroyImmediate(building.GetComponent<Collider>());
        BoxCollider buildingCollider = building.AddComponent<BoxCollider>();
        buildingCollider.size = new Vector3(6, 3.5f, 6);
        
        Renderer buildingRenderer = building.GetComponent<Renderer>();
        Material buildingMat = new Material(Shader.Find("Standard"));
        buildingMat.color = new Color(0.6f, 0.5f, 0.4f, 1f);
        buildingRenderer.material = buildingMat;

        // Create door opening (simple cube removal - visual only)
        GameObject doorOpening = GameObject.CreatePrimitive(PrimitiveType.Cube);
        doorOpening.name = "DoorOpening";
        doorOpening.transform.SetParent(building.transform);
        doorOpening.transform.localPosition = new Vector3(0, 0, -3.1f);
        doorOpening.transform.localScale = new Vector3(1.5f, 2.2f, 0.2f);
        Object.DestroyImmediate(doorOpening.GetComponent<Collider>());
        doorOpening.GetComponent<Renderer>().material.color = new Color(0, 0, 0, 0.5f);

        // ===== CREATE GLYPH (Small Sphere - 1/3 Player Height) =====
        GameObject glyph = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        glyph.name = "Glyph";
        glyph.transform.position = new Vector3(5, 0.67f, 0);
        glyph.transform.localScale = new Vector3(0.67f, 0.67f, 0.67f);
        
        Object.DestroyImmediate(glyph.GetComponent<Collider>());
        SphereCollider glyphCollider = glyph.AddComponent<SphereCollider>();
        glyphCollider.radius = 0.5f;
        glyphCollider.isTrigger = true;
        
        Renderer glyphRenderer = glyph.GetComponent<Renderer>();
        Material glyphMat = new Material(Shader.Find("Standard"));
        glyphMat.color = new Color(0.2f, 0.8f, 1f, 1f);
        glyphRenderer.material = glyphMat;
        
        GlyphObject glyphScript = glyph.AddComponent<GlyphObject>();
        glyphScript.interactionRange = 3f;

        // ===== CREATE NPC (Player-Sized Cube, Different Color) =====
        GameObject npc = GameObject.CreatePrimitive(PrimitiveType.Cube);
        npc.name = "NPC_Saori";
        npc.transform.position = new Vector3(3, 1, 3);
        npc.transform.localScale = new Vector3(0.4f, 2f, 0.4f);
        
        Object.DestroyImmediate(npc.GetComponent<Collider>());
        BoxCollider npcCollider = npc.AddComponent<BoxCollider>();
        npcCollider.size = new Vector3(1, 2, 1);
        npcCollider.isTrigger = true;
        
        Renderer npcRenderer = npc.GetComponent<Renderer>();
        Material npcMat = new Material(Shader.Find("Standard"));
        npcMat.color = new Color(0.8f, 0.3f, 0.6f, 1f);
        npcRenderer.material = npcMat;
        
        NPCObject npcScript = npc.AddComponent<NPCObject>();
        npcScript.npcName = "Saori";
        npcScript.interactionRange = 3f;

        // ===== CREATE PLAYER =====
        GameObject player = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        player.name = "Player";
        player.transform.position = new Vector3(0, 1, -5);
        player.tag = "Player";
        
        Object.DestroyImmediate(player.GetComponent<Collider>());
        CharacterController cc = player.AddComponent<CharacterController>();
        cc.height = 2f;
        cc.radius = 0.5f;
        
        Renderer playerRenderer = player.GetComponent<Renderer>();
        Material playerMat = new Material(Shader.Find("Standard"));
        playerMat.color = new Color(0.2f, 0.5f, 0.9f, 1f);
        playerRenderer.material = playerMat;
        
        SimplePlayerMovement movement = player.AddComponent<SimplePlayerMovement>();
        
        // Make camera child of player
        camObj.transform.SetParent(player.transform);
        camObj.transform.localPosition = new Vector3(0, 1.2f, -2.5f);
        camObj.transform.localRotation = Quaternion.identity;

        // ===== CREATE LIGHT =====
        GameObject lightObj = new GameObject("DirectionalLight");
        Light light = lightObj.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.2f;
        lightObj.transform.rotation = Quaternion.Euler(50, -30, 0);

        // ===== CREATE INTERACTION UI =====
        GameObject canvasGO = new GameObject("InteractionCanvas");
        Canvas canvas = canvasGO.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        
        CanvasScaler scaler = canvasGO.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920, 1080);

        InteractionUI interactionUI = canvasGO.AddComponent<InteractionUI>();

        // Save scene
        EditorSceneManager.SaveScene(scene, "Assets/Scenes/GamplayScene.unity");

        Debug.Log("✅ ENVIRONMENT SCENE CREATED");
        Debug.Log("📍 Player at (0, 1, -5)");
        Debug.Log("🏢 Building at (-8, 1.75, 0) - enter through door");
        Debug.Log("🔷 Glyph at (5, 0.67, 0) - 1/3 player size");
        Debug.Log("💬 NPC (Saori) at (3, 1, 3) - same height as player");
        Debug.Log("\nControls:");
        Debug.Log("  WASD = Move | Mouse = Look | Scroll = Zoom");
        Debug.Log("  Space = Jump | Shift = Sprint | E = Interact");
        Debug.Log("  ESC = Unlock cursor");
    }
}
