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
