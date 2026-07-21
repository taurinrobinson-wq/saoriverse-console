/*
 * ============================================================
 * PROPRIETARY & CONFIDENTIAL
 * 
 * © 2026 Tauri Robinson. All rights reserved.
 * This code is proprietary and may not be redistributed,
 * modified, or used without explicit written permission.
 * 
 * Unauthorized access, modification, or distribution is prohibited.
 * See LICENSE_COMMERCIAL.md and NDA_TEMPLATE.md for details.
 * ============================================================
 */

using UnityEngine;
using System.Collections.Generic;

/// <summary>
/// Central world graph system.
/// Maps all scenes and their connections.
/// Persists across scenes for world navigation queries.
/// </summary>
public class SceneGraph : MonoBehaviour
{
    public static SceneGraph Instance;

    [SerializeField] private SceneNode[] nodes;
    private Dictionary<string, SceneNode> nodeLookup;

    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
            return;
        }

        nodeLookup = new Dictionary<string, SceneNode>();
        foreach (var node in nodes)
        {
            if (node != null)
                nodeLookup[node.SceneName] = node;
        }

        Debug.Log($"[SceneGraph] Loaded {nodeLookup.Count} scene nodes");
    }

    public string GetSceneFromExit(string currentScene, string exitName)
    {
        if (!nodeLookup.ContainsKey(currentScene))
        {
            Debug.LogWarning($"[SceneGraph] Scene '{currentScene}' not in graph");
            return null;
        }

        return nodeLookup[currentScene].GetTargetScene(exitName);
    }
}
