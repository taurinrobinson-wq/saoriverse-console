using UnityEditor;
using UnityEngine;

public class VelinorResourcesImporter
{
    [MenuItem("Velinor/Reimport JSON Resources")]
    public static void ReimportJsonResources()
    {
        Debug.Log("[Velinor] Reimporting JSON resources from Dialogue and Data folders...");
        
        // Force reimport of the new resources folders
        AssetDatabase.ImportAsset("Assets/Resources/Dialogue", ImportAssetOptions.ImportRecursive);
        AssetDatabase.ImportAsset("Assets/Resources/Data", ImportAssetOptions.ImportRecursive);
        
        Debug.Log("[Velinor] ✅ JSON resources reimported!");
        Debug.Log("[Velinor] If errors persist, try:");
        Debug.Log("  1. Window > TextMeshPro > Import TMP Essential Resources (if not done)");
        Debug.Log("  2. Delete Assets/Resources/Dialogue/.meta and Assets/Resources/Data/.meta files and reimport manually");
        Debug.Log("  3. Restart Unity");
    }

    [MenuItem("Velinor/Verify JSON Files")]
    public static void VerifyJsonFiles()
    {
        Debug.Log("[Velinor] Checking JSON file locations...");
        
        TextAsset storyJson = Resources.Load<TextAsset>("Dialogue/kaelen_confession_01");
        TextAsset stateJson = Resources.Load<TextAsset>("Data/npc_state");
        
        if (storyJson != null)
            Debug.Log("✅ kaelen_confession_01.json found in Resources/Dialogue/");
        else
            Debug.LogError("❌ kaelen_confession_01.json NOT found in Resources/Dialogue/");
        
        if (stateJson != null)
            Debug.Log("✅ npc_state.json found in Resources/Data/");
        else
            Debug.LogError("❌ npc_state.json NOT found in Resources/Data/");
    }
}
