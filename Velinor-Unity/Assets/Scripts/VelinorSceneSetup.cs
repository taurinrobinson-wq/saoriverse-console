using UnityEngine;

/// <summary>
/// Velinor scene setup utilities with context menu helpers.
/// Provides one-click population of scenes with properly configured player character systems.
/// Attach this to an empty GameObject in your scene to access the context menu commands.
/// 
/// Usage:
/// 1. Create empty GameObject named "VelinorSetup" in scene
/// 2. Add this script
/// 3. Right-click component in Inspector → "Populate Player Character System"
/// 4. Script automatically creates and configures everything
/// 
/// © 2026 Saoriverse Console. All rights reserved.
/// This code is proprietary and confidential. Unauthorized copying, modification, or distribution
/// is strictly prohibited. See LICENSE_COMMERCIAL.md and NDA_TEMPLATE.md for licensing information.
/// </summary>
public class VelinorSceneSetup : MonoBehaviour
{
    [ContextMenu("Populate Player Character System")]
    public void PopulatePlayerCharacterSystem()
    {
        // Find or create Player root
        GameObject playerRoot = GameObject.FindGameObjectWithTag("Player");
        
        if (playerRoot == null)
        {
            playerRoot = new GameObject("Player");
            playerRoot.tag = "Player";
            Debug.Log("Created Player GameObject");
        }
        else
        {
            Debug.Log("Using existing Player GameObject");
        }
        
        // Add CharacterController if missing
        CharacterController cc = playerRoot.GetComponent<CharacterController>();
        if (cc == null)
        {
            cc = playerRoot.AddComponent<CharacterController>();
            cc.height = 2f;
            cc.radius = 0.4f;
            cc.center = new Vector3(0, 1f, 0);
            Debug.Log("Added CharacterController to Player");
        }
        
        // Add PlayerCharacterSetup if missing
        PlayerCharacterSetup pcs = playerRoot.GetComponent<PlayerCharacterSetup>();
        if (pcs == null)
        {
            pcs = playerRoot.AddComponent<PlayerCharacterSetup>();
            Debug.Log("Added PlayerCharacterSetup to Player");
        }
        
        // Create UMA character child if missing
        Transform umaChild = null;
        if (playerRoot.transform.childCount == 0)
        {
            GameObject umaObj = new GameObject("UMACharacter");
            umaObj.transform.SetParent(playerRoot.transform);
            umaObj.transform.localPosition = Vector3.zero;
            umaObj.transform.localRotation = Quaternion.identity;
            umaChild = umaObj.transform;
            Debug.Log("Created UMACharacter child");
        }
        else
        {
            umaChild = playerRoot.transform.GetChild(0);
            Debug.Log("Using existing child as UMACharacter");
        }
        
        // Find ground plane in scene
        Collider groundPlane = FindGroundPlane();
        if (groundPlane != null)
        {
            Debug.Log($"Found ground plane: {groundPlane.gameObject.name}");
        }
        else
        {
            Debug.LogWarning("No ground plane found - you'll need to assign it manually");
        }
        
        // Configure PlayerCharacterSetup references
        SerializedObject so = new SerializedObject(pcs);
        
        // Set UMA character transform
        SerializedProperty umaCharTransform = so.FindProperty("umaCharacterTransform");
        if (umaCharTransform != null)
        {
            umaCharTransform.objectReferenceValue = umaChild;
        }
        
        // Set ground plane collider
        if (groundPlane != null)
        {
            SerializedProperty groundPlaneCol = so.FindProperty("groundPlaneCollider");
            if (groundPlaneCol != null)
            {
                groundPlaneCol.objectReferenceValue = groundPlane;
            }
        }
        
        so.ApplyModifiedProperties();
        
        // Position player at origin
        playerRoot.transform.position = new Vector3(0, 0.5f, 0);
        
        Debug.Log("✓ Player character system populated successfully!");
        Debug.Log("Next steps: Add DynamicCharacterAvatar to UMACharacter child, create ground plane, configure depth scaling");
    }
    
