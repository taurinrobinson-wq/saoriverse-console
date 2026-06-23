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

        // ===== CREATE GROUND =====
        GameObject ground = new GameObject("Ground");
        ground.transform.position = new Vector3(0, 0, 0);
        
        BoxCollider groundCol = ground.AddComponent<BoxCollider>();
        groundCol.size = new Vector3(20, 2, 20);  // Simple: 20x20 platform, 2 tall
        
        Rigidbody groundRb = ground.AddComponent<Rigidbody>();
        groundRb.isKinematic = true;
        groundRb.useGravity = false;
        
        // Visual: gray cube, no scaling tricks
        GameObject groundVis = GameObject.CreatePrimitive(PrimitiveType.Cube);
        groundVis.name = "Visual";
        groundVis.transform.SetParent(ground.transform);
        groundVis.transform.localPosition = Vector3.zero;
        groundVis.transform.localScale = new Vector3(20, 2, 20);
        Object.DestroyImmediate(groundVis.GetComponent<Collider>());
        groundVis.GetComponent<MeshRenderer>().material.color = new Color(0.5f, 0.5f, 0.5f, 1f);

        // ===== CREATE PLAYER =====
        GameObject player = new GameObject("Player");
        player.transform.position = new Vector3(0, 1, 0);  // Bottom at y=0 (ground top), top at y=2
        player.tag = "Player";
        
        CharacterController cc = player.AddComponent<CharacterController>();
        cc.height = 2f;
        cc.radius = 0.5f;
        cc.center = new Vector3(0, 1, 0);  // Offset so CC extends from y=0 to y=2
        
        // Visual: blue cylinder (2 units tall, 1 unit diameter)
        GameObject playerVis = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        playerVis.name = "Visual";
        playerVis.transform.SetParent(player.transform);
        playerVis.transform.localPosition = new Vector3(0, 1, 0);  // Align with CC
        playerVis.transform.localScale = new Vector3(1f, 1f, 1f);  // Natural size
        Object.DestroyImmediate(playerVis.GetComponent<Collider>());
        playerVis.GetComponent<MeshRenderer>().material.color = new Color(0.2f, 0.5f, 0.9f, 1f);
        
        // Movement script
        player.AddComponent<SimplePlayerMovement>();

        // ===== CREATE CAMERA =====
        GameObject camObj = new GameObject("Main Camera");
        Camera cam = camObj.AddComponent<Camera>();
        cam.tag = "MainCamera";
        cam.backgroundColor = new Color(0.3f, 0.5f, 0.7f, 1f);
        camObj.AddComponent<AudioListener>();
        camObj.transform.SetParent(player.transform);
        camObj.transform.localPosition = new Vector3(0, 1.2f, -2.5f);

        // ===== CREATE LIGHT =====
        GameObject lightObj = new GameObject("DirectionalLight");
        Light light = lightObj.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.2f;
        lightObj.transform.rotation = Quaternion.Euler(50, -30, 0);

        EditorSceneManager.SaveScene(scene, "Assets/Scenes/GamplayScene.unity");
        Debug.Log("✅ Scene created - Simple 20x20 platform");
        Debug.Log("🎮 Press Space to jump!");
    }
}
