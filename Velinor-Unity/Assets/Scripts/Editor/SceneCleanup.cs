using UnityEditor;
using UnityEngine;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;

namespace Velinor.Editor
{
    /// <summary>
    /// SceneCleanup - Remove all scene content and prepare for fresh population
    /// </summary>
    public class SceneCleanup
    {
        [MenuItem("Velinor/Scene Setup/Clear Everything")]
        public static void ClearEverything()
        {
            Debug.Log("\n🧹 CLEARING MARKETPLACE SCENE...\n");

            Scene activeScene = SceneManager.GetActiveScene();
            if (activeScene.name != "Marketplace")
            {
                Debug.LogError("❌ Active scene is not 'Marketplace'. Load it first.");
                return;
            }

            // Get all root objects in scene
            GameObject[] rootObjects = activeScene.GetRootGameObjects();
            
            int count = 0;
            foreach (GameObject obj in rootObjects)
            {
                Debug.Log($"  Destroying: {obj.name}");
                Object.DestroyImmediate(obj);
                count++;
            }

            Debug.Log($"\n✅ SCENE CLEARED ({count} objects removed)\n");
            Debug.Log("📋 Next: Run 'Velinor > Scene Setup > Organize Market Scene'\n");

            EditorSceneManager.MarkSceneDirty(activeScene);
        }
    }
}
