using UnityEngine;

namespace Velinor.Core
{
    /// <summary>
    /// MarketSceneSetup - Organizes layered market environment
    /// 
    /// SCENE STRUCTURE:
    /// MarketScene/
    /// ├── Background/          (Layer: 9 "Background") - Mountains, sky, horizon
    /// ├── Midground/           (Layer: 10 "Midground") - Market stalls, buildings
    /// ├── Foreground/          (Layer: 11 "Foreground") - Ground, immediate props
    /// ├── Characters/          (Layer: 0 "Default")    - Player and NPCs
    /// ├── Effects/             (Layer: 12 "Effects")   - Dust, particles, overlays
    /// └── Camera & Lighting/   (Layer: 0)              - Main camera, lights, managers
    /// 
    /// ASSET STRATEGY:
    /// - Background: Kyle's Rock Pack (distant), simple sky sphere
    /// - Midground: Mediterranean Ruins Kit (market stalls), scattered from Modular SciFi
    /// - Foreground: Ground plane, scattered rocks, immediate-proximity items
    /// 
    /// CAMERA SETUP:
    /// - Main camera at height ~1.5m (player eye level)
    /// - Positioned to show depth: see into market, horizon behind
    /// - Use Depth of Field on background for atmospheric depth
    /// </summary>
    public class MarketSceneSetup : MonoBehaviour
    {
        [Header("Scene References")]
        [SerializeField] private Transform backgroundRoot;
        [SerializeField] private Transform midgroundRoot;
        [SerializeField] private Transform foregroundRoot;
        [SerializeField] private Camera mainCamera;
        [SerializeField] private Light mainLight;

        [Header("Depth of Field Settings (For Future Post-Processing)")]
        // These settings are prepared for future post-processing implementation
        // Currently using built-in URP depth of field via camera

        [Header("Lighting")]
        [SerializeField] private Color duskColor = new Color(1f, 0.7f, 0.4f);
        [SerializeField] private float lightIntensity = 0.8f;
        [SerializeField] private Vector3 sunAngle = new Vector3(45f, 315f, 0f);

        private void OnEnable()
        {
            // Scene hierarchy can be organized in Editor, this ensures proper layer assignment
            AssignLayers();
            ConfigureCamera();
            ConfigureLighting();
        }

        private void AssignLayers()
        {
            // Ensure layers exist (they should be manually created in Project Settings > Layers)
            // Background (Layer 9), Midground (Layer 10), Foreground (Layer 11), Effects (Layer 12)

            if (backgroundRoot != null)
                SetLayerRecursive(backgroundRoot.gameObject, LayerMask.NameToLayer("Background"));

            if (midgroundRoot != null)
                SetLayerRecursive(midgroundRoot.gameObject, LayerMask.NameToLayer("Midground"));

            if (foregroundRoot != null)
                SetLayerRecursive(foregroundRoot.gameObject, LayerMask.NameToLayer("Foreground"));
        }

        private void SetLayerRecursive(GameObject obj, int layer)
        {
            if (obj == null) return;
            obj.layer = layer;
            foreach (Transform child in obj.transform)
            {
                SetLayerRecursive(child.gameObject, layer);
            }
        }

        private void ConfigureCamera()
        {
            if (mainCamera == null)
            {
                mainCamera = Camera.main;
                
                // If no Main Camera found, look for any camera
                if (mainCamera == null)
                {
                    mainCamera = FindAnyObjectByType<Camera>();
                }
                
                // If still no camera, create one
                if (mainCamera == null)
                {
                    GameObject cameraObj = new GameObject("Main Camera");
                    mainCamera = cameraObj.AddComponent<Camera>();
                    cameraObj.tag = "MainCamera";
                    cameraObj.AddComponent<AudioListener>();
                    Debug.Log("⚠️ No camera found. Created new Main Camera.");
                }
            }

            if (mainCamera == null) return;

            // Ensure MainCamera tag is set
            if (mainCamera.gameObject.tag != "MainCamera")
                mainCamera.gameObject.tag = "MainCamera";

            // ORTHOGRAPHIC SETUP for 2D parallax environment
            mainCamera.orthographic = true;
            mainCamera.orthographicSize = 5f; // Controls zoom level
            
            // Position camera for 2D parallax (Z depth handles sorting)
            mainCamera.transform.position = new Vector3(0, 0, -10f);
            mainCamera.transform.rotation = Quaternion.identity; // Face forward
            
            // Render settings for parallax layers
            mainCamera.cullingMask = -1; // Render all layers
            mainCamera.clearFlags = CameraClearFlags.SolidColor;
            mainCamera.backgroundColor = new Color(0.08f, 0.08f, 0.08f, 1f); // Neutral dark (RGB ~20/20/20)
            mainCamera.depth = 0;
            
            Debug.Log("✅ Camera configured (Orthographic, Size 5) at (0, 0, -10) for 2D parallax");
            Debug.Log("✅ MainCamera tag confirmed, cullingMask: all layers, background: neutral dark");
        }

