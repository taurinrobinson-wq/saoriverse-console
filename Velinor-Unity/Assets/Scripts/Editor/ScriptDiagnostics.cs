using UnityEditor;
using UnityEngine;
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
}
