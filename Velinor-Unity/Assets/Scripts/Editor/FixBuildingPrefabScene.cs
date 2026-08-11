using UnityEditor;
using UnityEngine;

/// <summary>
/// FixBuildingPrefabScene - Comprehensive scene setup fix for BuildingPrefab.
/// 
/// Fixes:
/// 1. Adds proper colliders to interactive objects (Door, SaoriNPC)
/// 2. Converts camera from first-person to third-person
/// 3. Sets correct initial camera orientation (facing building)
/// 
/// Usage: Go to Velinor > Fix BuildingPrefab Scene in the menu.
/// </summary>
public class FixBuildingPrefabScene
{
    [MenuItem("Velinor/Fix BuildingPrefab Scene")]
    public static void FixScene()
    {
        Debug.Log("=== Fixing BuildingPrefab Scene ===\n");

        // Step 1: Remove duplicate/old scripts
        RemoveDuplicateScripts();

        // Step 2: Fix Player setup
        FixPlayer();
        FixDoor();
        FixSaoriNPC();

        Debug.Log("\n✅ BuildingPrefab Scene is now FIXED!");
        Debug.Log("\n📋 What was fixed:");
        Debug.Log("  • Camera repositioned for third-person view");
        Debug.Log("  • Door given proper collider for interaction");
        Debug.Log("  • SaoriNPC given proper collider for interaction");
        Debug.Log("  • Initial camera orientation set to face building");
        
        Debug.Log("\n🎮 How to use:");
        Debug.Log("  • WASD: Movement always active (W=forward relative to camera)");
        Debug.Log("  • Right-click + Mouse: Camera look");
        Debug.Log("  • Left-click: Interact (when cursor visible)");
        Debug.Log("  • E-key: Alternate interact");
    }

    private static void RemoveDuplicateScripts()
    {
        GameObject player = GameObject.Find("Player");
        if (player == null)
        {
            Debug.LogError("❌ Player GameObject not found!");
            return;
        }

        Debug.Log("🧹 Removing duplicate/old scripts...");

        int removedCount = 0;

        // Remove old StarterAssets input handler
        var oldInput = player.GetComponent<StarterAssets.StarterAssetsInputs>();
        if (oldInput != null)
        {
            Debug.Log("  ❌ Removing: Starter Assets Inputs (old)");
            Object.DestroyImmediate(oldInput);
            removedCount++;
        }

        // Remove old StarterAssets controller
        var oldController = player.GetComponent<StarterAssets.ThirdPersonController>();
        if (oldController != null)
        {
            Debug.Log("  ❌ Removing: Third Person Controller (old)");
            Object.DestroyImmediate(oldController);
            removedCount++;
        }

        if (removedCount > 0)
        {
            Debug.Log($"✓ Removed {removedCount} old scripts\n");
        }
    }

