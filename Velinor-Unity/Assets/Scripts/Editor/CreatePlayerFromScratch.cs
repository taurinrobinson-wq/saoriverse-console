using UnityEditor;
using UnityEngine;
using UnityEngine.InputSystem;

namespace StarterAssets
{
    /// <summary>
    /// CreatePlayerFromScratch - Builds a complete, fully-configured Player GameObject.
    /// This bypasses all legacy issues by creating a clean, working setup.
    /// 
    /// Usage: Delete the old Player, then run this: Velinor > Create Fresh Player
    /// </summary>
    public class CreatePlayerFromScratch
    {
        [MenuItem("Velinor/Create Fresh Player")]
        public static void CreatePlayer()
        {
            Debug.Log("=== Creating Fresh Player from Scratch ===\n");

            // Step 1: Delete old Player if it exists
            GameObject oldPlayer = GameObject.Find("Player");
            if (oldPlayer != null)
            {
                Debug.Log("❌ Old Player found - deleting it first...");
                Object.DestroyImmediate(oldPlayer);
                Debug.Log("✓ Old Player deleted");
            }

            // Step 2: Create root Player GameObject
            GameObject player = new GameObject("Player");
            player.tag = "Player";
            Debug.Log("✓ Created Player root GameObject");

            // Step 3: Add CharacterController (movement physics)
            CharacterController charController = player.AddComponent<CharacterController>();
            charController.height = 1.8f;
            charController.radius = 0.5f;
            charController.center = Vector3.zero;  // NO OFFSET!
            charController.slopeLimit = 45f;
            charController.stepOffset = 0.3f;
            Debug.Log("✓ Added CharacterController (height=1.8, radius=0.5, center=0,0,0)");

            // Step 4: Add VelinorPlayerController (movement + interaction logic)
            VelinorPlayerController playerController = player.AddComponent<VelinorPlayerController>();
            playerController.MoveSpeed = 2.0f;
            playerController.SpeedChangeRate = 10.0f;
            playerController.GroundedOffset = -0.14f;
            playerController.GroundedRadius = 0.28f;
            playerController.GroundLayers = LayerMask.GetMask("Default");
            playerController.CameraHeight = 0.93f;
            playerController.TopClamp = 70.0f;
            playerController.BottomClamp = -30.0f;
            playerController.LookSensitivity = new Vector2(7.5f, 5.0f);
            Debug.Log("✓ Added VelinorPlayerController with default settings");

            // Step 5: Add VelinorStarterAssetsInputs (input handling)
            VelinorStarterAssetsInputs inputHandler = player.AddComponent<VelinorStarterAssetsInputs>();
            Debug.Log("✓ Added VelinorStarterAssetsInputs");

            // Step 6: Add PlayerInput (for Input System)
            PlayerInput playerInput = player.AddComponent<PlayerInput>();
            playerInput.defaultActionMap = "Player";
            
            // Try to find the InputActionAsset
            string[] inputAssetGuids = AssetDatabase.FindAssets("InputSystem_Actions t:InputActionAsset");
            if (inputAssetGuids.Length > 0)
            {
                string inputAssetPath = AssetDatabase.GUIDToAssetPath(inputAssetGuids[0]);
                InputActionAsset inputAsset = AssetDatabase.LoadAssetAtPath<InputActionAsset>(inputAssetPath);
                if (inputAsset != null)
                {
                    playerInput.actions = inputAsset;
                    Debug.Log($"✓ PlayerInput configured with InputActionAsset");
                }
            }
            Debug.Log("✓ Added PlayerInput component");

            // Step 7: Position player above ground
            player.transform.position = new Vector3(0, 0.9f, 0);
            Debug.Log("✓ Player positioned at (0, 0.9, 0)");

            // Step 8: Create and configure Main Camera
            GameObject cameraObj = new GameObject("Main Camera");
            cameraObj.tag = "MainCamera";
            cameraObj.transform.SetParent(player.transform);
            cameraObj.transform.localPosition = new Vector3(0, 0.8f, -2.5f);  // Third-person offset
            cameraObj.transform.localRotation = Quaternion.Euler(0, 0, 0);
            Debug.Log("✓ Created Main Camera as child of Player");

            Camera cam = cameraObj.AddComponent<Camera>();
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.2f, 0.2f, 0.2f, 1f);
            cam.nearClipPlane = 0.3f;
            cam.farClipPlane = 1000f;
            cam.orthographic = false;  // Perspective camera
            Debug.Log("✓ Camera configured (perspective, near=0.3, far=1000)");

            AudioListener audioListener = cameraObj.AddComponent<AudioListener>();
            Debug.Log("✓ Added AudioListener to camera");

            // Step 9: Add visual representation (optional debug capsule)
            GameObject visualMesh = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            visualMesh.name = "VisualMesh";
            visualMesh.transform.SetParent(player.transform);
            visualMesh.transform.localPosition = Vector3.zero;
            visualMesh.transform.localScale = new Vector3(1, 1, 1);
            
            // Remove the collider from the visual mesh (we use CharacterController instead)
            Collider visualCollider = visualMesh.GetComponent<Collider>();
            if (visualCollider != null)
            {
                Object.DestroyImmediate(visualCollider);
            }
            Debug.Log("✓ Added visual capsule mesh");

            Debug.Log("\n✅ Fresh Player Created Successfully!");
            Debug.Log("\n📋 Player Hierarchy:");
            Debug.Log("  Player (root)");
            Debug.Log("    ├─ CharacterController");
            Debug.Log("    ├─ VelinorPlayerController");
            Debug.Log("    ├─ VelinorStarterAssetsInputs");
            Debug.Log("    ├─ PlayerInput");
            Debug.Log("    ├─ Main Camera");
            Debug.Log("    │  └─ Camera + AudioListener");
            Debug.Log("    └─ VisualMesh (debug capsule)");

            Debug.Log("\n🎮 Ready to Play!");
            Debug.Log("   • WASD: Always move (camera-relative)");
            Debug.Log("   • Right-click + Mouse: Look around");
            Debug.Log("   • Left-click/E: Interact");
            Debug.Log("   • Cursor visible by default, locks on right-click");

            Selection.activeGameObject = player;
        }
    }
}
