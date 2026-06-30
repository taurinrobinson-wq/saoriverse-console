using UnityEngine;

#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Velinor.Core
{
    /// <summary>
    /// SceneLayerManager - Helper utility for managing scene depth layers
    /// 
    /// Usage:
    /// 1. Select any GameObject in scene
    /// 2. Right-click and use "Velinor/Assign to Layer..." options
    /// 3. Or drag objects into appropriate root containers
    /// 
    /// Layers needed:
    /// - Layer 9: Background
    /// - Layer 10: Midground  
    /// - Layer 11: Foreground
    /// - Layer 12: Effects
    /// </summary>
    public class SceneLayerManager : MonoBehaviour
    {
        /// <summary>
        /// Automatically organize scene for market view
        /// Call this from EditorGUI or implement as an initialization step
        /// </summary>
        public static void OrganizeMarketScene()
        {
            #if UNITY_EDITOR

            // Create root containers if they don't exist
            GameObject background = FindOrCreateContainer("Background");
            GameObject midground = FindOrCreateContainer("Midground");
            GameObject foreground = FindOrCreateContainer("Foreground");
            GameObject characters = FindOrCreateContainer("Characters");
            GameObject effects = FindOrCreateContainer("Effects");
            GameObject managers = FindOrCreateContainer("Managers");

            // Assign layers
            SetLayerRecursive(background, LayerMask.NameToLayer("Background"));
            SetLayerRecursive(midground, LayerMask.NameToLayer("Midground"));
            SetLayerRecursive(foreground, LayerMask.NameToLayer("Foreground"));
            SetLayerRecursive(characters, LayerMask.NameToLayer("Default"));
            SetLayerRecursive(effects, LayerMask.NameToLayer("Effects"));
            SetLayerRecursive(managers, LayerMask.NameToLayer("Default"));

            Debug.Log("✅ Market scene structure created and organized!");

            #endif
        }

        private static GameObject FindOrCreateContainer(string name)
        {
            Transform existing = GameObject.Find(name)?.transform;
            if (existing != null) return existing.gameObject;

            GameObject container = new GameObject(name);
            container.tag = "SceneContainer";
            return container;
        }

        private static void SetLayerRecursive(GameObject obj, int layer)
        {
            if (obj == null) return;
            obj.layer = layer;
            foreach (Transform child in obj.transform)
            {
                SetLayerRecursive(child.gameObject, layer);
            }
        }

        /// <summary>
        /// Get all objects in a specific layer (useful for debugging scene structure)
        /// </summary>
        public static GameObject[] GetObjectsInLayer(string layerName)
        {
            int layer = LayerMask.NameToLayer(layerName);
            var allObjects = FindObjectsOfType<GameObject>();
            var layerObjects = System.Array.FindAll(allObjects, obj => obj.layer == layer);
            return layerObjects;
        }

        /// <summary>
        /// Print scene structure to console for verification
        /// </summary>
        public static void PrintSceneStructure()
        {
            Debug.Log("=== MARKET SCENE STRUCTURE ===");
            Debug.Log($"Background objects: {GetObjectsInLayer("Background").Length}");
            Debug.Log($"Midground objects: {GetObjectsInLayer("Midground").Length}");
            Debug.Log($"Foreground objects: {GetObjectsInLayer("Foreground").Length}");
            Debug.Log($"Effect objects: {GetObjectsInLayer("Effects").Length}");
            Debug.Log("==============================");
        }
    }

    #if UNITY_EDITOR

    public class SceneLayerManagerMenu
    {
        [MenuItem("Velinor/Scene Setup/Organize Market Scene")]
        public static void OrganizeMarketSceneMenu()
        {
            SceneLayerManager.OrganizeMarketScene();
        }

        [MenuItem("Velinor/Scene Setup/Print Scene Structure")]
        public static void PrintSceneStructureMenu()
        {
            SceneLayerManager.PrintSceneStructure();
        }

        [MenuItem("Velinor/Assign to Layer/Background", false, 20)]
        public static void AssignToBackground()
        {
            AssignSelectionToLayer("Background");
        }

        [MenuItem("Velinor/Assign to Layer/Midground", false, 21)]
        public static void AssignToMidground()
        {
            AssignSelectionToLayer("Midground");
        }

        [MenuItem("Velinor/Assign to Layer/Foreground", false, 22)]
        public static void AssignToForeground()
        {
            AssignSelectionToLayer("Foreground");
        }

        [MenuItem("Velinor/Assign to Layer/Effects", false, 23)]
        public static void AssignToEffects()
        {
            AssignSelectionToLayer("Effects");
        }

        private static void AssignSelectionToLayer(string layerName)
        {
            int layer = LayerMask.NameToLayer(layerName);
            foreach (GameObject obj in Selection.gameObjects)
            {
                SetLayerRecursive(obj, layer);
            }
            Debug.Log($"✅ Selected objects assigned to layer '{layerName}'");
        }

        private static void SetLayerRecursive(GameObject obj, int layer)
        {
            if (obj == null) return;
            obj.layer = layer;
            foreach (Transform child in obj.transform)
            {
                SetLayerRecursive(child.gameObject, layer);
            }
        }
    }

    #endif
}
