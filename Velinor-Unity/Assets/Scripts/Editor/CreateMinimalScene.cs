using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

public class CreateMinimalScene
{
    [MenuItem("Velinor/Create Minimal Test Scene")]
    public static void Create()
    {
        // Create new scene
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

        // ===== CREATE GROUND (SIMPLE BOX) =====
        GameObject ground = new GameObject("Ground");
        ground.transform.position = Vector3.zero;
        
        // Add collider - NO SCALING TRICKS
        BoxCollider groundCol = ground.AddComponent<BoxCollider>();
        groundCol.size = new Vector3(100, 2, 100);  // Large flat platform
        groundCol.isTrigger = false;
        
        // Add Rigidbody - STATIC
        Rigidbody groundRb = ground.AddComponent<Rigidbody>();
        groundRb.isKinematic = true;
        groundRb.useGravity = false;
        
        // Add visual mesh
        MeshFilter mf = ground.AddComponent<MeshFilter>();
        mf.mesh = Resources.GetBuiltinResource<Mesh>("Cube.fbx");
        
        MeshRenderer mr = ground.AddComponent<MeshRenderer>();
        Material mat = new Material(Shader.Find("Standard"));
        mat.color = new Color(0.5f, 0.5f, 0.5f, 1f);
        mr.material = mat;
        
        // Scale for visual appearance only (collider uses absolute size)
        ground.transform.localScale = new Vector3(50, 1, 50);

        // ===== CREATE PLAYER =====
        GameObject player = new GameObject("Player");
        player.transform.position = new Vector3(0, 3, -10);  // WELL ABOVE GROUND
        player.tag = "Player";
        
        // CharacterController component
        CharacterController cc = player.AddComponent<CharacterController>();
        cc.height = 2f;
        cc.radius = 0.5f;
        cc.center = new Vector3(0, 1, 0);  // Center at feet
        
        // Movement script
        SimplePlayerMovement movement = player.AddComponent<SimplePlayerMovement>();
        
        // Add camera as child
        camObj.transform.SetParent(player.transform);
        camObj.transform.localPosition = new Vector3(0, 1.2f, -2.5f);
        camObj.transform.localRotation = Quaternion.identity;

        // ===== CREATE LIGHT =====
        GameObject lightObj = new GameObject("DirectionalLight");
        Light light = lightObj.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.2f;
        lightObj.transform.rotation = Quaternion.Euler(50, -30, 0);

        // Save scene
        EditorSceneManager.SaveScene(scene, "Assets/Scenes/GamplayScene.unity");

        Debug.Log("✅ MINIMAL SCENE CREATED");
        Debug.Log("📍 Player spawns at (0, 3, -10) - WELL ABOVE GROUND");
        Debug.Log("🟫 Ground is at (0, 0, 0) with collider size 100x2x100");
        Debug.Log("Use WASD to move, Space to jump");
    }
}
