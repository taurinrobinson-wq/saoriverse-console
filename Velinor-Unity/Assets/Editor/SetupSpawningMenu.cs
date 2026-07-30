using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;

public static class SetupSpawningMenu
{
    [MenuItem("Velinor/Setup Spawning Systems")]
    public static void SetupSpawning()
    {
        string scenePath1 = "Assets/Scenes/MachinesCave_01.unity";
        string scenePath2 = "Assets/Scenes/MachinesCave_02.unity";

        // ==========================================
        // Configure MachinesCave_01
        // ==========================================
        var scene1 = EditorSceneManager.OpenScene(scenePath1, OpenSceneMode.Single);

        var transitionManagerObj1 = Object.FindFirstObjectByType<SceneTransitionManager>();
        if (transitionManagerObj1 != null)
        {
            // Remove any missing or invalid components first to clean up
            SerializedObject obj = new SerializedObject(transitionManagerObj1.gameObject);
            SerializedProperty componentsProp = obj.FindProperty("m_Component");
            for (int i = componentsProp.arraySize - 1; i >= 0; i--)
            {
                SerializedProperty componentProp = componentsProp.GetArrayElementAtIndex(i).FindPropertyRelative("component");
                if (componentProp.objectReferenceValue == null)
                {
                    componentsProp.DeleteArrayElementAtIndex(i);
                }
            }
            obj.ApplyModifiedProperties();

            // Add SceneSpawnManager properly from the permanent Editor assembly
            var spawnManager = transitionManagerObj1.GetComponent<SceneSpawnManager>();
            if (spawnManager == null)
            {
                spawnManager = transitionManagerObj1.gameObject.AddComponent<SceneSpawnManager>();
            }

            var serializedManager = new SerializedObject(spawnManager);
            serializedManager.FindProperty("defaultSpawnID").stringValue = "Default";
            serializedManager.ApplyModifiedProperties();
            Debug.Log("Scene 1: Added and configured SceneSpawnManager");
        }

        EditorSceneManager.MarkSceneDirty(scene1);
        EditorSceneManager.SaveScene(scene1);

        // ==========================================
        // Configure MachinesCave_02
        // ==========================================
        var scene2 = EditorSceneManager.OpenScene(scenePath2, OpenSceneMode.Single);

        var transitionManagerObj2 = Object.FindFirstObjectByType<SceneTransitionManager>();
        if (transitionManagerObj2 != null)
        {
            // Remove any missing or invalid components first
            SerializedObject obj = new SerializedObject(transitionManagerObj2.gameObject);
            SerializedProperty componentsProp = obj.FindProperty("m_Component");
            for (int i = componentsProp.arraySize - 1; i >= 0; i--)
            {
                SerializedProperty componentProp = componentsProp.GetArrayElementAtIndex(i).FindPropertyRelative("component");
                if (componentProp.objectReferenceValue == null)
                {
                    componentsProp.DeleteArrayElementAtIndex(i);
                }
            }
            obj.ApplyModifiedProperties();

            var spawnManager = transitionManagerObj2.GetComponent<SceneSpawnManager>();
            if (spawnManager == null)
            {
                spawnManager = transitionManagerObj2.gameObject.AddComponent<SceneSpawnManager>();
            }

            var serializedManager = new SerializedObject(spawnManager);
            serializedManager.FindProperty("defaultSpawnID").stringValue = "Default";
            serializedManager.ApplyModifiedProperties();
            Debug.Log("Scene 2: Added and configured SceneSpawnManager");
        }

        EditorSceneManager.MarkSceneDirty(scene2);
        EditorSceneManager.SaveScene(scene2);

        // Return to scene 1
        EditorSceneManager.OpenScene(scenePath1, OpenSceneMode.Single);
        Debug.Log("✓ Spawning systems setup completed from permanent assembly!");
    }
}