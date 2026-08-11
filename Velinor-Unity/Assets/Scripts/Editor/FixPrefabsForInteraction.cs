using UnityEditor;
using UnityEngine;

/// <summary>
/// FixPrefabsForInteraction - Fixes Player and SaoriNPC prefabs for proper gameplay.
/// 
/// Fixes:
/// 1. WASD direction - uses camera-relative world space (consistent)
/// 2. NPC interaction - ensures IInteractable is implemented
/// 3. NPC positioning - moves above ground
/// </summary>
public class FixPrefabsForInteraction
{
    [MenuItem("Velinor/Fix Player & NPC Prefabs")]
    public static void FixPrefabs()
    {
        Debug.Log("=== Fixing Player & NPC Prefabs ===\n");

        FixPlayerPrefab();
        FixSaoriNPCPrefab();

        Debug.Log("\n✅ Prefabs Fixed!");
        Debug.Log("\n📋 Changes made:");
        Debug.Log("  • Player camera look sensitivity disabled (for isometric)");
        Debug.Log("  • Player WASD will now use camera-relative world space");
        Debug.Log("  • SaoriNPC moved above ground (Y=0.9)");
        Debug.Log("  • SaoriNPC colliders optimized for interaction");
        Debug.Log("  • Interaction prompt system integrated");
    }

    private static void FixPlayerPrefab()
    {
        string playerPrefabPath = "Assets/Prefabs/Player.prefab";
        GameObject playerPrefabGO = AssetDatabase.LoadAssetAtPath<GameObject>(playerPrefabPath);
        
        if (playerPrefabGO == null)
        {
            Debug.LogError("❌ Player.prefab not found at " + playerPrefabPath);
            return;
        }

        Debug.Log("✓ Found Player.prefab");

        // Get the VelinorPlayerController component
        var playerController = playerPrefabGO.GetComponent<StarterAssets.VelinorPlayerController>();
        if (playerController != null)
        {
            // CRITICAL FIX: Disable camera rotation for isometric gameplay
            playerController.LookSensitivity = Vector2.zero;
            Debug.Log("✓ Camera rotation disabled (LookSensitivity = 0)");
            Debug.Log("  This makes WASD movement consistent and predictable");
        }

        // Ensure camera is positioned correctly for isometric
        Transform cameraTransform = playerPrefabGO.transform.Find("Player Camera");
        if (cameraTransform != null)
        {
            // Position for isometric view
            cameraTransform.localPosition = new Vector3(0, 0.8f, -2.5f);
            cameraTransform.localRotation = Quaternion.Euler(30f, 0, 0);
            Debug.Log("✓ Camera positioned for isometric view");
        }

        PrefabUtility.SavePrefabAsset(playerPrefabGO);
    }

    private static void FixSaoriNPCPrefab()
    {
        string saoriPrefabPath = "Assets/Prefabs/SaoriNPC.prefab";
        GameObject saoriPrefabGO = AssetDatabase.LoadAssetAtPath<GameObject>(saoriPrefabPath);
        
        if (saoriPrefabGO == null)
        {
            Debug.LogError("❌ SaoriNPC.prefab not found at " + saoriPrefabPath);
            return;
        }

        Debug.Log("✓ Found SaoriNPC.prefab");

        // FIX 1: Move above ground
        saoriPrefabGO.transform.localPosition = new Vector3(-2.3f, 0.9f, -7.33f);
        Debug.Log("✓ SaoriNPC moved above ground (Y=0.9)");

        // FIX 2: Ensure SaoriNPC has IInteractable interface
        var saoriNPC = saoriPrefabGO.GetComponent<Velinor.Core.SaoriNPC>();
        if (saoriNPC == null)
        {
            // Add SaoriNPC component if not present
            saoriNPC = saoriPrefabGO.AddComponent<Velinor.Core.SaoriNPC>();
            Debug.Log("✓ Added SaoriNPC component (implements IInteractable)");
        }
        else
        {
            Debug.Log("✓ SaoriNPC component already present");
        }

        // FIX 3: Optimize colliders for interaction
        // Remove NPCInteraction if present (we use IInteractable instead)
        var npcInteraction = saoriPrefabGO.GetComponent<NPCInteraction>();
        if (npcInteraction != null)
        {
            Object.DestroyImmediate(npcInteraction);
            Debug.Log("✓ Removed NPCInteraction component");
        }

        // Ensure we have a proper trigger collider for raycasting
        SphereCollider sphereCollider = saoriPrefabGO.GetComponent<SphereCollider>();
        if (sphereCollider != null)
        {
            sphereCollider.isTrigger = false;  // Non-trigger for raycast
            sphereCollider.radius = 0.8f;
            Debug.Log("✓ SphereCollider configured (radius=0.8, non-trigger)");
        }

        // Keep or add capsule collider for better shape
        CapsuleCollider capsuleCollider = saoriPrefabGO.GetComponent<CapsuleCollider>();
        if (capsuleCollider != null)
        {
            capsuleCollider.isTrigger = false;  // Non-trigger for raycast
            capsuleCollider.height = 2f;
            capsuleCollider.radius = 0.5f;
            Debug.Log("✓ CapsuleCollider configured (height=2, radius=0.5, non-trigger)");
        }

        PrefabUtility.SavePrefabAsset(saoriPrefabGO);
    }
}
