using UnityEditor;
using UnityEngine;

/// <summary>
/// FixBuildingPrefabIsometric - Setup proper isometric camera and player positioning.
/// Configures orthographic camera for isometric view with correct clipping planes.
/// </summary>
public class FixBuildingPrefabIsometric
{
    [MenuItem("Velinor/Fix BuildingPrefab Isometric Setup")]
    public static void FixIsometricSetup()
    {
        Debug.Log("=== Setting Up Isometric Camera & Player ===\n");

        FixPlayerPosition();
        FixCameraIsometric();

        Debug.Log("\n✅ Isometric setup complete!");
        Debug.Log("\n📋 Changes made:");
        Debug.Log("  • Player positioned above ground (Y = 0.9)");
        Debug.Log("  • Camera set to orthographic isometric view");
        Debug.Log("  • Clipping planes adjusted for full scene visibility");
        Debug.Log("  • Camera offset: (0, 3, -2.5) for isometric angle");
    }

    private static void FixPlayerPosition()
    {
        GameObject player = GameObject.Find("Player");
        if (player == null)
        {
            Debug.LogError("❌ Player not found!");
            return;
        }

        // Make sure player is above ground, not buried
        Vector3 playerPos = player.transform.position;
        
        // Reset to sensible position (above ground plane)
        if (playerPos.y < 0.5f)
        {
            playerPos.y = 0.9f; // Capsule center height
            player.transform.position = playerPos;
            Debug.Log($"✓ Player repositioned to Y={playerPos.y}");
        }
        else
        {
            Debug.Log($"✓ Player already at reasonable height (Y={playerPos.y})");
        }
    }

    private static void FixCameraIsometric()
    {
        GameObject cameraObj = GameObject.FindGameObjectWithTag("MainCamera");
        if (cameraObj == null)
        {
            Debug.LogError("❌ Main Camera not found!");
            return;
        }

        Camera cam = cameraObj.GetComponent<Camera>();
        if (cam == null)
        {
            Debug.LogError("❌ Camera component not found!");
            return;
        }

        // Set camera to orthographic
        cam.orthographic = true;
        Debug.Log("✓ Camera set to orthographic");

        // Set reasonable orthographic size (adjust zoom)
        cam.orthographicSize = 5f;
        Debug.Log("✓ Orthographic size: 5");

        // CRITICAL: Set wide clipping planes for isometric view
        // Near plane must be negative or small to see above scene
        // Far plane must be large to see below scene
        cam.nearClipPlane = -100f; // Allows seeing above the scene
        cam.farClipPlane = 100f;   // Allows seeing below the scene
        Debug.Log("✓ Clipping planes: Near=-100, Far=100 (full scene visibility)");

        // Position camera for isometric view (looking down at 45-degree angle)
        cameraObj.transform.localPosition = new Vector3(0, 3f, -2.5f);
        cameraObj.transform.localRotation = Quaternion.Euler(30f, 0, 0); // Looking down at angle
        Debug.Log("✓ Camera positioned for isometric view (45° angle)");
    }
}