    [ContextMenu("Create Ground Plane")]
    public void CreateGroundPlane()
    {
        // Check if ground plane already exists
        Collider existing = FindGroundPlane();
        if (existing != null)
        {
            Debug.LogWarning($"Ground plane already exists: {existing.gameObject.name}");
            return;
        }
        
        // Create plane GameObject
        GameObject planeObj = new GameObject("GroundPlane");
        planeObj.transform.position = Vector3.zero;
        
        // Add mesh filter and renderer
        MeshFilter mf = planeObj.AddComponent<MeshFilter>();
        mf.mesh = Resources.GetBuiltinResource<Mesh>("Plane.fbx");
        
        MeshRenderer mr = planeObj.AddComponent<MeshRenderer>();
        mr.enabled = false;  // Invisible
        
        // Add collider
        BoxCollider bc = planeObj.AddComponent<BoxCollider>();
        bc.size = new Vector3(20, 0.1f, 20);
        
        // Configure for ground (tilt for isometric perspective)
        planeObj.transform.Rotate(75, 0, 0);
        planeObj.transform.localScale = new Vector3(20, 1, 20);
        
        Debug.Log("✓ Ground plane created and configured!");
        Debug.Log("Adjust rotation (x=75 for isometric) and scale to match your scene");
    }
    
    [ContextMenu("Create Scene Managers")]
    public void CreateSceneManagers()
    {
        // Create SceneSpawnManager if missing
        if (FindObjectOfType<SceneSpawnManager>() == null)
        {
            GameObject smObj = new GameObject("SceneSpawnManager");
            smObj.AddComponent<SceneSpawnManager>();
            Debug.Log("Created SceneSpawnManager");
        }
        else
        {
            Debug.Log("SceneSpawnManager already exists");
        }
        
        // Create SceneTransitionManager if missing (but this should be DontDestroyOnLoad)
        if (FindObjectOfType<SceneTransitionManager>() == null)
        {
            GameObject tmObj = new GameObject("SceneTransitionManager");
            SceneTransitionManager stm = tmObj.AddComponent<SceneTransitionManager>();
            Debug.Log("Created SceneTransitionManager (check DontDestroyOnLoad setup)");
        }
        else
        {
            Debug.Log("SceneTransitionManager already exists");
        }
        
        // Create AmbientLayerController if missing
        if (FindObjectOfType<AmbientLayerController>() == null)
        {
            GameObject alcObj = new GameObject("AmbientLayerController");
            alcObj.AddComponent<AmbientLayerController>();
            Debug.Log("Created AmbientLayerController");
        }
        else
        {
            Debug.Log("AmbientLayerController already exists");
        }
        
        Debug.Log("✓ Scene managers created!");
    }
    
    [ContextMenu("Setup Camera for 3D/2D Hybrid")]
    public void SetupCamera()
    {
        Camera mainCam = Camera.main;
        if (mainCam == null)
        {
            Debug.LogError("No main camera found!");
            return;
        }
        
        // Configure for isometric/3D hybrid view
        mainCam.orthographic = true;
        mainCam.orthographicSize = 5f;
        mainCam.transform.position = new Vector3(-0.5f, 3f, -3f);
        mainCam.transform.rotation = Quaternion.Euler(45, 0, 0);
        mainCam.nearClipPlane = 0.1f;
        mainCam.farClipPlane = 100f;
        
        Debug.Log("✓ Camera configured for 3D/2D hybrid perspective!");
        Debug.Log("Adjust position and rotation to match your scene");
    }
    
    [ContextMenu("Create Spawn Point")]
    public void CreateSpawnPoint()
    {
        GameObject spawnObj = new GameObject("SpawnPoint_Main");
        spawnObj.transform.position = new Vector3(0, 0.5f, 0);
        
        SpawnPoint sp = spawnObj.AddComponent<SpawnPoint>();
        
        // Set default spawn ID
        SerializedObject so = new SerializedObject(sp);
        SerializedProperty spawnID = so.FindProperty("spawnID");
        if (spawnID != null)
        {
            spawnID.stringValue = "main";
        }
        so.ApplyModifiedProperties();
        
        Debug.Log("✓ Created SpawnPoint_Main at origin");
        Debug.Log("Add more SpawnPoints as needed with different IDs");
    }
    
    [ContextMenu("Complete Scene Setup")]
    public void CompleteSceneSetup()
    {
        Debug.Log("=== Starting Complete Scene Setup ===");
        CreateGroundPlane();
        CreateSceneManagers();
        SetupCamera();
        CreateSpawnPoint();
        PopulatePlayerCharacterSystem();
        Debug.Log("=== Scene Setup Complete! ===");
    }
    
    /// <summary>
    /// Helper to find ground plane in scene by name or tag.
    /// </summary>
    private Collider FindGroundPlane()
    {
        // Search by name
        Collider[] allColliders = FindObjectsByType<Collider>(FindObjectsInactive.Exclude, FindObjectsSortMode.None);
        foreach (var col in allColliders)
        {
            string name = col.gameObject.name.ToLower();
            if (name.Contains("ground") || name.Contains("plane") || name.Contains("floor"))
            {
                return col;
            }
        }
        return null;
    }
}
