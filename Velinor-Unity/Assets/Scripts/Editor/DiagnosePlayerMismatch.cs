using UnityEditor;
using UnityEngine;

/// <summary>
/// DiagnosePlayerMismatch - Diagnoses why the visual mesh and CharacterController are misaligned.
/// Shows the hierarchy, positions, scales, and component configurations.
/// </summary>
public class DiagnosePlayerMismatch
{
    [MenuItem("Velinor/Diagnose Player Mesh Mismatch")]
    public static void DiagnosePlayer()
    {
        GameObject player = GameObject.Find("Player");
        if (player == null)
        {
            Debug.LogError("❌ Player not found!");
            return;
        }

        Debug.Log("=== PLAYER HIERARCHY & COMPONENT DIAGNOSIS ===\n");

        // Check root Player position
        Debug.Log($"[ROOT] Player");
        Debug.Log($"  Position: {player.transform.position}");
        Debug.Log($"  Rotation: {player.transform.rotation.eulerAngles}");
        Debug.Log($"  Scale: {player.transform.localScale}");

        // Check CharacterController
        var charController = player.GetComponent<CharacterController>();
        if (charController != null)
        {
            Debug.Log($"\n[COMPONENT] CharacterController");
            Debug.Log($"  Height: {charController.height}");
            Debug.Log($"  Radius: {charController.radius}");
            Debug.Log($"  Center (OFFSET): {charController.center}");
            Debug.Log($"  ⚠️  CENTER OFFSET is the problem! It shifts the collision volume");
        }

        // Check all child GameObjects
        Debug.Log($"\n[CHILDREN] Player has {player.transform.childCount} children:");
        foreach (Transform child in player.transform)
        {
            Debug.Log($"\n  Child: {child.name}");
            Debug.Log($"    Local Position: {child.localPosition}");
            Debug.Log($"    Local Rotation: {child.localRotation.eulerAngles}");
            Debug.Log($"    Local Scale: {child.localScale}");

            // Check if it has a mesh renderer
            MeshRenderer meshRend = child.GetComponent<MeshRenderer>();
            if (meshRend != null)
            {
                Debug.Log($"    ✓ Has MeshRenderer (VISUAL)");
            }

            // Check if it has a collider
            Collider coll = child.GetComponent<Collider>();
            if (coll != null)
            {
                Debug.Log($"    ✓ Has {coll.GetType().Name}");
            }
        }

        Debug.Log("\n=== DIAGNOSIS ===\n");
        Debug.Log("The issue is likely ONE of these:");
        Debug.Log("1. CharacterController.center is offset (e.g., (0, 0.9, 0))");
        Debug.Log("   └─ Solution: Set center to (0, 0, 0)");
        Debug.Log("\n2. Child mesh/collider has local position offset");
        Debug.Log("   └─ Solution: Move offset to parent CharacterController.center instead");
        Debug.Log("\n3. Child has negative scale or rotation");
        Debug.Log("   └─ Solution: Reset scale to (1, 1, 1) and rotation to (0, 0, 0)");
        Debug.Log("\n💡 Tip: In Unity, CharacterController.center offset + Transform.position = actual collision volume");
    }
}
