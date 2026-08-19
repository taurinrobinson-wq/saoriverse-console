using UnityEngine;

/// <summary>
/// Cleanup script to remove VignetteGenerator from shadow objects
/// Run once, then delete this script
/// </summary>
public class CleanupVignetteSetup : MonoBehaviour
{
    [ContextMenu("Remove VignetteGenerator from Shadows")]
    public void CleanupVignette()
    {
        // Find and remove VignetteGenerator from OuterDoorShadow
        Transform outerShadow = FindChildByName(transform.root, "OuterDoorShadow");
        if (outerShadow != null)
        {
            VignetteGenerator outerVig = outerShadow.GetComponent<VignetteGenerator>();
            if (outerVig != null)
            {
                DestroyImmediate(outerVig);
                Debug.Log("Removed VignetteGenerator from OuterDoorShadow");
            }
        }

        // Find and remove VignetteGenerator from InnerDoorShadow
        Transform innerShadow = FindChildByName(transform.root, "InnerDoorShadow");
        if (innerShadow != null)
        {
            VignetteGenerator innerVig = innerShadow.GetComponent<VignetteGenerator>();
            if (innerVig != null)
            {
                DestroyImmediate(innerVig);
                Debug.Log("Removed VignetteGenerator from InnerDoorShadow");
            }
        }

        Debug.Log("Cleanup complete! You can now delete the CleanupVignetteSetup script.");
    }

    private Transform FindChildByName(Transform parent, string name)
    {
        if (parent.name == name)
            return parent;

        foreach (Transform child in parent)
        {
            Transform result = FindChildByName(child, name);
            if (result != null)
                return result;
        }

        return null;
    }
}
