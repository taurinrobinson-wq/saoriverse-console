#if UNITY_EDITOR
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

public static class PrefabMaterialFixer
{
    public static void ProcessPrefabsInFolder(string rootFolder, bool dryRun, ReportBuilder report)
    {
        bool srpActive = GraphicsSettings.currentRenderPipeline != null;
        var prefabPaths = FolderCache.GetPrefabs(rootFolder);
        int total = prefabPaths.Count;
        int index = 0;

        foreach (var pPath in prefabPaths)
        {
            EditorUtility.DisplayProgressBar("Fix Imported Materials - Prefabs", pPath, (float)index / (total > 0 ? total : 1));
            index++;

            var prefabRoot = PrefabUtility.LoadPrefabContents(pPath);
            bool prefabChanged = false;

            try
            {
                var renderers = prefabRoot.GetComponentsInChildren<Renderer>(true);
                foreach (var r in renderers)
                {
                    var mats = r.sharedMaterials;
                    int slotCount = mats != null ? mats.Length : 0;
                    bool anyDefault = false;

                    for (int i = 0; i < slotCount; i++)
                    {
                        var mat = mats[i];
                        if (mat == null || mat.shader == null || mat.shader.name == "Hidden/InternalErrorShader" || mat.name.ToLower().Contains("default"))
                        {
                            anyDefault = true;
                            string folder = Path.GetDirectoryName(pPath).Replace("\\", "/");
                            var candidates = FolderCache.GetMaterials(folder);

                            Material pick = null;
                            string rendererName = r.gameObject.name.ToLower();
                            foreach (var cPath in candidates)
                            {
                                string cname = Path.GetFileNameWithoutExtension(cPath).ToLower();
                                if (rendererName.Contains(cname))
                                {
                                    pick = AssetDatabase.LoadAssetAtPath<Material>(cPath);
                                    break;
                                }
                            }

                            if (pick == null && candidates.Count > 0)
                            {
                                foreach (var cPath in candidates)
                                {
                                    string dir = Path.GetDirectoryName(cPath).ToLower();
                                    if (dir.EndsWith("materials"))
                                    {
                                        pick = AssetDatabase.LoadAssetAtPath<Material>(cPath);
                                        break;
                                    }
                                }
                            }

                            if (pick != null)
                            {
                                mats[i] = pick;
                                prefabChanged = true;
                                report.LogReassign(pPath, r.gameObject.name, i, AssetDatabase.GetAssetPath(pick));
                            }
                            else if (mat != null && (mat.shader == null || mat.shader.name.Contains("Hidden/InternalError")))
                            {
                                var newMat = FallbackMaterialFactory.CreateFallbackMaterialForSlot(pPath, i, srpActive);
                                mats[i] = newMat;
                                prefabChanged = true;
                                report.LogAutoFallback(pPath, r.gameObject.name, i, AssetDatabase.GetAssetPath(newMat));
                            }
                        }
                    }

                    for (int i = 0; i < slotCount; i++)
                    {
                        var mat = mats[i];
                        if (mat == null) continue;
                        string sname = mat.shader != null ? mat.shader.name : "";
                        if (sname == "Standard")
                        {
                            bool hasMain = mat.HasProperty("_MainTex") && mat.GetTexture("_MainTex") != null;
                            if (!hasMain)
                            {
                                string prefabFolder = Path.GetDirectoryName(pPath).Replace("\\", "/");
                                bool assigned = TextureAutoAssigner.TryAssignTexturesFromFolder(mat, prefabFolder);
                                if (assigned)
                                {
                                    prefabChanged = true;
                                    report.LogPatchStandard(pPath, r.gameObject.name, i);
                                }
                                else
                                {
                                    var newMat = FallbackMaterialFactory.CreateStandardFallback(pPath, i);
                                    mats[i] = newMat;
                                    prefabChanged = true;
                                    report.LogAutoStd(pPath, r.gameObject.name, i, AssetDatabase.GetAssetPath(newMat));
                                }
                            }
                        }
                    }

                    if (anyDefault)
                    {
                        r.sharedMaterials = mats;
                    }
                }

                if (prefabChanged && !dryRun)
                {
                    PrefabUtility.SaveAsPrefabAsset(prefabRoot, pPath);
                }
            }
            finally
            {
                PrefabUtility.UnloadPrefabContents(prefabRoot);
            }
        }

        EditorUtility.ClearProgressBar();
    }
}
#endif
