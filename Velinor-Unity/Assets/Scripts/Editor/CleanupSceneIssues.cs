using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

/// <summary>
/// CleanupSceneIssues - Fixes missing script references and duplicate AudioListeners.
/// </summary>
public class CleanupSceneIssues
{
    [MenuItem("Velinor/Cleanup Scene Issues")]
    public static void CleanupScene()
    {
        Debug.Log("=== Cleaning Up Scene Issues ===\n");

        RemoveMissingScriptReferences();
        RemoveDuplicateAudioListeners();

        Debug.Log("\n✅ Scene Cleanup Complete!");
        Debug.Log("\nℹ️  Save the scene to persist changes:");
        Debug.Log("   Ctrl+S or File > Save Scene");

        EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
    }

    private static void RemoveMissingScriptReferences()
    {
        Debug.Log("🔍 Scanning for missing script references...");

        GameObject[] allObjects = Object.FindObjectsByType<GameObject>(FindObjectsInactive.Include);
        int removedCount = 0;

        foreach (GameObject obj in allObjects)
        {
            Component[] components = obj.GetComponents<Component>();
            foreach (Component component in components)
            {
                // If component is null, it's a missing script reference
                if (component == null)
                {
                    Debug.Log($"  ❌ Removing missing script from: {obj.name}");
                    removedCount++;
                }
            }
        }

        if (removedCount > 0)
        {
            Debug.Log($"✓ Removed {removedCount} missing script references\n");
            
            // Use a more aggressive approach: find and remove via SerializedObject
            RemoveMissingScriptsRecursive(EditorSceneManager.GetActiveScene().GetRootGameObjects());
        }
        else
        {
            Debug.Log("✓ No missing script references found\n");
        }
    }

    private static void RemoveMissingScriptsRecursive(GameObject[] roots)
    {
        foreach (GameObject root in roots)
        {
            RemoveMissingScriptsFromGameObject(root);
            
            Transform[] childTransforms = root.GetComponentsInChildren<Transform>();
            GameObject[] childObjects = new GameObject[childTransforms.Length - 1]; // Exclude root
            for (int i = 1; i < childTransforms.Length; i++)
            {
                childObjects[i - 1] = childTransforms[i].gameObject;
            }
            
            if (childObjects.Length > 0)
            {
                RemoveMissingScriptsRecursive(childObjects);
            }
        }
    }

    private static void RemoveMissingScriptsFromGameObject(GameObject obj)
    {
        SerializedObject serializedObject = new SerializedObject(obj);
        SerializedProperty prop = serializedObject.FindProperty("m_Component");

        int arraySize = prop.arraySize;
        for (int i = arraySize - 1; i >= 0; i--)
        {
            SerializedProperty element = prop.GetArrayElementAtIndex(i);
            if (element.objectReferenceValue == null)
            {
                Debug.Log($"  ❌ Removing missing component from: {obj.name}");
                prop.DeleteArrayElementAtIndex(i);
            }
        }

        serializedObject.ApplyModifiedProperties();
    }

    private static void RemoveDuplicateAudioListeners()
    {
        Debug.Log("🔍 Scanning for duplicate AudioListeners...");

        AudioListener[] listeners = Object.FindObjectsByType<AudioListener>(FindObjectsInactive.Include);

        if (listeners.Length == 0)
        {
            Debug.Log("⚠️  No AudioListeners found in scene!");
            return;
        }

        if (listeners.Length == 1)
        {
            Debug.Log("✓ Exactly 1 AudioListener found - this is correct\n");
            return;
        }

        Debug.Log($"⚠️  Found {listeners.Length} AudioListeners (should be 1)");

        // Keep the first one, remove the rest
        for (int i = 1; i < listeners.Length; i++)
        {
            Debug.Log($"  ❌ Removing AudioListener from: {listeners[i].gameObject.name}");
            Object.DestroyImmediate(listeners[i]);
        }

        Debug.Log($"✓ Removed {listeners.Length - 1} duplicate AudioListeners\n");
    }
}
