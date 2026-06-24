using UnityEditor;
using UnityEngine;

public class VelinorResourcesImporter
{
    [MenuItem("Velinor/Reimport JSON Resources")]
    public static void ReimportJsonResources()
    {
        Debug.Log("[Velinor] Reimporting JSON resources from velinor folder...");
        
        // Force reimport of the velinor resources folder
        AssetDatabase.ImportAsset("Assets/Resources/velinor", ImportAssetOptions.ImportRecursive);
        
        Debug.Log("[Velinor] ✅ JSON resources reimported!");
        Debug.Log("[Velinor] If errors persist, try:");
        Debug.Log("  1. Window > TextMeshPro > Import TMP Essential Resources (if not done)");
        Debug.Log("  2. Delete Assets/Resources/velinor/.meta files and reimport manually");
        Debug.Log("  3. Restart Unity");
    }

    [MenuItem("Velinor/Verify JSON Files")]
    public static void VerifyJsonFiles()
    {
        Debug.Log("[Velinor] Checking JSON file locations...");
        
        TextAsset storyJson = Resources.Load<TextAsset>("velinor/stories/sample_story");
        TextAsset stateJson = Resources.Load<TextAsset>("velinor/data/npc_state");
        
        if (storyJson != null)
            Debug.Log("✅ sample_story.json found");
        else
            Debug.LogError("❌ sample_story.json NOT found in Resources/velinor/stories/");
        
        if (stateJson != null)
            Debug.Log("✅ npc_state.json found");
        else
            Debug.LogError("❌ npc_state.json NOT found in Resources/velinor/data/");
    }
}
