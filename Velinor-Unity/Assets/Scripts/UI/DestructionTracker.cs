using UnityEngine;

/// <summary>
/// Utility script to track unexpected destruction of GameObjects.
/// Silent during scene unload/play stop - only warns about mid-gameplay destruction.
/// </summary>
public class DestructionTracker : MonoBehaviour
{
    public string objectName = "Unknown";

    private void OnDestroy()
    {
        // Only warn about destruction during active gameplay
        // Silently allow destruction during scene unload or play mode stop
        if (gameObject.scene.isLoaded && Application.isPlaying)
        {
            Debug.LogWarning($"[UNEXPECTED DESTRUCTION] {objectName} was destroyed during gameplay!");
        }
    }
}
