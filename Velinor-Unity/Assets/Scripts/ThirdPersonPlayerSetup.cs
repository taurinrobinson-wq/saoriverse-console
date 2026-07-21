using UnityEngine;
using UnityEditor;

/// <summary>
/// Third-person controller player setup helper.
/// Provides one-click context menu to add a complete player character to your scene.
/// Uses StarterAssets ThirdPersonController instead of UMA for simplicity.
/// 
/// Usage:
/// 1. Select any GameObject in your scene
/// 2. Add this script to it (or add to any existing GameObject)
/// 3. Right-click component in Inspector → "Add Third Person Player"
/// 4. Done! Player spawns with camera and all components wired up
/// 
/// © 2026 Saoriverse Console. All rights reserved.
/// This code is proprietary and confidential. Unauthorized copying, modification, or distribution
/// is strictly prohibited. See LICENSE_COMMERCIAL.md and NDA_TEMPLATE.md for licensing information.
/// </summary>
public class ThirdPersonPlayerSetup : MonoBehaviour
{
    [SerializeField]
    private float playerSpawnX = 0f;

    [SerializeField]
    private float playerSpawnY = 0f;

    [SerializeField]
    private float playerSpawnZ = 0f;

    [ContextMenu("Add Third Person Player")]
    public void AddThirdPersonPlayer()
    {
        Debug.Log("=== Creating Third Person Player ===");

        // Load player prefab - use PlayerArmature which has rigging and animations
        GameObject playerPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(
            "Assets/StarterAssets/ThirdPersonController/Prefabs/PlayerArmature.prefab");

        if (playerPrefab == null)
        {
            Debug.LogError("❌ Cannot find PlayerArmature prefab!");
            Debug.LogError("Expected at: Assets/StarterAssets/ThirdPersonController/Prefabs/PlayerArmature.prefab");
            return;
        }

        // Instantiate player
        GameObject player = Instantiate(playerPrefab);
        player.name = "Player";
        player.transform.position = new Vector3(playerSpawnX, playerSpawnY, playerSpawnZ);
        player.tag = "Player";
        Debug.Log("✓ Created Player from prefab (rigged with animations)");

        // Load camera prefab
        GameObject cameraPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(
            "Assets/StarterAssets/ThirdPersonController/Prefabs/PlayerFollowCamera.prefab");

        if (cameraPrefab != null)
        {
            GameObject cameraObj = Instantiate(cameraPrefab);
            cameraObj.name = "PlayerFollowCamera";
            cameraObj.transform.SetParent(player.transform);
            cameraObj.transform.localPosition = Vector3.zero;
            cameraObj.transform.localRotation = Quaternion.identity;
            Debug.Log("✓ Added follow camera");
        }
        else
        {
            Debug.LogWarning("⚠ Could not find PlayerFollowCamera prefab (optional)");
        }

        // Find and link ground plane, or create one if needed
        Collider groundPlane = FindGroundPlane();
        if (groundPlane == null)
        {
            // Create ground plane
            GameObject groundObj = new GameObject("GroundPlane");
            groundObj.transform.position = Vector3.zero;

            // Add collider
            BoxCollider bc = groundObj.AddComponent<BoxCollider>();
            bc.size = new Vector3(100, 0.1f, 100);

            // Add mesh for reference
            MeshFilter mf = groundObj.AddComponent<MeshFilter>();
            mf.mesh = Resources.GetBuiltinResource<Mesh>("Cube.fbx");

            MeshRenderer mr = groundObj.AddComponent<MeshRenderer>();
            mr.enabled = false;  // Invisible

            groundPlane = bc;
            Debug.Log("✓ Created ground plane (invisible)");
        }

        Debug.Log("\n=== Third Person Player Ready! ===");
        Debug.Log("Player setup complete with:");
        Debug.Log("  • ThirdPersonController component");
        Debug.Log("  • Animator for animations");
        Debug.Log("  • Follow camera system");
        Debug.Log("  • Ground collision detection");
        Debug.Log("");
        Debug.Log("Controls:");
        Debug.Log("  • WASD or Analog Stick: Move");
        Debug.Log("  • Space / South Button: Jump");
        Debug.Log("  • Shift: Sprint");
        Debug.Log("  • Mouse/Right Stick: Look around");
        Debug.Log("");
        Debug.Log("Press Play to test!");
    }

    private Collider FindGroundPlane()
    {
        Collider[] allColliders = FindObjectsByType<Collider>(FindObjectsInactive.Exclude);
        foreach (var col in allColliders)
        {
            // Skip the player's own colliders
            if (col.gameObject.name.Contains("Player"))
                continue;

            string name = col.gameObject.name.ToLower();
            if (name.Contains("ground") || name.Contains("plane") || name.Contains("floor"))
            {
                return col;
            }
        }
        return null;
    }
}
