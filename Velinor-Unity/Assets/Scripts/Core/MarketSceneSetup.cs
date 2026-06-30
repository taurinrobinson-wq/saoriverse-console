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

        [Header("Depth of Field Settings")]
        [SerializeField] private bool enableDepthOfField = true;
        [SerializeField] private float focusDistance = 15f;
        [SerializeField] private float aperture = 16f;

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
            }

            if (mainCamera == null) return;

            // Position camera for market view (can be adjusted in Editor)
            mainCamera.transform.position = new Vector3(0, 1.5f, -5f);
            mainCamera.transform.LookAt(new Vector3(0, 0, 10f));

            // Configure culling masks to render layers in correct order
            // This ensures proper z-buffer handling for depth layering
            mainCamera.cullingMask = ~(1 << LayerMask.NameToLayer("UI")); // Render everything except UI
        }

        private void ConfigureLighting()
        {
            if (mainLight == null)
            {
                mainLight = FindObjectOfType<Light>();
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
    }
}
