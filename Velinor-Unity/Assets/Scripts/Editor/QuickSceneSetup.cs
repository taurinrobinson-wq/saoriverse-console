using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

public class QuickSceneSetup
{
    [MenuItem("Velinor/Quick Test Scene")]
    public static void CreateTestScene()
    {
        // Open fresh scene
        Scene scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);

        // Delete default camera
        GameObject defaultCam = GameObject.Find("Main Camera");
        if (defaultCam != null) Object.DestroyImmediate(defaultCam);

        // ===== CREATE CAMERA AT GOOD POSITION =====
        GameObject camObj = new GameObject("Main Camera");
        Camera cam = camObj.AddComponent<Camera>();
        cam.tag = "MainCamera";
        cam.backgroundColor = new Color(0.3f, 0.5f, 0.7f, 1f); // Blue background
        camObj.AddComponent<AudioListener>();
        
        // Position camera to see everything
        camObj.transform.position = new Vector3(0, 5, -10);
        camObj.transform.LookAt(new Vector3(0, 0, 0));

        // ===== CREATE GROUND - GUARANTEED VISIBLE =====
        GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = "Ground";
        ground.transform.position = Vector3.zero;
        ground.transform.localScale = new Vector3(10, 1, 10);

        // Remove collider from plane
        Collider groundCollider = ground.GetComponent<Collider>();
        if (groundCollider != null) Object.DestroyImmediate(groundCollider);

        // Add box collider for solid ground
        BoxCollider bc = ground.AddComponent<BoxCollider>();
        bc.size = new Vector3(10, 0.1f, 10);

        // Material for ground
        Renderer groundRenderer = ground.GetComponent<Renderer>();
        Material groundMat = new Material(Shader.Find("Standard"));
        groundMat.color = new Color(0.5f, 0.4f, 0.3f, 1f);
        groundRenderer.material = groundMat;

        // ===== CREATE PLAYER CAPSULE =====
        GameObject player = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        player.name = "Player";
        player.transform.position = new Vector3(0, 1, 0);
        
        Renderer playerRenderer = player.GetComponent<Renderer>();
        Material playerMat = new Material(Shader.Find("Standard"));
        playerMat.color = new Color(0.2f, 0.5f, 0.8f, 1f); // Blue
        playerRenderer.material = playerMat;

        // ===== CREATE NPC CUBE =====
        GameObject npc = GameObject.CreatePrimitive(PrimitiveType.Cube);
        npc.name = "NPC_Saori";
        npc.transform.position = new Vector3(3, 1, 3);
        npc.transform.localScale = new Vector3(0.5f, 1.5f, 0.5f); // Tall thin cube
        
        Renderer npcRenderer = npc.GetComponent<Renderer>();
        Material npcMat = new Material(Shader.Find("Standard"));
        npcMat.color = new Color(0.8f, 0.3f, 0.6f, 1f); // Purple-pink
        npcRenderer.material = npcMat;

        // ===== CREATE LIGHT =====
        GameObject lightObj = new GameObject("Light");
        Light light = lightObj.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1;
        lightObj.transform.rotation = Quaternion.Euler(50, -30, 0);

        // Save scene
        EditorSceneManager.SaveScene(scene, "Assets/Scenes/GamplayScene.unity");

        Debug.Log("✅ TEST SCENE CREATED");
        Debug.Log("📍 Camera at (0, 5, -10) looking at origin");
        Debug.Log("🟤 Ground plane at (0, 0, 0)");
        Debug.Log("🔵 Player capsule at (0, 1, 0)");
        Debug.Log("💜 NPC cube at (3, 1, 3)");
        Debug.Log("Hit Play now!");
    }
}
