using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEditor;
using UnityEditor.SceneManagement;

namespace Velinor.Editor
{
    /// <summary>
    /// Creates new URP-based MachinesCave scenes from proper templates
    /// Use: Velinor → Setup → Create URP Scenes
    /// 
    /// This creates:
    /// - MachinesCave_00_URP (outdoor template - desert cave)
    /// - MachinesCave_01_URP (indoor template)
    /// - MachinesCave_02_URP (indoor template)
    /// </summary>
    public class CreateURPCaveScenes
    {
        private const string SCENES_PATH = "Assets/Scenes/";

        [MenuItem("Velinor/Setup/Create URP Cave Scenes")]
        public static void CreateURPScenes()
        {
            EditorUtility.DisplayDialog("URP Scene Creation",
                "This will create three new URP-based scenes:\n" +
                "• MachinesCave_00_URP (Outdoor)\n" +
                "• MachinesCave_01_URP (Indoor)\n" +
                "• MachinesCave_02_URP (Indoor)\n\n" +
                "These will start from proper URP templates.\n\n" +
                "IMPORTANT: You'll need to manually port content from old scenes:\n" +
                "1. Door/Collider structures\n" +
                "2. Puzzle UI and logic\n" +
                "3. Glyph pickups and locations\n" +
                "4. Custom spawn points",
                "OK");

            // Create outdoor scene (MachinesCave_00_URP)
            Scene cave00 = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
            EditorSceneManager.SaveScene(cave00, SCENES_PATH + "MachinesCave_00_URP.unity");
            SetupOutdoorScene(cave00);
            EditorSceneManager.SaveScene(cave00);
            Debug.Log("[CreateURPCaveScenes] Created MachinesCave_00_URP (Outdoor)");

            // Create indoor scenes
            Scene cave01 = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
            EditorSceneManager.SaveScene(cave01, SCENES_PATH + "MachinesCave_01_URP.unity");
            SetupIndoorScene(cave01, "MachinesCave_01_URP");
            EditorSceneManager.SaveScene(cave01);
            Debug.Log("[CreateURPCaveScenes] Created MachinesCave_01_URP (Indoor)");

            Scene cave02 = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
            EditorSceneManager.SaveScene(cave02, SCENES_PATH + "MachinesCave_02_URP.unity");
            SetupIndoorScene(cave02, "MachinesCave_02_URP");
            EditorSceneManager.SaveScene(cave02);
            Debug.Log("[CreateURPCaveScenes] Created MachinesCave_02_URP (Indoor)");

            EditorUtility.DisplayDialog("Success",
                "Created 3 new URP scenes!\n\n" +
                "Next steps:\n" +
                "1. Open each scene to verify lighting/effects look good\n" +
                "2. Copy puzzle logic, doors, glyphs from old scenes\n" +
                "3. Adjust lighting and post-processing as needed",
                "OK");
        }

        private static void SetupOutdoorScene(Scene scene)
        {
            // Get or create Directional Light for outdoor (sunny desert)
            GameObject lightObj = new GameObject("Directional Light");
            Light light = lightObj.AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.5f; // Outdoor sunlight
            light.color = new Color(1f, 0.95f, 0.8f); // Warm desert sun
            lightObj.transform.eulerAngles = new Vector3(50f, -30f, 0f);
            SceneManager.MoveGameObjectToScene(lightObj, scene);

            // Add Global Volume for outdoor post-processing
            GameObject volumeObj = new GameObject("GlobalVolume");
            volumeObj.AddComponent<BoxCollider>().isTrigger = true;
            var volume = volumeObj.AddComponent<UnityEngine.Rendering.Volume>();
            volume.isGlobal = true;
            SceneManager.MoveGameObjectToScene(volumeObj, scene);

            // Create ground plane
            GameObject groundObj = GameObject.CreatePrimitive(PrimitiveType.Plane);
            groundObj.name = "GroundPlane";
            groundObj.transform.localScale = new Vector3(100f, 1f, 100f);
            Object.DestroyImmediate(groundObj.GetComponent<Collider>());
            groundObj.AddComponent<BoxCollider>();
            Object.DestroyImmediate(groundObj.GetComponent<MeshRenderer>());
            SceneManager.MoveGameObjectToScene(groundObj, scene);

            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.5f, 0.5f, 0.5f, 1f);
        }

        private static void SetupIndoorScene(Scene scene, string sceneName)
        {
            // Get or create Directional Light for indoor (dimmer, cooler)
            GameObject lightObj = new GameObject("Directional Light");
            Light light = lightObj.AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 0.6f; // Indoor dimmer
            light.color = new Color(0.7f, 0.8f, 0.9f); // Cool indoor light
            lightObj.transform.eulerAngles = new Vector3(45f, 45f, 0f);
            SceneManager.MoveGameObjectToScene(lightObj, scene);

            // Add Global Volume for indoor post-processing
            GameObject volumeObj = new GameObject("GlobalVolume");
            volumeObj.AddComponent<BoxCollider>().isTrigger = true;
            var volume = volumeObj.AddComponent<UnityEngine.Rendering.Volume>();
            volume.isGlobal = true;
            SceneManager.MoveGameObjectToScene(volumeObj, scene);

            // Create ground plane
            GameObject groundObj = GameObject.CreatePrimitive(PrimitiveType.Plane);
            groundObj.name = "GroundPlane";
            groundObj.transform.localScale = new Vector3(50f, 1f, 50f);
            Object.DestroyImmediate(groundObj.GetComponent<Collider>());
            groundObj.AddComponent<BoxCollider>();
            Object.DestroyImmediate(groundObj.GetComponent<MeshRenderer>());
            SceneManager.MoveGameObjectToScene(groundObj, scene);

            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.3f, 0.35f, 0.4f, 1f); // Darker indoor ambient
        }
    }
}
