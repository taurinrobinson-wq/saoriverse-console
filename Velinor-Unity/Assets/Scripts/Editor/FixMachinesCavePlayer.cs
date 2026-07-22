using UnityEngine;
using UnityEditor;

/// <summary>
/// Fixes the Player GameObject in MachinesCave scene by ensuring all ThirdPersonController dependencies are properly set up.
/// Usage: Add this to any GameObject, then use the context menu option.
/// </summary>
public class FixMachinesCavePlayer : MonoBehaviour
{
    [ContextMenu("Fix Player GameObject")]
    public void FixPlayer()
    {
        Debug.Log("=== Fixing MachinesCave Player ===");

        // Find the Player GameObject
        GameObject player = GameObject.Find("Player");
        if (player == null)
        {
            Debug.LogError("❌ Cannot find Player GameObject in scene!");
            return;
        }

        Debug.Log("✓ Found Player GameObject");

        // 1. Ensure CharacterController exists
        CharacterController charController = player.GetComponent<CharacterController>();
        if (charController == null)
        {
            charController = player.AddComponent<CharacterController>();
            charController.height = 1.8f;
            charController.radius = 0.5f;
            charController.center = new Vector3(0, 0.9f, 0);
            Debug.Log("✓ Added CharacterController");
        }
        else
        {
            Debug.Log("✓ CharacterController already exists");
        }

        // 2. Ensure StarterAssetsInputs exists
        StarterAssets.StarterAssetsInputs starterInput = player.GetComponent<StarterAssets.StarterAssetsInputs>();
        if (starterInput == null)
        {
            starterInput = player.AddComponent<StarterAssets.StarterAssetsInputs>();
            Debug.Log("✓ Added StarterAssetsInputs");
        }
        else
        {
            Debug.Log("✓ StarterAssetsInputs already exists");
        }

        // 3. Ensure ThirdPersonController exists and is configured
        StarterAssets.ThirdPersonController tpc = player.GetComponent<StarterAssets.ThirdPersonController>();
        if (tpc == null)
        {
            tpc = player.AddComponent<StarterAssets.ThirdPersonController>();
            Debug.Log("✓ Added ThirdPersonController");
        }
        else
        {
            Debug.Log("✓ ThirdPersonController already exists");
        }

        // 4. Create or find CinemachineCameraTarget
        Transform camTarget = player.transform.Find("CinemachineCameraTarget");
        if (camTarget == null)
        {
            GameObject camTargetObj = new GameObject("CinemachineCameraTarget");
            camTargetObj.transform.SetParent(player.transform);
            camTargetObj.transform.localPosition = new Vector3(0, 0.6f, 0);
            camTargetObj.transform.localRotation = Quaternion.identity;
            camTarget = camTargetObj.transform;
            Debug.Log("✓ Created CinemachineCameraTarget");
        }
        else
        {
            Debug.Log("✓ CinemachineCameraTarget already exists");
        }

        // 5. Assign CinemachineCameraTarget to ThirdPersonController if not set
        if (tpc.CinemachineCameraTarget == null)
        {
            tpc.CinemachineCameraTarget = camTarget.gameObject;
            Debug.Log("✓ Assigned CinemachineCameraTarget to ThirdPersonController");
        }

        // 6. Set GroundLayers to "Default" layer if not set
        if (tpc.GroundLayers == 0)
        {
            tpc.GroundLayers = LayerMask.GetMask("Default");
            Debug.Log("✓ Set GroundLayers to Default");
        }

        // 7. Find or create Main Camera
        GameObject mainCam = GameObject.FindGameObjectWithTag("MainCamera");
        if (mainCam == null)
        {
            mainCam = new GameObject("Main Camera");
            mainCam.tag = "MainCamera";
            mainCam.transform.SetParent(player.transform);
            mainCam.transform.localPosition = new Vector3(0, 0.6f, 0);

            Camera cam = mainCam.AddComponent<Camera>();
            cam.nearClipPlane = 0.3f;
            cam.farClipPlane = 1000f;

            mainCam.AddComponent<AudioListener>();
            Debug.Log("✓ Created Main Camera");
        }
        else
        {
            Debug.Log("✓ Main Camera already exists");
        }

        // 8. Check for Animator
        Animator animator = player.GetComponent<Animator>();
        if (animator == null)
        {
            Debug.LogWarning("⚠ Player does not have Animator component. This may cause animation errors.");
        }
        else
        {
            Debug.Log("✓ Animator exists");
        }

        Debug.Log("\n🎮 Player setup complete! Errors should be resolved.");
        Debug.Log("If you still see errors, check:");
        Debug.Log("  - Input System is enabled in Project Settings > Player > Active Input Handling");
        Debug.Log("  - StarterAssets.inputactions is properly configured");
    }
}
