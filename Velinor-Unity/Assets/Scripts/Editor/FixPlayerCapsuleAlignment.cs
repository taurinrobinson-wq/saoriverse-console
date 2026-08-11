using UnityEditor;
using UnityEngine;

/// <summary>
/// FixPlayerCapsuleAlignment - Fixes misalignment between visual mesh and CharacterController.
/// Resets CharacterController center offset and ensures visual mesh is at correct position.
/// </summary>
public class FixPlayerCapsuleAlignment
{
    [MenuItem("Velinor/Fix Player Capsule Alignment")]
    public static void FixAlignment()
    {
        GameObject player = GameObject.Find("Player");
        if (player == null)
        {
            Debug.LogError("❌ Player not found!");
            return;
        }

        Debug.Log("=== Fixing Player Capsule Alignment ===\n");

        var charController = player.GetComponent<CharacterController>();
        if (charController == null)
        {
            Debug.LogError("❌ CharacterController not found!");
            return;
        }

        // Show before state
        Debug.Log("BEFORE:");
        Debug.Log($"  CharacterController.center: {charController.center}");
        Debug.Log($"  Player position: {player.transform.position}");

        // FIX 1: Reset CharacterController center to (0, 0, 0)
        if (charController.center != Vector3.zero)
        {
            Vector3 oldCenter = charController.center;
            charController.center = Vector3.zero;
            Debug.Log($"\n✓ CharacterController.center reset from {oldCenter} to (0, 0, 0)");
        }

        // FIX 2: Adjust player position to compensate
        // If center was at (0, 0.9, 0), we need to raise the player by 0.9 units
        Vector3 playerPos = player.transform.position;
        if (playerPos.y < 0.5f)
        {
            playerPos.y = 0.9f;
            player.transform.position = playerPos;
            Debug.Log($"✓ Player position adjusted to Y={playerPos.y} (above ground)");
        }

        // FIX 3: Check all child objects for position/scale issues
        Debug.Log($"\n✓ Checking {player.transform.childCount} child objects...");
        foreach (Transform child in player.transform)
        {
            // Reset child local position if it has an unnecessary offset
            if (child.name.Contains("Armature") || child.name.Contains("Capsule") || child.name.Contains("Mesh"))
            {
                if (child.localPosition != Vector3.zero)
                {
                    Debug.Log($"  ⚠️  {child.name} has local position offset: {child.localPosition}");
                    Debug.Log($"     Resetting to (0, 0, 0)...");
                    child.localPosition = Vector3.zero;
                }

                // Check for negative scales
                if (child.localScale.x < 0 || child.localScale.y < 0 || child.localScale.z < 0)
                {
                    Debug.Log($"  ⚠️  {child.name} has negative scale: {child.localScale}");
                    child.localScale = new Vector3(
                        Mathf.Abs(child.localScale.x),
                        Mathf.Abs(child.localScale.y),
                        Mathf.Abs(child.localScale.z)
                    );
                    Debug.Log($"     Fixed to: {child.localScale}");
                }

                // Check for unwanted rotation
                if (child.localRotation != Quaternion.identity)
                {
                    Debug.Log($"  ⚠️  {child.name} has local rotation: {child.localRotation.eulerAngles}");
                    Debug.Log($"     Consider resetting to (0, 0, 0) if not intentional");
                }
            }
        }

        Debug.Log("\nAFTER:");
        Debug.Log($"  CharacterController.center: {charController.center}");
        Debug.Log($"  Player position: {player.transform.position}");

        Debug.Log("\n✅ Alignment fixed!");
        Debug.Log("\n💡 The visual mesh and CharacterController should now be at the same position.");
    }
}