        private void ConfigureLighting()
        {
            if (mainLight == null)
            {
                mainLight = FindAnyObjectByType<Light>();
            }

            if (mainLight == null) return;

            // Dusk lighting
            mainLight.color = duskColor;
            mainLight.intensity = lightIntensity;
            mainLight.transform.eulerAngles = sunAngle;
            mainLight.type = LightType.Directional;
            mainLight.shadows = LightShadows.Soft;
        }

        /// <summary>
        /// Helper: Position an object in a specific depth layer
        /// </summary>
        public void PlaceInLayer(GameObject obj, string layerName)
        {
            SetLayerRecursive(obj, LayerMask.NameToLayer(layerName));
        }

        /// <summary>
        /// Helper: Scale object for distance effect
        /// Use this to create visual distance between midground and background
        /// </summary>
        public void ScaleForDistance(GameObject obj, float distanceFactor)
        {
            // Distance factor: 1.0 = midground, 0.5 = distant, 0.3 = very distant
            obj.transform.localScale *= distanceFactor;
        }

        /// <summary>
        /// Verify camera configuration is correct for 2D parallax
        /// </summary>
        public void VerifyCamera()
        {
            Debug.Log("\n=== CAMERA VERIFICATION ===");
            
            Camera cam = Camera.main;
            if (cam == null)
            {
                cam = FindAnyObjectByType<Camera>();
            }

            if (cam == null)
            {
                Debug.LogError("❌ NO CAMERA FOUND in scene!");
                return;
            }

            bool allGood = true;

            // Check MainCamera tag
            if (cam.gameObject.tag != "MainCamera")
            {
                Debug.LogWarning($"❌ Camera missing MainCamera tag (current: {cam.gameObject.tag})");
                allGood = false;
            }
            else
            {
                Debug.Log("✅ MainCamera tag correct");
            }

            // Check orthographic
            if (!cam.orthographic)
            {
                Debug.LogWarning("❌ Camera is PERSPECTIVE (should be ORTHOGRAPHIC for 2D parallax)");
                allGood = false;
            }
            else
            {
                Debug.Log("✅ Camera is orthographic");
            }

            // Check orthographic size
            if (Mathf.Abs(cam.orthographicSize - 5f) > 0.1f)
            {
                Debug.LogWarning($"❌ OrthographicSize is {cam.orthographicSize} (should be ~5)");
                allGood = false;
            }
            else
            {
                Debug.Log($"✅ OrthographicSize: {cam.orthographicSize}");
            }

            // Check position
            Vector3 expectedPos = new Vector3(0, 0, -10f);
            if (Vector3.Distance(cam.transform.position, expectedPos) > 0.1f)
            {
                Debug.LogWarning($"❌ Camera position is {cam.transform.position} (should be ~{expectedPos})");
                allGood = false;
            }
            else
            {
                Debug.Log($"✅ Camera position: {cam.transform.position}");
            }

            // Check culling mask
            if (cam.cullingMask != -1)
            {
                Debug.LogWarning($"❌ Culling mask is {cam.cullingMask} (should be -1 to render all layers)");
                allGood = false;
            }
            else
            {
                Debug.Log("✅ Culling mask: all layers");
            }

            // Check clear flags
            if (cam.clearFlags != CameraClearFlags.SolidColor)
            {
                Debug.LogWarning($"❌ Clear flags are {cam.clearFlags} (should be SolidColor)");
                allGood = false;
            }
            else
            {
                Debug.Log("✅ Clear flags: SolidColor");
            }

            // Check background color
            Color expectedBg = new Color(0.08f, 0.08f, 0.08f, 1f);
            if (Vector4.Distance(cam.backgroundColor, expectedBg) > 0.05f)
            {
                Debug.LogWarning($"❌ Background color is {cam.backgroundColor} (should be neutral dark)");
            }
            else
            {
                Debug.Log($"✅ Background color: neutral dark");
            }

            Debug.Log("=== END VERIFICATION ===\n");
            
            if (allGood)
                Debug.Log("🎉 Camera is properly configured for 2D parallax!");
        }
    }
}
