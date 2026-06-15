using UnityEngine;
using System.IO;

public class DataLoadTest : MonoBehaviour
{
    void Start()
    {
        TestDataLoading();
    }

    void TestDataLoading()
    {
        Debug.Log("=== Velinor Data Loading Test ===");
        
        // Check if data folder exists
        string dataPath = Path.Combine(Application.dataPath, "Data/JSON");
        if (Directory.Exists(dataPath))
        {
            Debug.Log($"✅ Found data directory: {dataPath}");
            
            // List all JSON files
            string[] jsonFiles = Directory.GetFiles(dataPath, "*.json");
            Debug.Log($"✅ Found {jsonFiles.Length} JSON files:");
            foreach (string file in jsonFiles)
            {
                Debug.Log($"   • {Path.GetFileName(file)}");
            }
        }
        else
        {
            Debug.LogError($"❌ Data directory not found: {dataPath}");
        }
        
        // Check graphics
        string glyphPath = Path.Combine(Application.dataPath, "Graphics/Glyphs");
        if (Directory.Exists(glyphPath))
        {
            Debug.Log($"✅ Found glyphs directory: {glyphPath}");
            string[] glyphDirs = Directory.GetDirectories(glyphPath);
            Debug.Log($"✅ Found {glyphDirs.Length} glyph subdirectories");
        }
        else
        {
            Debug.LogError($"❌ Glyphs directory not found: {glyphPath}");
        }
        
        // Check backgrounds
        string bgPath = Path.Combine(Application.dataPath, "Graphics/Backgrounds");
        if (Directory.Exists(bgPath))
        {
            string[] bgFiles = Directory.GetFiles(bgPath, "*.png");
            string[] bgJpgs = Directory.GetFiles(bgPath, "*.jpg");
            Debug.Log($"✅ Found {bgFiles.Length + bgJpgs.Length} background images");
        }
        else
        {
            Debug.LogError($"❌ Backgrounds directory not found: {bgPath}");
        }
        
        Debug.Log("=== Test Complete ===");
    }
}
