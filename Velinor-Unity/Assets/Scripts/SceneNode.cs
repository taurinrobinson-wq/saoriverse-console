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

/// <summary>
/// Represents a single scene node in the world graph.
/// Defines connections to other scenes.
/// </summary>
[System.Serializable]
public class SceneConnection
{
    public string exitName;      // e.g. "NorthExit", "DoorwayA"
    public string targetScene;   // e.g. "CaveScene2"
}

public class SceneNode : MonoBehaviour
{
    [SerializeField] private string sceneName;
    [SerializeField] private SceneConnection[] connections;

    public string GetTargetScene(string exitName)
    {
        foreach (var c in connections)
        {
            if (c.exitName == exitName)
                return c.targetScene;
        }
        return null;
    }

    public string SceneName => sceneName;
}
