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
/// Manages player spawn points when loading scenes.
/// When a scene loads, this finds the matching spawn point and places the player there.
/// </summary>
public class SceneSpawnManager : MonoBehaviour
{
    public static string nextSpawnID = "";

    private void Start()
    {
        if (string.IsNullOrEmpty(nextSpawnID))
            return;

        SpawnPoint[] points = FindObjectsOfType<SpawnPoint>();

        foreach (var p in points)
        {
            if (p.SpawnID == nextSpawnID)
            {
                GameObject player = GameObject.FindGameObjectWithTag("Player");
                if (player != null)
                {
                    player.transform.position = p.transform.position;
                    Debug.Log($"[SceneSpawnManager] Player spawned at: {nextSpawnID}");
                }
                break;
            }
        }

        nextSpawnID = "";
    }
}
