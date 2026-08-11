using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

/// <summary>
/// FixBuildingPrefabPlayer - Comprehensive repair for BuildingPrefab player movement issues.
/// 
/// PROBLEM: Two critical components were disabled (m_Enabled: 0) in the scene, breaking all movement.
/// SOLUTION: This script re-enables them and ensures proper input system configuration.
/// 
/// Usage: Go to Velinor > Fix BuildingPrefab Player in the menu while BuildingPrefab scene is open.
/// </summary>
public class FixBuildingPrefabPlayer
{
    [MenuItem("Velinor/Fix BuildingPrefab Player Movement")]
    public static void FixPlayer()
    {
        Debug.Log("=== Fixing BuildingPrefab Player Movement ===\n");

        // Find the Player GameObject
        GameObject player = GameObject.Find("Player");
        if (player == null)
        {
            Debug.LogError("❌ Cannot find Player GameObject in scene!");
            return;
        }

        Debug.Log("✓ Found Player GameObject");

        // 1. Ensure CharacterController exists and is configured
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
            Debug.Log("✓ CharacterController exists");
        }

        // 2. Ensure VelinorStarterAssetsInputs exists and is ENABLED
        StarterAssets.VelinorStarterAssetsInputs inputs = player.GetComponent<StarterAssets.VelinorStarterAssetsInputs>();
        if (inputs == null)
        {
            inputs = player.AddComponent<StarterAssets.VelinorStarterAssetsInputs>();
            Debug.Log("✓ Added VelinorStarterAssetsInputs");
        }
        
        if (!inputs.enabled)
        {
            inputs.enabled = true;
            Debug.Log("✓ ENABLED VelinorStarterAssetsInputs (was DISABLED!)");
        }
        else
        {
            Debug.Log("✓ VelinorStarterAssetsInputs already enabled");
        }

        // 3. Ensure VelinorPlayerController exists and is ENABLED
        StarterAssets.VelinorPlayerController playerController = player.GetComponent<StarterAssets.VelinorPlayerController>();
        if (playerController == null)
        {
            playerController = player.AddComponent<StarterAssets.VelinorPlayerController>();
            playerController.MoveSpeed = 3f;
            playerController.GroundLayers = LayerMask.GetMask("Default");
            Debug.Log("✓ Added VelinorPlayerController");
        }

        if (!playerController.enabled)
        {
            playerController.enabled = true;
            Debug.Log("✓ ENABLED VelinorPlayerController (was DISABLED!)");
        }
        else
        {
            Debug.Log("✓ VelinorPlayerController already enabled");
        }

        // 4. Ensure PlayerInput exists and is properly configured
#if ENABLE_INPUT_SYSTEM
        PlayerInput playerInput = player.GetComponent<PlayerInput>();
        if (playerInput == null)
        {
            playerInput = player.AddComponent<PlayerInput>();
            Debug.Log("✓ Added PlayerInput");
        }
        
        // Load and assign the InputActionAsset
        InputActionAsset inputActionsAsset = AssetDatabase.LoadAssetAtPath<InputActionAsset>(
            "Assets/StarterAssets/InputSystem_Actions.inputactions");
        
        if (inputActionsAsset != null)
        {
            playerInput.actions = inputActionsAsset;
            playerInput.defaultControlScheme = "KeyboardMouse";
            playerInput.defaultActionMap = "Player";
            playerInput.notificationBehavior = PlayerNotifications.InvokeUnityEvents;
            
            if (!playerInput.enabled)
            {
                playerInput.enabled = true;
                Debug.Log("✓ ENABLED PlayerInput (was DISABLED!)");
            }
            
            Debug.Log("✓ PlayerInput configured with InputActionAsset");
        }
        else
        {
            Debug.LogWarning("⚠ Could not find InputSystem_Actions.inputactions - Input System may not work correctly");
        }
#else
        Debug.LogWarning("⚠ Input System not enabled in project (ENABLE_INPUT_SYSTEM not defined). Using old Input API.");
#endif

        // 5. Find or create Main Camera
        GameObject mainCam = GameObject.FindGameObjectWithTag("MainCamera");
        if (mainCam == null)
        {
            mainCam = new GameObject("Main Camera");
            mainCam.tag = "MainCamera";
            mainCam.transform.SetParent(player.transform);
            mainCam.transform.localPosition = new Vector3(0, 0.93f, 0); // First-person head position

            Camera cam = mainCam.AddComponent<Camera>();
            cam.nearClipPlane = 0.3f;
            cam.farClipPlane = 1000f;

            mainCam.AddComponent<AudioListener>();
            Debug.Log("✓ Created Main Camera");
        }
        else
        {
            Debug.Log("✓ Main Camera already exists");
            
            // Ensure it's a child of player for first-person
            if (mainCam.transform.parent != player.transform)
            {
                mainCam.transform.SetParent(player.transform);
                mainCam.transform.localPosition = new Vector3(0, 0.93f, 0);
                Debug.Log("✓ Repositioned Main Camera to player");
            }
        }

        // 6. Ground layer check
        if (playerController.GroundLayers == 0)
        {
            playerController.GroundLayers = LayerMask.GetMask("Default");
            Debug.Log("✓ Set GroundLayers to 'Default'");
        }

        // 7. Final verification
        Debug.Log("\n=== VERIFICATION ===");
        Debug.Log($"CharacterController enabled: {charController.enabled}");
        Debug.Log($"VelinorStarterAssetsInputs enabled: {inputs.enabled}");
        Debug.Log($"VelinorPlayerController enabled: {playerController.enabled}");
#if ENABLE_INPUT_SYSTEM
        Debug.Log($"PlayerInput enabled: {playerInput.enabled}");
        Debug.Log($"PlayerInput has InputActionAsset: {playerInput.actions != null}");
#endif

        Debug.Log("\n✅ BuildingPrefab Player is now FIXED!");
        Debug.Log("\n📋 What was wrong:");
        Debug.Log("  • VelinorStarterAssetsInputs was DISABLED → Input not being read");
        Debug.Log("  • VelinorPlayerController was DISABLED → Movement code not running");
        Debug.Log("  • PlayerInput may have been misconfigured → Input System couldn't work");
        
        Debug.Log("\n🎮 Controls:");
        Debug.Log("  • WASD = Move");
        Debug.Log("  • Mouse = Look around");
        Debug.Log("  • ESC = Unlock cursor");
        Debug.Log("  • E = Interact with NPCs");

        // Mark scene as dirty so changes are saved
        EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
    }
}
