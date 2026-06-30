using UnityEngine;

#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Velinor.Core
{
    /// <summary>
    /// SceneTestSetup - Add visual test elements to see the scene structure
    /// 
    /// Creates placeholder ground plane and simple objects in each layer
    /// so you can see the depth layering working
    /// </summary>
    public class SceneTestSetup
    {
        #if UNITY_EDITOR

        [MenuItem("Velinor/Scene Setup/Add Test Objects (Visual Debug)", false, 50)]
        public static void AddTestObjects()
        {
            Debug.Log("🔨 Adding test objects to visualize scene structure...");

            // Find or create containers
            Transform foregroundRoot = GameObject.Find("Foreground")?.transform;
            Transform midgroundRoot = GameObject.Find("Midground")?.transform;
            Transform backgroundRoot = GameObject.Find("Background")?.transform;

            if (foregroundRoot == null || midgroundRoot == null || backgroundRoot == null)
            {
                Debug.LogError("❌ Scene containers not found. Run 'Organize Market Scene' first!");
                return;
            }

            // FOREGROUND: Ground Plane
            GameObject groundPlane = GameObject.CreatePrimitive(PrimitiveType.Plane);
            groundPlane.name = "Ground";
            groundPlane.transform.parent = foregroundRoot;
            groundPlane.transform.position = new Vector3(0, 0, 0);
            groundPlane.transform.localScale = new Vector3(10, 1, 10);
            groundPlane.GetComponent<Collider>().enabled = false; // Don't need physics collider
            SetMaterialColor(groundPlane, new Color(0.6f, 0.55f, 0.5f)); // Gray-brown
            Debug.Log("✅ Created Ground Plane (Foreground)");

            // MIDGROUND: Test Cube (market stall placeholder)
            GameObject midgroundCube = GameObject.CreatePrimitive(PrimitiveType.Cube);
            midgroundCube.name = "TestStall";
            midgroundCube.transform.parent = midgroundRoot;
            midgroundCube.transform.position = new Vector3(0, 1, 10);
            midgroundCube.transform.localScale = new Vector3(3, 2, 2);
            midgroundCube.GetComponent<Collider>().enabled = false;
            SetMaterialColor(midgroundCube, new Color(0.9f, 0.8f, 0.6f)); // Tan/beige
            Debug.Log("✅ Created Test Stall (Midground)");

            // BACKGROUND: Mountain placeholder
            GameObject backgroundCube = GameObject.CreatePrimitive(PrimitiveType.Cube);
            backgroundCube.name = "TestMountain";
            backgroundCube.transform.parent = backgroundRoot;
            backgroundCube.transform.position = new Vector3(0, 5, 25);
            backgroundCube.transform.localScale = new Vector3(20, 15, 5);
            backgroundCube.GetComponent<Collider>().enabled = false;
            SetMaterialColor(backgroundCube, new Color(0.4f, 0.4f, 0.4f)); // Dark gray
            Debug.Log("✅ Created Test Mountain (Background)");

            // Add simple lighting if none exists
            if (FindObjectOfType<Light>() == null)
            {
                GameObject lightObj = new GameObject("Directional Light");
                Light light = lightObj.AddComponent<Light>();
                light.type = LightType.Directional;
                light.color = new Color(1f, 0.7f, 0.4f); // Warm dusk color
                light.intensity = 0.8f;
                lightObj.transform.eulerAngles = new Vector3(45, 315, 0);
                Debug.Log("✅ Created Dusk Directional Light");
            }

            Debug.Log("\n✅ TEST SETUP COMPLETE!");
            Debug.Log("📋 You should now see:");
            Debug.Log("   - Ground plane (foreground, gray-brown)");
            Debug.Log("   - Tan cube (midground market stall)");
            Debug.Log("   - Dark cube (background mountain)");
            Debug.Log("\n💡 This is just for visualization. Replace these with real assets from:");
            Debug.Log("   - Kyle's Rock Pack (mountains, rocks)");
            Debug.Log("   - Mediterranean Ruins Kit (market stalls)");
            Debug.Log("   - Other imported asset packs");
            Debug.Log("\n📋 Next: Delete these test objects and import real assets from Asset Store packages");
        }

        private static void SetMaterialColor(GameObject obj, Color color)
        {
            Renderer renderer = obj.GetComponent<Renderer>();
            if (renderer != null)
            {
                Material mat = new Material(Shader.Find("Standard"));
                mat.color = color;
                renderer.material = mat;
            }
        }

        #endif
    }
}