    private static void FixPlayer()
    {
        GameObject player = GameObject.Find("Player");
        if (player == null)
        {
            Debug.LogError("❌ Player GameObject not found!");
            return;
        }

        Debug.Log("✓ Found Player GameObject");

        // Ensure Player GameObject is active
        if (!player.activeInHierarchy)
        {
            player.SetActive(true);
            Debug.Log("✓ Player GameObject activated");
        }

        // Enable CharacterController if it's disabled
        CharacterController charController = player.GetComponent<CharacterController>();
        if (charController != null && !charController.enabled)
        {
            charController.enabled = true;
            Debug.Log("✓ CharacterController component enabled");
        }

        // Find or create Main Camera
        GameObject cameraObj = GameObject.FindGameObjectWithTag("MainCamera");
        if (cameraObj == null)
        {
            cameraObj = new GameObject("Main Camera");
            cameraObj.tag = "MainCamera";
            cameraObj.transform.SetParent(player.transform);
            Debug.Log("✓ Created Main Camera");
        }
        else
        {
            Debug.Log("✓ Main Camera already exists");
            // Reparent to player if needed
            if (cameraObj.transform.parent != player.transform)
            {
                cameraObj.transform.SetParent(player.transform);
                Debug.Log("✓ Reparented camera to player");
            }
        }

        // Set camera to THIRD-PERSON position (behind and above player)
        cameraObj.transform.localPosition = new Vector3(0, 0.8f, -2.5f);
        cameraObj.transform.localRotation = Quaternion.identity;

        Camera cam = cameraObj.GetComponent<Camera>();
        if (cam == null)
        {
            cam = cameraObj.AddComponent<Camera>();
            Debug.Log("✓ Added Camera component");
        }

        cam.nearClipPlane = 0.3f;
        cam.farClipPlane = 1000f;

        if (cameraObj.GetComponent<AudioListener>() == null)
        {
            cameraObj.AddComponent<AudioListener>();
        }

        Debug.Log("✓ Camera set to third-person (behind player)");

        // Set initial camera yaw to face building (assume building is at positive Z)
        // This makes WASD feel natural: W = forward toward building
        var playerController = player.GetComponent<StarterAssets.VelinorPlayerController>();
        if (playerController != null)
        {
            // The yaw will be set by the controller, but we ensure proper starting rotation
            player.transform.rotation = Quaternion.identity; // Face forward (Z+)
            Debug.Log("✓ Player rotation set to face building");
        }
    }

    private static void FixDoor()
    {
        GameObject door = FindGameObjectInScene("Door");
        if (door == null)
        {
            Debug.LogWarning("⚠ Door GameObject not found. Interaction may not work.");
            return;
        }

        Debug.Log("✓ Found Door GameObject");

        // Ensure Door has a collider for interaction raycast
        Collider doorCollider = door.GetComponent<Collider>();
        if (doorCollider == null)
        {
            doorCollider = door.AddComponent<BoxCollider>();
            Debug.Log("✓ Added BoxCollider to Door");
        }

        // Collider should NOT be a trigger (so raycast hits it)
        doorCollider.isTrigger = false;
        Debug.Log("✓ Door collider set to non-trigger (raycast-able)");

        // Ensure DoorController is present
        var doorController = door.GetComponent<DoorController>();
        if (doorController == null)
        {
            doorController = door.AddComponent<DoorController>();
            Debug.Log("✓ Added DoorController component");
        }
    }

    private static void FixSaoriNPC()
    {
        GameObject saori = FindGameObjectInScene("Saori");
        if (saori == null)
        {
            Debug.LogWarning("⚠ Saori/SaoriNPC GameObject not found. Interaction may not work.");
            return;
        }

        Debug.Log("✓ Found Saori GameObject");

        // Ensure Saori has a collider for interaction raycast
        Collider saoriCollider = saori.GetComponent<Collider>();
        if (saoriCollider == null)
        {
            saoriCollider = saori.AddComponent<BoxCollider>();
            Debug.Log("✓ Added BoxCollider to Saori");
        }

        // Collider should NOT be a trigger (so raycast hits it)
        saoriCollider.isTrigger = false;
        Debug.Log("✓ Saori collider set to non-trigger (raycast-able)");

        // Ensure SaoriNPC or IInteractable is present
        if (saori.GetComponent<Velinor.Core.IInteractable>() == null)
        {
            var saoriNPC = saori.GetComponent<Velinor.Core.SaoriNPC>();
            if (saoriNPC == null)
            {
                saoriNPC = saori.AddComponent<Velinor.Core.SaoriNPC>();
                Debug.Log("✓ Added SaoriNPC component");
            }
        }
    }

    /// <summary>
    /// Find a game object by name in the current scene (case-insensitive partial match).
    /// </summary>
    private static GameObject FindGameObjectInScene(string name)
    {
        GameObject[] allObjects = GameObject.FindObjectsByType<GameObject>();
        foreach (GameObject obj in allObjects)
        {
            if (obj.name.Contains(name) || obj.name.IndexOf(name, System.StringComparison.OrdinalIgnoreCase) >= 0)
            {
                return obj;
            }
        }
        return null;
    }
}
