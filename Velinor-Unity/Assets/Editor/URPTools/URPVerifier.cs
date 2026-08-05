using UnityEditor;
using UnityEngine;
using System.Collections.Generic;

public class URPVerifier : EditorWindow
{
    [MenuItem("URP Tools/Verify URP Cleanliness")]
    public static void VerifyURP()
    {
        List<string> issues = new List<string>();

        // Check for HDRP pipeline assets
        string[] hdrpPipeline = AssetDatabase.FindAssets("HDRenderPipelineAsset");
        if (hdrpPipeline.Length > 0)
            issues.Add("HDRP Pipeline Asset detected.");

        string[] hdrpGlobal = AssetDatabase.FindAssets("HDRenderPipelineGlobalSettings");
        if (hdrpGlobal.Length > 0)
            issues.Add("HDRP Global Settings detected.");

        // Check for HDRP diffusion profiles
        string[] diffusionProfiles = AssetDatabase.FindAssets("DiffusionProfile");
        if (diffusionProfiles.Length > 0)
            issues.Add("HDRP Diffusion Profiles detected.");

        // Check for HDRP default resources
        string[] hdrpDefault = AssetDatabase.FindAssets("HDRPDefaultResources");
        if (hdrpDefault.Length > 0)
            issues.Add("HDRP Default Resources folder detected.");

        // Check for HDRP materials
        string[] materials = AssetDatabase.FindAssets("t:Material");
        foreach (string guid in materials)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            Material mat = AssetDatabase.LoadAssetAtPath<Material>(path);

            if (mat != null && mat.shader != null)
            {
                string shaderName = mat.shader.name.ToLower();
                if (shaderName.Contains("hdrp"))
                    issues.Add("HDRP Material: " + path);
            }
        }

        // Check for HDRP scripts
        string[] scripts = AssetDatabase.FindAssets("t:Script");
        foreach (string guid in scripts)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            string lower = path.ToLower();

            if (lower.Contains("hdrp") ||
                lower.Contains("hdadditional") ||
                lower.Contains("diffusionprofile"))
            {
                issues.Add("HDRP Script: " + path);
            }
        }

        // Check for HDRP shadergraphs
        string[] shaderGraphs = AssetDatabase.FindAssets("t:Shader");
        foreach (string guid in shaderGraphs)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            string lower = path.ToLower();

            if (lower.Contains("hdrp"))
                issues.Add("HDRP ShaderGraph: " + path);
        }

        // Check for HDRP volume profiles
        string[] volumeProfiles = AssetDatabase.FindAssets("t:VolumeProfile");
        foreach (string guid in volumeProfiles)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            if (path.ToLower().Contains("hdrp"))
                issues.Add("HDRP Volume Profile: " + path);
        }

        // Output results
        if (issues.Count == 0)
        {
            Debug.Log("URP Verification: Project is clean. No HDRP contamination detected.");
        }
        else
        {
            Debug.LogWarning("URP Verification: HDRP contamination found:");
            foreach (string issue in issues)
                Debug.LogWarning(" - " + issue);
        }
    }
}
