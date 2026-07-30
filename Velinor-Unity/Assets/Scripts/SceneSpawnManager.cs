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
using UnityEngine.SceneManagement;

/// <summary>
/// Manages player spawn points when loading scenes.
/// When a scene loads, this finds the matching spawn point and places the player there.
/// </summary>
public class SceneSpawnManager : MonoBehaviour
{
    public static string nextSpawnID = "";

    [Header("Default Spawning Settings")]
    [Tooltip("If the scene is loaded directly without an active transition, which spawn ID should the player start at?")]
    [SerializeField] private string defaultSpawnID = "Default";

    private bool hasSpawnedInCurrentScene = false;

    private void OnEnable()
    {
        Debug.Log("[SceneSpawnManager] OnEnable called!");
        SceneManager.sceneLoaded += OnSceneLoaded;
    }

    private void OnDisable()
    {
        Debug.Log("[SceneSpawnManager] OnDisable called!");
        SceneManager.sceneLoaded -= OnSceneLoaded;
    }

    private void Start()
    {
        Debug.Log("[SceneSpawnManager] Start called!");
        // Try spawning in Start in case OnSceneLoaded was missed for the initial scene
        TriggerSpawn(SceneManager.GetActiveScene().name);
    }

    private void OnSceneLoaded(Scene scene, LoadSceneMode mode)
    {
        Debug.Log($"[SceneSpawnManager] OnSceneLoaded called for scene: {scene.name}");
        hasSpawnedInCurrentScene = false; // Reset for new scene load
        TriggerSpawn(scene.name);
    }

    private void TriggerSpawn(string sceneName)
    {
        Debug.Log($"[SceneSpawnManager] TriggerSpawn called! hasSpawnedInCurrentScene={hasSpawnedInCurrentScene}, nextSpawnID='{nextSpawnID}', defaultSpawnID='{defaultSpawnID}'");
        if (hasSpawnedInCurrentScene)
        {
            Debug.Log("[SceneSpawnManager] Already spawned in current scene, returning.");
            return;
        }

        string spawnToUse = string.IsNullOrEmpty(nextSpawnID) ? defaultSpawnID : nextSpawnID;
        Debug.Log($"[SceneSpawnManager] spawnToUse determined as: '{spawnToUse}'");

        if (string.IsNullOrEmpty(spawnToUse))
        {
            Debug.Log("[SceneSpawnManager] spawnToUse is empty, returning.");
            return;
        }

        SpawnPoint[] points = FindObjectsByType<SpawnPoint>(FindObjectsInactive.Exclude);
        Debug.Log($"[SceneSpawnManager] Found {points.Length} SpawnPoints in the scene.");

        foreach (var p in points)
        {
            Debug.Log($"[SceneSpawnManager] Checking SpawnPoint: '{p.gameObject.name}' with SpawnID='{p.SpawnID}'");
            if (p.SpawnID == spawnToUse)
            {
                GameObject player = GameObject.FindGameObjectWithTag("Player");
                if (player != null)
                {
                    // Use Teleport if PlayerController2D5 is present to ensure immediate scale update
                    var p25 = player.GetComponent<PlayerController2D5>();
                    if (p25 != null)
                    {
                        p25.Teleport(p.transform.position);
                        Debug.Log("[SceneSpawnManager] Teleported player via PlayerController2D5.");
                    }
                    else
                    {
                        player.transform.position = p.transform.position;
                    }
                    
                    hasSpawnedInCurrentScene = true;
                    Debug.Log($"[SceneSpawnManager] Player successfully spawned at point '{spawnToUse}' (Position: {p.transform.position}) in scene '{sceneName}'");
                }
                else
                {
                    Debug.LogWarning("[SceneSpawnManager] Player GameObject NOT found by tag 'Player'!");
                }
                break;
            }
        }

        if (!hasSpawnedInCurrentScene)
        {
            Debug.LogWarning($"[SceneSpawnManager] No SpawnPoint found with ID '{spawnToUse}'!");
        }

        nextSpawnID = "";
    }
}
