#if UNITY_EDITOR
using UnityEditor;

public static class DiagnosticsMenu
{
    [MenuItem("Tools/Diagnostics/Scan Missing Scripts and Materials")]
    public static void ScanAllIssues()
    {
        DiagnosticsScanner.ScanAllScenesAndPrefabs();
    }

    [MenuItem("Tools/Diagnostics/Convert Tent Materials to URP")]
    public static void ConvertTentMaterials()
    {
        TentMaterialConverter.ConvertTentExtractedMaterials();
    }

    [MenuItem("Tools/Asset Repair/[STEP 1] Comprehensive Repair All Asset Packs")]
    public static void ComprehensiveRepair()
    {
        ComprehensiveAssetRepair.RepairAllAssetPacks();
    }
}
#endif
