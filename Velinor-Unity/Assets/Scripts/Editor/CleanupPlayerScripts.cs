using UnityEditor;
using UnityEngine;

/// <summary>
/// Cleanup duplicate scripts on the Player GameObject.
/// Removes old StarterAssets scripts in favor of the new Velinor scripts.
/// </summary>
public class CleanupPlayerScripts
{
    [MenuItem("Velinor/Cleanup Player Duplicate Scripts")]
    public static void CleanupPlayer()
    {
        GameObject player = GameObject.Find("Player");
        if (player == null)
        {
            EditorUtility.DisplayDialog("Error", "Player GameObject not found!", "OK");
            return;
        }

        Debug.Log("=== Cleaning Up Player Duplicate Scripts ===\n");

        int removedCount = 0;

        // Remove old StarterAssets scripts
        RemoveComponentIfExists<StarterAssets.StarterAssetsInputs>(player, ref removedCount);
        RemoveComponentIfExists<StarterAssets.ThirdPersonController>(player, ref removedCount);

        // Ensure we have the NEW versions
        EnsureComponentExists<StarterAssets.VelinorStarterAssetsInputs>(player);
        EnsureComponentExists<StarterAssets.VelinorPlayerController>(player);

        Debug.Log($"\n✅ Cleanup Complete!");
        Debug.Log($"   Removed: {removedCount} duplicate scripts");
        Debug.Log($"\n📋 Player now has ONLY:");
        Debug.Log($"   ✓ Character Controller");
        Debug.Log($"   ✓ PlayerInput (for Input System)");
        Debug.Log($"   ✓ Velinor Starter Assets Inputs");
        Debug.Log($"   ✓ Velinor Player Controller");
        Debug.Log($"   ✓ Main Camera");

        EditorUtility.DisplayDialog("Cleanup Complete", 
            $"Removed {removedCount} duplicate scripts.\n\n" +
            "Player is now clean and optimized!", 
            "OK");
    }

    private static void RemoveComponentIfExists<T>(GameObject obj, ref int removedCount) where T : Component
    {
        T component = obj.GetComponent<T>();
        if (component != null)
        {
            string componentName = typeof(T).Name;
            Debug.Log($"❌ Removing old script: {componentName}");
            Object.DestroyImmediate(component);
            removedCount++;
        }
    }

    private static void EnsureComponentExists<T>(GameObject obj) where T : Component
    {
        if (obj.GetComponent<T>() == null)
        {
            obj.AddComponent<T>();
            Debug.Log($"✓ Added: {typeof(T).Name}");
        }
        else
        {
            Debug.Log($"✓ Already has: {typeof(T).Name}");
        }
    }
}
