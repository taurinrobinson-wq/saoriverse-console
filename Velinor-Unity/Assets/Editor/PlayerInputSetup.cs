using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.InputSystem;

public class PlayerInputSetup : EditorWindow
{
    [MenuItem("Tools/Setup Player Input")]
    public static void SetupPlayerInput()
    {
        Scene activeScene = EditorSceneManager.GetActiveScene();
        
        // Load the InputActions asset
        var inputActionsAsset = AssetDatabase.LoadAssetAtPath<InputActionAsset>(
            "Assets/StarterAssets/InputSystem_Actions.inputactions");
        
        if (inputActionsAsset == null)
        {
            EditorUtility.DisplayDialog("Error", "Could not find InputSystem_Actions.inputactions!\n\nMake sure it exists at:\nAssets/StarterAssets/InputSystem_Actions.inputactions", "OK");
            return;
        }

        // Find the player character
        var players = FindObjectsByType<CharacterController>();
        if (players.Length == 0)
        {
            EditorUtility.DisplayDialog("Error", "No CharacterController found in scene!", "OK");
            return;
        }

        int assignedCount = 0;
        foreach (CharacterController controller in players)
        {
            var playerInput = controller.GetComponent<PlayerInput>();
            if (playerInput != null)
            {
                playerInput.actions = inputActionsAsset;
                if (string.IsNullOrEmpty(playerInput.defaultControlScheme))
                {
                    playerInput.defaultControlScheme = "KeyboardMouse";
                }
                EditorUtility.SetDirty(playerInput);
                Debug.Log($"✓ Assigned InputActions to {controller.gameObject.name}");
                assignedCount++;
            }
        }

        if (assignedCount > 0)
        {
            EditorSceneManager.MarkSceneDirty(activeScene);
            EditorUtility.DisplayDialog("Success", $"Player Input setup complete!\n\nAssigned InputActions to {assignedCount} player(s).", "OK");
            Debug.Log($"✅ Player Input setup complete! ({assignedCount} player assigned)");
        }
        else
        {
            EditorUtility.DisplayDialog("Warning", "Found CharacterController but no PlayerInput component!", "OK");
        }
    }
}
