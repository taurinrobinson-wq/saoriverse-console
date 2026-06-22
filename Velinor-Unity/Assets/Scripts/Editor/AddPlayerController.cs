using UnityEditor;
using UnityEngine;
using StarterAssets;

public class AddPlayerController
{
    [MenuItem("Velinor/Add Player Controller to Scene")]
    public static void AddPlayerController()
    {
        // Find Player object
        GameObject player = GameObject.Find("Player");
        if (player == null)
        {
            Debug.LogError("❌ Player object not found in scene!");
            return;
        }

        Debug.Log("🎮 Setting up Player with controller...");

        // ===== ADD CHARACTER CONTROLLER =====
        if (player.GetComponent<CharacterController>() == null)
        {
            CharacterController cc = player.AddComponent<CharacterController>();
            cc.height = 1.8f;
            cc.radius = 0.3f;
            cc.center = new Vector3(0, 0.9f, 0);
            cc.slopeLimit = 45f;
            cc.stepOffset = 0.3f;
            Debug.Log("✅ Added CharacterController");
        }

        // ===== ADD INPUT HANDLER =====
        if (player.GetComponent<StarterAssetsInputs>() == null)
        {
            StarterAssetsInputs inputs = player.AddComponent<StarterAssetsInputs>();
            inputs.analogMovement = false;
            Debug.Log("✅ Added StarterAssetsInputs");
        }

        // ===== ADD PLAYER CONTROLLER =====
        if (player.GetComponent<VelinorPlayerController>() == null)
        {
            VelinorPlayerController controller = player.AddComponent<VelinorPlayerController>();
            controller.MoveSpeed = 5f;
            controller.GroundLayers = LayerMask.GetMask("Default");
            controller.GroundedOffset = -0.5f;
            controller.GroundedRadius = 0.3f;
            Debug.Log("✅ Added VelinorPlayerController");
        }

        // ===== SETUP CAMERA =====
        GameObject cameraObj = GameObject.Find("Main Camera");
        if (cameraObj != null)
        {
            cameraObj.transform.position = new Vector3(2f, 2.5f, -5f);
            cameraObj.transform.LookAt(player.transform.position + Vector3.up);
            Debug.Log("✅ Positioned Main Camera");
        }

        // ===== CREATE CAMERA TARGET =====
        VelinorPlayerController playerCtrl = player.GetComponent<VelinorPlayerController>();
        if (playerCtrl.CinemachineCameraTarget == null)
        {
            GameObject cameraTarget = new GameObject("CameraTarget");
            cameraTarget.transform.SetParent(player.transform);
            cameraTarget.transform.localPosition = new Vector3(0, 0.93f, 0);
            playerCtrl.CinemachineCameraTarget = cameraTarget;
            Debug.Log("✅ Created CameraTarget");
        }

        Debug.Log("🎮 Player controller setup complete!");
        Debug.Log("Use WASD to move, mouse to look around, Space to jump, Shift to sprint");
    }
}
