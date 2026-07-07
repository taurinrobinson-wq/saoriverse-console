#if UNITY_EDITOR
using System.Text;
using UnityEngine;
using System.IO;

public class ReportBuilder
{
    private readonly StringBuilder _sb = new StringBuilder();

    private int _convertedCount;
    private int _patchedCount;
    private int _reassignedCount;
    private int _fallbackCount;
    private int _stdFallbackCount;
    private int _prefabPatchedCount;

    public ReportBuilder()
    {
        _sb.AppendLine("Material Fix Report");
        _sb.AppendLine(System.DateTime.Now.ToString());
    }

    public void LogConvert(string path, string shaderName)
    {
        _convertedCount++;
        _sb.AppendLine($"[CONVERT] {path} -> shader set to '{shaderName}'");
    }

    public void LogSkipConvert(string path)
    {
        _sb.AppendLine($"[SKIP-CONVERT] {path} (SRP inactive or URP shader not found)");
    }

    public void LogPatch(string path)
    {
        _patchedCount++;
        _sb.AppendLine($"[PATCH] {path} - assigned missing textures");
    }

    public void LogMaterialFallback(string path, string newShader)
    {
        _fallbackCount++;
        _sb.AppendLine($"[MAT-FALLBACK] {path} -> shader set to '{newShader}'");
    }

    public void LogReassign(string prefabPath, string rendererName, int slot, string matPath)
    {
        _reassignedCount++;
        _sb.AppendLine($"[REASSIGN] {prefabPath} - renderer '{rendererName}' slot {slot} -> {matPath}");
    }

    public void LogAutoFallback(string prefabPath, string rendererName, int slot, string matPath)
    {
        _fallbackCount++;
        _sb.AppendLine($"[AUTO-FALLBACK] {prefabPath} - renderer '{rendererName}' slot {slot} -> {matPath}");
    }

    public void LogPatchStandard(string prefabPath, string rendererName, int slot)
    {
        _prefabPatchedCount++;
        _sb.AppendLine($"[PATCH-MAT] {prefabPath} - assigned textures to Standard material on '{rendererName}' slot {slot}");
    }

    public void LogAutoStd(string prefabPath, string rendererName, int slot, string matPath)
    {
        _stdFallbackCount++;
        _sb.AppendLine($"[AUTO-STD] {prefabPath} - created Standard fallback {matPath} for renderer '{rendererName}' slot {slot}");
    }

    public void FinalizeAndWrite()
    {
        _sb.AppendLine();
        _sb.AppendLine("=== Summary ===");
        _sb.AppendLine($"Converted:       {_convertedCount}");
        _sb.AppendLine($"Patched:         {_patchedCount}");
        _sb.AppendLine($"Reassigned:      {_reassignedCount}");
        _sb.AppendLine($"Fallbacks:       {_fallbackCount}");
        _sb.AppendLine($"Std Fallbacks:   {_stdFallbackCount}");
        _sb.AppendLine($"Prefab Patched:  {_prefabPatchedCount}");

        var outPath = Path.Combine(Application.dataPath, "..", "MaterialFixReport.txt");
        try
        {
            File.WriteAllText(outPath, _sb.ToString());
            Debug.Log($"Material fixes complete. Report written to: {outPath}");
        }
        catch (System.Exception ex)
        {
            Debug.LogWarning("Failed to write MaterialFixReport.txt: " + ex.Message);
        }
    }
}
#endif
