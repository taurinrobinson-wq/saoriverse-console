using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEditor;
using UnityEditor.SceneManagement;

namespace Velinor.Editor
{
    /// <summary>
    /// Editor utility to set up the PlayerTest scene with elements from MachinesCave_01
    /// Use: Velinor → Setup → PlayerTest Scene
    /// </summary>
    public class SetupPlayerTestScene
    {
        [MenuItem("Velinor/Setup/PlayerTest Scene from MachinesCave_01")]
        public static void SetupPlayerTestFromMachinesCave01()
        {
            // Load both scenes
            EditorSceneManager.OpenScene("Assets/Scenes/MachinesCave_01.unity", OpenSceneMode.Additive);
            EditorSceneManager.OpenScene("Assets/Scenes/PlayerTest.unity", OpenSceneMode.Additive);

            Scene cave01 = EditorSceneManager.GetSceneByName("MachinesCave_01");
            Scene playerTest = EditorSceneManager.GetSceneByName("PlayerTest");

            if (!cave01.IsValid() || !playerTest.IsValid())
            {
                EditorUtility.DisplayDialog("Error", "Could not load both scenes", "OK");
                return;
            }

            // Get root objects from MachinesCave_01
            GameObject[] caveRootObjects = cave01.GetRootGameObjects();
            int copiedCount = 0;

            // Objects to copy (by name)
            string[] objectsToCopy = new string[]
            {
                "Directional Light",
                "GroundPlane",
                "Background",
                "SceneCollider",
                "GlobalVolumeProfile"
            };

            foreach (string objName in objectsToCopy)
            {
                GameObject sourceObj = FindGameObjectInScene(caveRootObjects, objName);
                if (sourceObj != null)
                {
                    GameObject copiedObj = Object.Instantiate(sourceObj);
                    copiedObj.name = sourceObj.name;
                    UnityEngine.SceneManagement.SceneManager.MoveGameObjectToScene(copiedObj, playerTest);
                    copiedCount++;
                    Debug.Log($"[SetupPlayerTestScene] Copied: {objName}");
                }
            }

            // Find Main Camera in MachinesCave_01 and update PlayerTest's camera
            GameObject caveCamera = FindGameObjectInScene(caveRootObjects, "Main Camera");
            GameObject testCamera = FindGameObjectInScene(playerTest.GetRootGameObjects(), "Main Camera");

            if (caveCamera != null && testCamera != null)
            {
                // Copy camera settings
                Camera caveCameraCom = caveCamera.GetComponent<Camera>();
                Camera testCameraCom = testCamera.GetComponent<Camera>();
                if (caveCameraCom != null && testCameraCom != null)
                {
                    EditorUtility.CopySerialized(caveCameraCom, testCameraCom);
                    Debug.Log("[SetupPlayerTestScene] Updated Main Camera settings");
                }
            }

            // Save and close MachinesCave_01
            EditorSceneManager.SaveScene(playerTest);
            EditorSceneManager.CloseScene(cave01, true);

            EditorUtility.DisplayDialog("Success",
                $"PlayerTest scene setup complete!\n\nCopied {copiedCount} objects from MachinesCave_01.\n\nNext steps:\n" +
                "1. Add Asuna prefab to scene\n" +
                "2. Add SpawnPoint for player\n" +
                "3. Add StarterAssets.VelinorPlayerController to Asuna",
                "OK");
        }

        private static GameObject FindGameObjectInScene(GameObject[] roots, string name)
        {
            foreach (GameObject root in roots)
            {
                if (root.name == name)
                    return root;

                Transform found = root.transform.Find(name);
                if (found != null)
                    return found.gameObject;
            }
            return null;
        }
    }
}
