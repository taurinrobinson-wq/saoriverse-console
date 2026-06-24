using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using System.IO;
using System.Reflection;

public class ScriptDiagnostics
{
    [MenuItem("Velinor/Diagnostics/Check Script References")]
    public static void CheckScriptReferences()
    {
        Debug.Log("🔍 Checking script references...");
        
        // Check if scripts can be found by their type names
        var types = new string[]
        {
            "SimplePlayerMovement",
            "NPCInteraction",
            "GlyphObject",
            "InteractionUI",
            "Interactable"
        };
        
        foreach (var typeName in types)
        {
            System.Type type = System.Type.GetType(typeName);
            if (type != null)
            {
                Debug.Log($"✅ {typeName} - FOUND");
            }
            else
            {
                Debug.LogError($"❌ {typeName} - NOT FOUND");
            }
        }
        
        // Check for compile errors
        Debug.Log("✅ Script diagnostic complete. Check console for any ❌ marks.");
    }
    
    [MenuItem("Velinor/Diagnostics/Force Recompile")]
    public static void ForceRecompile()
    {
        Debug.Log("🔄 Forcing script recompilation...");
        AssetDatabase.Refresh(ImportAssetOptions.ForceUpdate);
        Debug.Log("✅ Recompilation triggered. Wait for compiler to finish.");
    }
    
    [MenuItem("Velinor/Diagnostics/Clean Old Scenes")]
    public static void CleanOldScenes()
    {
        Debug.Log("🧹 Cleaning up old scene files with broken references...");
        
        string[] scenesToClean = {
            "Assets/Velinor.unity",
            "Assets/Scenes/TestScene.unity",
            "Assets/Scenes/GamplayScene.unity"
        };
        
        foreach (string scenePath in scenesToClean)
        {
            if (File.Exists(scenePath))
            {
                Debug.Log($"🗑️  Deleting {scenePath}");
                AssetDatabase.DeleteAsset(scenePath);
            }
        }
        
        Debug.Log("✅ Old scenes cleaned. Refresh will complete in a moment.");
        AssetDatabase.Refresh();
    }
}
