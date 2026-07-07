#if UNITY_EDITOR
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;

public static class FolderCache
{
    private static readonly Dictionary<string, List<string>> _texturesByFolder = new Dictionary<string, List<string>>();
    private static readonly Dictionary<string, List<string>> _materialsByFolder = new Dictionary<string, List<string>>();
    private static readonly Dictionary<string, List<string>> _prefabsByFolder = new Dictionary<string, List<string>>();

    public static void Clear()
    {
        _texturesByFolder.Clear();
        _materialsByFolder.Clear();
        _prefabsByFolder.Clear();
    }

    public static List<string> GetTextures(string folder)
    {
        if (string.IsNullOrEmpty(folder) || !AssetDatabase.IsValidFolder(folder))
            return new List<string>();

        if (_texturesByFolder.TryGetValue(folder, out var cached))
            return cached;

        var texGuids = AssetDatabase.FindAssets("t:Texture2D", new[] { folder });
        var textures = texGuids
            .Select(g => AssetDatabase.GUIDToAssetPath(g))
            .ToList();

        _texturesByFolder[folder] = textures;
        return textures;
    }

    public static List<string> GetMaterials(string folder)
    {
        if (string.IsNullOrEmpty(folder) || !AssetDatabase.IsValidFolder(folder))
            return new List<string>();

        if (_materialsByFolder.TryGetValue(folder, out var cached))
            return cached;

        var matGuids = AssetDatabase.FindAssets("t:Material", new[] { folder });
        var mats = matGuids
            .Select(g => AssetDatabase.GUIDToAssetPath(g))
            .ToList();

        _materialsByFolder[folder] = mats;
        return mats;
    }

    public static List<string> GetPrefabs(string folder)
    {
        if (string.IsNullOrEmpty(folder) || !AssetDatabase.IsValidFolder(folder))
            return new List<string>();

        if (_prefabsByFolder.TryGetValue(folder, out var cached))
            return cached;

        var prefabGuids = AssetDatabase.FindAssets("t:Prefab", new[] { folder });
        var prefabs = prefabGuids
            .Select(g => AssetDatabase.GUIDToAssetPath(g))
            .ToList();

        _prefabsByFolder[folder] = prefabs;
        return prefabs;
    }
}
#endif
