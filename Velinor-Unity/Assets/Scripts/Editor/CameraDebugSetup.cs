using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Velinor.Core;

namespace Velinor.Editor
{
    /// <summary>
    /// CameraDebugSetup - Debug and verify camera configuration
    /// Provides menu options to diagnose camera rendering issues
    /// </summary>
    public class CameraDebugSetup
    {
        [MenuItem("Velinor/Debug/Verify Camera Configuration")]
        public static void VerifyCameraConfiguration()
        {
            Debug.Log("\n========================================");
            Debug.Log("CAMERA CONFIGURATION DEBUG");
            Debug.Log("========================================\n");

            // Find or create MarketSceneSetup
            MarketSceneSetup setup = Object.FindAnyObjectByType<MarketSceneSetup>();
            if (setup != null)
            {
                setup.VerifyCamera();
            }
            else
            {
                // Manual verification without MarketSceneSetup
                Camera cam = Camera.main;
                if (cam == null)
                {
                    cam = Object.FindAnyObjectByType<Camera>();
                }

                if (cam == null)
                {
                    Debug.LogError("❌ NO CAMERA FOUND in scene!");
                    return;
                }

                Debug.Log($"Camera found: {cam.gameObject.name}");
                Debug.Log($"  Tag: {cam.gameObject.tag}");
                Debug.Log($"  Orthographic: {cam.orthographic}");
                Debug.Log($"  OrthographicSize: {cam.orthographicSize}");
                Debug.Log($"  Position: {cam.transform.position}");
                Debug.Log($"  Rotation: {cam.transform.rotation.eulerAngles}");
                Debug.Log($"  CullingMask: {cam.cullingMask}");
                Debug.Log($"  ClearFlags: {cam.clearFlags}");
                Debug.Log($"  BackgroundColor: {cam.backgroundColor}");
            }
        }

        [MenuItem("Velinor/Debug/Show Active Scene Info")]
        public static void ShowActiveSceneInfo()
        {
            Scene activeScene = SceneManager.GetActiveScene();
            
            Debug.Log("\n========================================");
            Debug.Log("ACTIVE SCENE INFO");
            Debug.Log("========================================");
            Debug.Log($"Scene Name: {activeScene.name}");
            Debug.Log($"Scene Path: {activeScene.path}");
            Debug.Log($"Is Loaded: {activeScene.isLoaded}");
            Debug.Log($"Root GameObjects Count: {activeScene.rootCount}");
            
            // List all root objects
            Debug.Log("\nRoot GameObjects:");
            GameObject[] roots = activeScene.GetRootGameObjects();
            foreach (GameObject root in roots)
            {
                Debug.Log($"  - {root.name} (Active: {root.activeInHierarchy})");
            }

            // Check for cameras
            Camera[] cameras = Object.FindObjectsByType<Camera>();
            Debug.Log($"\nCameras in scene: {cameras.Length}");
            foreach (Camera cam in cameras)
            {
                Debug.Log($"  - {cam.gameObject.name} (Tag: {cam.gameObject.tag}, Enabled: {cam.enabled})");
            }

            // Check for lights
            Light[] lights = Object.FindObjectsByType<Light>();
            Debug.Log($"\nLights in scene: {lights.Length}");
            foreach (Light light in lights)
            {
                Debug.Log($"  - {light.gameObject.name} (Type: {light.type}, Enabled: {light.enabled})");
            }

            // Check for AudioListener
            AudioListener[] listeners = Object.FindObjectsByType<AudioListener>();
            Debug.Log($"\nAudioListeners in scene: {listeners.Length}");

            // Check for AudioSource
            AudioSource[] sources = Object.FindObjectsByType<AudioSource>();
            Debug.Log($"\nAudioSources in scene: {sources.Length}");

            Debug.Log("========================================\n");
        }

        [MenuItem("Velinor/Debug/Fix Camera (Orthographic 2D Parallax)")]
        public static void FixCameraFor2DParallax()
        {
            Debug.Log("\nAttempting to fix camera for 2D parallax...");

            Camera cam = Camera.main;
            if (cam == null)
            {
                cam = Object.FindAnyObjectByType<Camera>();
            }

            if (cam == null)
            {
                Debug.LogError("❌ No camera found. Creating new Main Camera...");
                GameObject cameraObj = new GameObject("Main Camera");
                cam = cameraObj.AddComponent<Camera>();
                cam.gameObject.tag = "MainCamera";
                cam.gameObject.AddComponent<AudioListener>();
            }

            // Apply 2D parallax configuration
            cam.orthographic = true;
            cam.orthographicSize = 5f;
            cam.transform.position = new Vector3(0, 0, -10f);
            cam.transform.rotation = Quaternion.identity;
            cam.cullingMask = -1;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.08f, 0.08f, 0.08f, 1f);
            cam.depth = 0;
            cam.gameObject.tag = "MainCamera";

            Debug.Log("✅ Camera fixed for 2D parallax!");
            Debug.Log($"  Position: {cam.transform.position}");
            Debug.Log($"  Orthographic: {cam.orthographic}");
            Debug.Log($"  Size: {cam.orthographicSize}");

            EditorSceneManager.MarkSceneDirty(SceneManager.GetActiveScene());
        }

        [MenuItem("Velinor/Debug/Load Marketplace Scene")]
        public static void LoadMarketplaceScene()
        {
            string[] sceneGuids = AssetDatabase.FindAssets("Marketplace t:Scene");
            if (sceneGuids.Length > 0)
            {
                string scenePath = AssetDatabase.GUIDToAssetPath(sceneGuids[0]);
                EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
                Debug.Log($"✅ Loaded scene: {scenePath}");
            }
            else
            {
                Debug.LogError("❌ Marketplace scene not found. Please ensure it exists in the project.");
            }
        }
    }
}
