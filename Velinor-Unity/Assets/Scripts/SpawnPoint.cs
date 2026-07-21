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
/// Marks a spawn point in a scene.
/// Assign a unique ID so the spawn manager can find it.
/// </summary>
public class SpawnPoint : MonoBehaviour
{
    [SerializeField] private string spawnID = "Default";

    public string SpawnID => spawnID;
}
