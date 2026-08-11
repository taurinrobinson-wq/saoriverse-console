using UnityEditor;
using UnityEngine;

/// <summary>
/// DisableIsometricCameraRotation - Disable camera rotation for isometric gameplay.
/// In isometric games, the camera typically doesn't rotate - it stays at a fixed angle.
/// </summary>
public class DisableIsometricCameraRotation
{
    [MenuItem("Velinor/Disable Isometric Camera Rotation")]
    public static void DisableCameraRotation()
    {
        GameObject player = GameObject.Find("Player");
        if (player == null)
        {
            Debug.LogError("❌ Player not found!");
            return;
        }

        var playerController = player.GetComponent<StarterAssets.VelinorPlayerController>();
        if (playerController == null)
        {
            Debug.LogError("❌ VelinorPlayerController not found!");
            return;
        }

        // Disable look sensitivity to prevent camera rotation
        playerController.LookSensitivity = Vector2.zero;
        Debug.Log("✓ Camera rotation disabled (LookSensitivity = 0)");
        Debug.Log("✓ Right-click + mouse will no longer rotate camera in isometric view");
        Debug.Log("\n💡 Tip: In isometric games, camera stays at fixed angle");
        Debug.Log("   Player still moves with WASD as normal");
    }
}
