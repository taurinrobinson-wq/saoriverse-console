using UnityEngine;

#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Velinor.Core
{
    /// <summary>
    /// LayerSetup - Automatically creates required layers for market scene
    /// 
    /// Run this FIRST before running SceneLayerManager.OrganizeMarketScene()
    /// </summary>
    public class LayerSetup
    {
        #if UNITY_EDITOR

        [MenuItem("Velinor/Scene Setup/Create Required Layers", false, 10)]
        public static void CreateRequiredLayers()
        {
            Debug.Log("🔧 Creating required layers...");

            // Get the tag manager (layers are stored here too)
            SerializedObject tagManager = new SerializedObject(AssetDatabase.LoadMainAssetAtPath("ProjectSettings/TagManager.asset"));
            SerializedProperty layers = tagManager.FindProperty("layers");

            // Define required layers
            var requiredLayers = new System.Collections.Generic.Dictionary<int, string>
            {
                { 9, "Background" },
                { 10, "Midground" },
                { 11, "Foreground" },
                { 12, "Effects" }
            };

            bool anyCreated = false;

            foreach (var layer in requiredLayers)
            {
                int layerIndex = layer.Key;
                string layerName = layer.Value;

                SerializedProperty layerSP = layers.GetArrayElementAtIndex(layerIndex);
                
                if (layerSP.stringValue == "")
                {
                    layerSP.stringValue = layerName;
                    anyCreated = true;
                    Debug.Log($"✅ Created Layer {layerIndex}: {layerName}");
                }
                else if (layerSP.stringValue != layerName)
                {
                    Debug.LogWarning($"⚠️ Layer {layerIndex} already exists as '{layerSP.stringValue}', expected '{layerName}'");
                }
                else
                {
                    Debug.Log($"✅ Layer {layerIndex}: {layerName} (already exists)");
                }
            }

            if (anyCreated)
            {
                tagManager.ApplyModifiedProperties();
                Debug.Log("✅ All required layers created successfully!");
            }
            else
            {
                Debug.Log("✅ All required layers already exist!");
            }

            Debug.Log("\n📋 Next step: Go to Velinor → Scene Setup → Organize Market Scene");
        }

        #endif
    }
}
