using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

public class SceneSetup : EditorWindow
{
    [MenuItem("Tools/Setup Scene - Fix Camera and Player")]
    public static void SetupScene()
    {
        Scene activeScene = EditorSceneManager.GetActiveScene();
        Debug.Log($"Setting up scene: {activeScene.name}");

        // Find all cameras in the scene
        Camera[] cameras = FindObjectsByType<Camera>();
        if (cameras.Length == 0)
        {
            EditorUtility.DisplayDialog("Error", "No cameras found in scene!", "OK");
            return;
        }

        // Set the first camera as Main Camera
        Camera mainCam = cameras[0];
        mainCam.gameObject.tag = "MainCamera";
        EditorUtility.SetDirty(mainCam.gameObject);
        Debug.Log($"✓ Set {mainCam.gameObject.name} as Main Camera");

        // Ensure camera is not clipped by near plane
        mainCam.nearClipPlane = 0.01f;
        EditorUtility.SetDirty(mainCam);

        // Find player character and ensure it's visible
        GameObject player = GameObject.FindGameObjectWithTag("Player");
        if (player == null)
        {
            // Try to find any object named "Player" or "ThirdPersonController"
            player = GameObject.Find("Player");
            if (player == null)
                player = GameObject.Find("ThirdPersonController");
            if (player == null)
                player = GameObject.Find("Velinor");
        }

        if (player != null)
        {
            // Enable all renderers on player
            Renderer[] renderers = player.GetComponentsInChildren<Renderer>();
            foreach (Renderer renderer in renderers)
            {
                if (!renderer.enabled)
                {
                    renderer.enabled = true;
                    EditorUtility.SetDirty(renderer.gameObject);
                }
            }
            Debug.Log($"✓ Enabled renderers on player: {player.name}");

            // Tag as Player if not already
            if (!player.CompareTag("Player"))
            {
                player.tag = "Player";
                EditorUtility.SetDirty(player);
            }

            // Position camera to look at player
            Vector3 playerPos = player.transform.position;
            mainCam.transform.position = playerPos + Vector3.up * 1.5f + Vector3.back * 5f;
            mainCam.transform.LookAt(playerPos + Vector3.up);
            EditorUtility.SetDirty(mainCam.gameObject);
            Debug.Log($"✓ Positioned camera to view player");
        }
        else
        {
            Debug.LogWarning("Could not find player in scene!");
        }

        // Find and enable any NPCs
        foreach (GameObject go in FindObjectsByType<GameObject>())
        {
            if (go.name.Contains("NPC") || go.name.Contains("Character"))
            {
                Renderer[] renderers = go.GetComponentsInChildren<Renderer>();
                foreach (Renderer renderer in renderers)
                {
                    if (!renderer.enabled)
                    {
                        renderer.enabled = true;
                        EditorUtility.SetDirty(renderer.gameObject);
                    }
                }
            }
        }

        EditorSceneManager.MarkSceneDirty(activeScene);
        EditorUtility.DisplayDialog("Success", "Scene setup complete!\n\n✓ Camera set to Main Camera\n✓ Player renderers enabled\n✓ NPCs made visible", "OK");
        Debug.Log("✅ Scene setup complete!");
    }
}
