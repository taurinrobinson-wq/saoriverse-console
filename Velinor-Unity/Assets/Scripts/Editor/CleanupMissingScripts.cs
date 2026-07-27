using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;

/// <summary>
/// CleanupMissingScripts - Removes all missing script references from the current scene.
/// Usage: Go to Velinor > Cleanup Missing Scripts in the menu.
/// </summary>
public class CleanupMissingScripts
{
    [MenuItem("Velinor/Cleanup Missing Scripts")]
    public static void RemoveMissingScripts()
    {
        int count = 0;
        Scene scene = EditorSceneManager.GetActiveScene();
        GameObject[] allGameObjects = scene.GetRootGameObjects();

        foreach (GameObject root in allGameObjects)
        {
            count += RemoveMissingScriptsRecursive(root);
        }

        if (count > 0)
        {
            EditorSceneManager.MarkSceneDirty(scene);
            Debug.Log($"✅ Removed {count} missing script components from the scene.");
        }
        else
        {
            Debug.Log("✅ No missing scripts found in the scene.");
        }
    }

    private static int RemoveMissingScriptsRecursive(GameObject gameObject)
    {
        int removed = 0;
        Component[] components = gameObject.GetComponents<Component>();

        foreach (Component component in components)
        {
            if (component == null)
            {
                // This is a missing script component
                Debug.LogWarning($"Removing missing script from '{gameObject.name}'", gameObject);
                Object.DestroyImmediate(component, true);
                removed++;
            }
        }

        foreach (Transform child in gameObject.transform)
        {
            removed += RemoveMissingScriptsRecursive(child.gameObject);
        }

        return removed;
    }
}
