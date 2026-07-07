#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;

public static class FixImportedMaterials
{
    [MenuItem("Tools/Fix Imported Materials")]
    public static void FixMaterialsMenu()
    {
        RunOnFolder("Assets/ImportedAssets");
    }

    [MenuItem("Tools/Fix Imported Materials/Run on Diagnosed Packs")]
    public static void FixOnDiagnosedPacks()
    {
        string[] folders = new string[] {
            "Assets/Kyle's Rock Pack",
            "Assets/DreamTree2",
            "Assets/Dry_Trees",
            "Assets/Medieval Props Pack 01",
            "Assets/EmbersStorm – Mediterranean Ruins Building Kit",
            "Assets/3 English Oak Set"
        };

        foreach (var f in folders)
        {
            if (AssetDatabase.IsValidFolder(f))
            {
                RunOnFolder(f);
            }
            else
            {
                Debug.Log($"[FixImportedMaterials] Folder not found: {f}");
            }
        }
    }

    [MenuItem("Tools/Fix Imported Materials/Toggle Dry Run")]
    public static void ToggleDryRun()
    {
        bool current = EditorPrefs.GetBool("FixImportedMaterials_DryRun", false);
        EditorPrefs.SetBool("FixImportedMaterials_DryRun", !current);
        Debug.Log($"[FixImportedMaterials] Dry run is now {(!current ? "ON" : "OFF")}");
    }

    private static void RunOnFolder(string rootFolder)
    {
        bool dryRun = EditorPrefs.GetBool("FixImportedMaterials_DryRun", false);
        var report = new ReportBuilder();

        FolderCache.Clear();

        MaterialConverter.ProcessMaterialsInFolder(rootFolder, dryRun, report);
        PrefabMaterialFixer.ProcessPrefabsInFolder(rootFolder, dryRun, report);

        if (!dryRun)
        {
            AssetDatabase.SaveAssets();
        }

        FolderCache.Clear();
        report.FinalizeAndWrite();
    }
}
#endif
