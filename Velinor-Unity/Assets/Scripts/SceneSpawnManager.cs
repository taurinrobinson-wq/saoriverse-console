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
