using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

public class CreateSimplePlayableScene
{
    [MenuItem("Velinor/Simple Playable Scene")]
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
        camObj.transform.position = new Vector3(0, 3, -8);
        camObj.transform.LookAt(Vector3.zero);

        // ===== CREATE GROUND =====
        GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = "Ground";
        ground.transform.position = Vector3.zero;
        ground.transform.localScale = new Vector3(20, 1, 20);
        Collider groundCollider = ground.GetComponent<Collider>();
        if (groundCollider != null) Object.DestroyImmediate(groundCollider);
        BoxCollider bc = ground.AddComponent<BoxCollider>();
        bc.size = new Vector3(20, 0.1f, 20);
        
        Renderer groundRenderer = ground.GetComponent<Renderer>();
        Material groundMat = new Material(Shader.Find("Standard"));
        groundMat.color = new Color(0.6f, 0.5f, 0.4f, 1f);
        groundRenderer.material = groundMat;

        // ===== CREATE PLAYER =====
        GameObject player = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        player.name = "Player";
        player.transform.position = new Vector3(0, 1, 0);
        
        Renderer playerRenderer = player.GetComponent<Renderer>();
        Material playerMat = new Material(Shader.Find("Standard"));
        playerMat.color = new Color(0.2f, 0.5f, 0.9f, 1f);
        playerRenderer.material = playerMat;

        // ===== CREATE NPC =====
        GameObject npc = GameObject.CreatePrimitive(PrimitiveType.Cube);
        npc.name = "NPC";
        npc.transform.position = new Vector3(5, 0.75f, 5);
        npc.transform.localScale = new Vector3(0.8f, 1.5f, 0.8f);
        
        Renderer npcRenderer = npc.GetComponent<Renderer>();
        Material npcMat = new Material(Shader.Find("Standard"));
        npcMat.color = new Color(0.8f, 0.3f, 0.6f, 1f);
        npcRenderer.material = npcMat;

        // ===== CREATE LIGHT =====
        GameObject lightObj = new GameObject("DirectionalLight");
        Light light = lightObj.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.2f;
        lightObj.transform.rotation = Quaternion.Euler(50, -30, 0);

        // Save
        EditorSceneManager.SaveScene(scene, "Assets/Scenes/GamplayScene.unity");
        
        Debug.Log("✅ Simple playable scene created");
        Debug.Log("📍 Camera at (0, 3, -8)");
        Debug.Log("🟤 Ground, 🔵 Blue Player, 💜 Purple NPC");
        Debug.Log("Just hit Play - no controllers added yet");
    }
}
