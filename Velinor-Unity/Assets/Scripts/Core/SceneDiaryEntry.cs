using UnityEngine;
using UnityEngine.SceneManagement;
#if UNITY_EDITOR
using UnityEditor.SceneManagement;
#endif

/// <summary>
/// Triggers a diary entry when a scene loads for the first time.
/// Useful for player observations and scene-based narrative moments.
/// 
/// Inspector Features:
/// - Drag Scene File: Drop a scene asset to auto-populate the Diary Entry Key
/// - Diary Entry Key: Auto-generated as {sceneName}_first_visit or manually set
/// - Trigger Condition: "first_visit_only" (default) or "always"
/// - Required Flag: Optional condition that must be met (e.g., "marketplace_visited")
/// - Reset Button (Editor Only): Manually clear the trigger flag for testing
/// </summary>
public class SceneDiaryEntry : MonoBehaviour
{
    [SerializeField] private Object sceneAsset;
    [SerializeField] private string diaryEntryKey = "";
    [SerializeField] private string triggerCondition = "first_visit_only";
    [SerializeField] private string requiredFlag = "";
    
    [Space(10)]
    [SerializeField] private bool resetFlagInEditor = false;
    [SerializeField] private string debugFlagName = "";

    private string FlagKey => $"{gameObject.scene.name}_diary_{diaryEntryKey}_triggered";

    private void OnEnable()
    {
        SceneManager.sceneLoaded += OnSceneLoaded;
        
        #if UNITY_EDITOR
        debugFlagName = FlagKey;
        #endif
        
        Debug.Log($"[SceneDiaryEntry] OnEnable() called. FlagKey: {FlagKey}");
    }

    private void OnDisable()
    {
        SceneManager.sceneLoaded -= OnSceneLoaded;
    }
    
    private void Start()
    {
        // Handle the case where the scene is already loaded (most common)
        Debug.Log($"[SceneDiaryEntry] Start() called. Current scene: {gameObject.scene.name}");
        TriggerDiaryEntry();
    }

    #if UNITY_EDITOR
    private void OnValidate()
    {
        // Auto-generate diary entry key from scene asset if provided
        if (sceneAsset != null)
        {
            string assetPath = UnityEditor.AssetDatabase.GetAssetPath(sceneAsset);
            if (assetPath.EndsWith(".unity"))
            {
                string sceneName = System.IO.Path.GetFileNameWithoutExtension(assetPath);
                string expectedKey = $"{sceneName}_first_visit";
                
                // Only auto-populate if the key is empty
                if (string.IsNullOrEmpty(diaryEntryKey))
                {
                    diaryEntryKey = expectedKey;
                    Debug.Log($"[SceneDiaryEntry] Auto-generated diary key from scene: {diaryEntryKey}");
                }
            }
        }

        // Reset flag if toggled in editor
        if (resetFlagInEditor)
        {
            resetFlagInEditor = false;
            ResetFlag();
        }
    }
    #endif

    private void OnSceneLoaded(Scene scene, LoadSceneMode mode)
    {
        // Ignore if this isn't the target scene
        if (scene.name != gameObject.scene.name)
            return;

        TriggerDiaryEntry();
    }

    public void TriggerDiaryEntry()
    {
        Debug.Log($"[SceneDiaryEntry] TriggerDiaryEntry() called. Entry Key: '{diaryEntryKey}'");
        
        // Validate entry key
        if (string.IsNullOrEmpty(diaryEntryKey))
        {
            Debug.LogWarning("[SceneDiaryEntry] No diary entry key configured!");
            return;
        }

        // Check if this should only trigger once
        if (triggerCondition == "first_visit_only" && PlayerPrefs.HasKey(FlagKey))
        {
            Debug.Log($"[SceneDiaryEntry] Entry '{diaryEntryKey}' already triggered in {gameObject.scene.name}. Skipping.");
            return;
        }

        // Check required flag condition if specified
        if (!string.IsNullOrEmpty(requiredFlag) && !PlayerPrefs.HasKey(requiredFlag))
        {
            Debug.Log($"[SceneDiaryEntry] Required flag '{requiredFlag}' not met. Skipping entry '{diaryEntryKey}'.");
            return;
        }

        // Validate DiaryManager exists
        if (DiaryManager.Instance == null)
        {
            Debug.LogError("[SceneDiaryEntry] DiaryManager.Instance is null! Make sure DiaryManager exists in the scene.");
            return;
        }

        // Get the diary content
        string content = DiaryEntriesMapping.GetEntry(diaryEntryKey);
        if (string.IsNullOrEmpty(content))
        {
            Debug.LogWarning($"[SceneDiaryEntry] Entry key '{diaryEntryKey}' not found in DiaryEntriesMapping!");
            return;
        }

        // Add the entry to the diary
        DiaryManager.Instance.AddEntry(content);
        Debug.Log($"[SceneDiaryEntry] ✓ Successfully added diary entry: '{diaryEntryKey}' in scene '{gameObject.scene.name}'");

        // Mark as triggered
        if (triggerCondition == "first_visit_only")
        {
            PlayerPrefs.SetInt(FlagKey, 1);
            PlayerPrefs.Save();
            Debug.Log($"[SceneDiaryEntry] Saved trigger flag: {FlagKey}");
        }
    }

    /// <summary>
    /// Manually reset the trigger flag. Useful for testing.
    /// Called automatically when resetFlagInEditor is toggled in editor.
    /// </summary>
    public void ResetFlag()
    {
        if (PlayerPrefs.HasKey(FlagKey))
        {
            PlayerPrefs.DeleteKey(FlagKey);
            PlayerPrefs.Save();
            Debug.Log($"[SceneDiaryEntry] Reset flag for '{diaryEntryKey}' in scene '{gameObject.scene.name}'");
        }
        else
        {
            Debug.Log($"[SceneDiaryEntry] No flag to reset for '{diaryEntryKey}' in scene '{gameObject.scene.name}'");
        }
    }

    /// <summary>
    /// Static utility to reset a specific flag by scene and entry key.
    /// </summary>
    public static void ResetFlagByKey(string sceneName, string entryKey)
    {
        string flagKey = $"{sceneName}_diary_{entryKey}_triggered";
        if (PlayerPrefs.HasKey(flagKey))
        {
            PlayerPrefs.DeleteKey(flagKey);
            PlayerPrefs.Save();
            Debug.Log($"[SceneDiaryEntry] Reset flag: {flagKey}");
        }
    }

    /// <summary>
    /// Static utility to reset all diary trigger flags (useful for full game reset).
    /// </summary>
    public static void ResetAllDiaryFlags()
    {
        string[] allKeys = PlayerPrefs.GetString("_diary_keys", "").Split(',');
        foreach (string key in allKeys)
        {
            if (!string.IsNullOrEmpty(key) && key.Contains("_diary_"))
            {
                PlayerPrefs.DeleteKey(key);
            }
        }
        PlayerPrefs.Save();
        Debug.Log("[SceneDiaryEntry] Reset all diary trigger flags");
    }
}
