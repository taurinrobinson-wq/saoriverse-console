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
