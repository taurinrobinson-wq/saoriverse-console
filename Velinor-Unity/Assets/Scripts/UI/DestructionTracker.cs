using UnityEngine;

/// <summary>
/// Utility script to track when GameObjects are destroyed.
/// Used for debugging container visibility issues.
/// </summary>
public class DestructionTracker : MonoBehaviour
{
    public string objectName = "Unknown";

    private void OnDestroy()
    {
        Debug.LogError($"[DESTRUCTION] {objectName} was DESTROYED! Stack trace follows:");
        Debug.LogError(System.Environment.StackTrace);
    }

    private void OnDisable()
    {
        if (gameObject.scene.isLoaded)  // Only log if not scene unloading
        {
            Debug.LogWarning($"[DISABLED] {objectName} was disabled - currently visible: {gameObject.activeSelf}");
        }
    }
}
