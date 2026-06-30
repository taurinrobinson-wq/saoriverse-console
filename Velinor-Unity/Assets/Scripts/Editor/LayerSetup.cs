using UnityEngine;

#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.SceneManagement;
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
                tagManager.ApplyModifiedPropertiesWithoutUndo();
                Debug.Log("✅ All required layers created successfully!");
                
                // Verify layers were created
                EditorApplication.delayCall += VerifyLayers;
            }
            else
            {
                Debug.Log("✅ All required layers already exist!");
                VerifyLayers();
            }

            Debug.Log("\n📋 Next step: Go to Velinor → Scene Setup → Organize Market Scene");
        }

        private static void VerifyLayers()
        {
            Debug.Log("\n✅ LAYER VERIFICATION:");
            Debug.Log($"  Background: {(LayerMask.NameToLayer("Background") != -1 ? "✓ Found" : "✗ Missing")}");
            Debug.Log($"  Midground:  {(LayerMask.NameToLayer("Midground") != -1 ? "✓ Found" : "✗ Missing")}");
            Debug.Log($"  Foreground: {(LayerMask.NameToLayer("Foreground") != -1 ? "✓ Found" : "✗ Missing")}");
            Debug.Log($"  Effects:    {(LayerMask.NameToLayer("Effects") != -1 ? "✓ Found" : "✗ Missing")}");
        }

        #endif
    }
}
