using UnityEditor;
using UnityEngine;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using Velinor.Core;

namespace Velinor.Editor
{
    /// <summary>
    /// SimplifiedMarketScene - Create a clean, textured marketplace without material loading issues
    /// 
    /// Approach: 
    /// - Load mesh-only geometry from assets
    /// - Apply simple, reliable materials
    /// - Create proper colliders
    /// - Position everything correctly for depth
    /// </summary>
    public class SimplifiedMarketScene
    {
        [MenuItem("Velinor/Scene Setup/Populate Simple Scene (No Materials Issues)")]
        public static void PopulateSimpleScene()
        {
            Debug.Log("\n🏗️  CREATING SIMPLIFIED MARKETPLACE SCENE\n");

            Scene activeScene = SceneManager.GetActiveScene();
            if (activeScene.name != "Marketplace")
            {
                Debug.LogError("❌ Active scene is not 'Marketplace'. Load it first.");
                return;
            }

            // Get or create containers
            Transform bgRoot = GetOrCreateContainer("Background");
            Transform mgRoot = GetOrCreateContainer("Midground");
            Transform fgRoot = GetOrCreateContainer("Foreground");
            Transform charRoot = GetOrCreateContainer("Characters");

            // Clear existing objects
            foreach (Transform child in bgRoot)
                Object.DestroyImmediate(child.gameObject);
            foreach (Transform child in mgRoot)
                Object.DestroyImmediate(child.gameObject);
            foreach (Transform child in fgRoot)
                Object.DestroyImmediate(child.gameObject);
            foreach (Transform child in charRoot)
                Object.DestroyImmediate(child.gameObject);

            // Step 1: Add simple background geometry (rocks)
            Debug.Log("📦 Creating background rocks...");
            AddSimpleBackgroundRocks(bgRoot);

            // Step 2: Add simple market structures (platforms, pillars)
            Debug.Log("🏛️  Creating market structures...");
            AddSimpleMarketStructures(mgRoot);

            // Step 3: Add foreground ground and props
            Debug.Log("🪨 Creating foreground elements...");
            AddSimpleForegroundElements(fgRoot);

            // Step 4: Add player
            Debug.Log("👤 Adding player...");
            AddPlayer(charRoot);

            // Step 5: Verify camera
            Debug.Log("📷 Configuring camera...");
            VerifyAndFixCamera();

            Debug.Log("✅ SIMPLIFIED MARKETPLACE READY!\n");
            Debug.Log("🎮 Press Play to explore. Camera should render properly.\n");

            EditorSceneManager.MarkSceneDirty(activeScene);
        }

        private static Transform GetOrCreateContainer(string name)
        {
            // Find ALL instances of this container name (handles duplicates)
            GameObject[] allObjects = Object.FindObjectsByType<GameObject>(FindObjectsInactive.Include, FindObjectsSortMode.None);
            GameObject existing = null;
            int duplicateCount = 0;

            foreach (GameObject obj in allObjects)
            {
                if (obj.name == name && obj.transform.parent == null) // Root-level objects only
                {
                    if (existing == null)
                    {
                        existing = obj;
                    }
                    else
                    {
                        // Delete duplicate
                        Object.DestroyImmediate(obj);
                        duplicateCount++;
                    }
                }
            }

            if (duplicateCount > 0)
            {
                Debug.Log($"  🧹 Removed {duplicateCount} duplicate '{name}' containers");
            }

            // Use existing or create new
            if (existing != null)
            {
                // Clear all children
                foreach (Transform child in existing.transform)
                {
                    Object.DestroyImmediate(child.gameObject);
                }
                return existing.transform;
            }

            GameObject container = new GameObject(name);
            return container.transform;
        }

        private static void AddSimpleBackgroundRocks(Transform parent)
        {
            // Create simple rocky mountains in background using cubes/capsules
            string[] rockNames = { "BackRock_Left", "BackRock_Center", "BackRock_Right", "BackRock_FarLeft" };
            Vector3[] positions = { new Vector3(-15, 8, 20), new Vector3(0, 10, 25), new Vector3(15, 7, 22), new Vector3(-20, 6, 28) };
            Vector3[] scales = { new Vector3(8, 12, 6), new Vector3(10, 15, 8), new Vector3(7, 10, 5), new Vector3(6, 8, 4) };
            Color[] colors = { new Color(0.4f, 0.4f, 0.35f), new Color(0.45f, 0.42f, 0.38f), new Color(0.42f, 0.41f, 0.36f), new Color(0.38f, 0.37f, 0.33f) };

            for (int i = 0; i < rockNames.Length; i++)
            {
                GameObject rock = GameObject.CreatePrimitive(PrimitiveType.Cube);
                rock.name = rockNames[i];
                rock.transform.parent = parent;
                rock.transform.position = positions[i];
                rock.transform.localScale = scales[i];

                // Remove collider, we'll add a simple one
                Object.DestroyImmediate(rock.GetComponent<Collider>());

                // Apply simple material
                MeshRenderer mr = rock.GetComponent<MeshRenderer>();
                Material mat = new Material(Shader.Find("Standard"));
                mat.color = colors[i];
                mr.material = mat;

                // Add simple collider
                rock.AddComponent<BoxCollider>();

                rock.layer = LayerMask.NameToLayer("Background");
                Debug.Log($"  ✅ {rockNames[i]} created");
            }
        }

        private static void AddSimpleMarketStructures(Transform parent)
        {
            // Create simple market platforms and pillars
            
            // Platforms (floors)
            string[] platformNames = { "Platform_Left", "Platform_Right", "Platform_Center_A", "Platform_Center_B" };
            Vector3[] platformPos = { new Vector3(-8, 0.5f, 5), new Vector3(8, 0.5f, 5), new Vector3(-5, 0.5f, 10), new Vector3(5, 0.5f, 10) };
            Vector3[] platformScale = { new Vector3(6, 0.5f, 6), new Vector3(6, 0.5f, 6), new Vector3(5, 0.5f, 5), new Vector3(5, 0.5f, 5) };
            Color platformColor = new Color(0.65f, 0.6f, 0.5f); // Tan stone

            for (int i = 0; i < platformNames.Length; i++)
            {
                GameObject platform = GameObject.CreatePrimitive(PrimitiveType.Cube);
                platform.name = platformNames[i];
                platform.transform.parent = parent;
                platform.transform.position = platformPos[i];
                platform.transform.localScale = platformScale[i];

                Object.DestroyImmediate(platform.GetComponent<Collider>());

                MeshRenderer mr = platform.GetComponent<MeshRenderer>();
                Material mat = new Material(Shader.Find("Standard"));
                mat.color = platformColor;
                mr.material = mat;

                platform.AddComponent<BoxCollider>();
                platform.layer = LayerMask.NameToLayer("Midground");
            }

            // Pillars (support structures)
            string[] pillarNames = { "Pillar_Left", "Pillar_Right", "Pillar_Center" };
            Vector3[] pillarPos = { new Vector3(-10, 1.5f, 8), new Vector3(10, 1.5f, 8), new Vector3(0, 1.5f, 12) };
            Vector3[] pillarScale = { new Vector3(1, 3, 1), new Vector3(1, 3, 1), new Vector3(1.5f, 4, 1.5f) };
            Color pillarColor = new Color(0.55f, 0.52f, 0.45f); // Darker stone

            for (int i = 0; i < pillarNames.Length; i++)
            {
                GameObject pillar = GameObject.CreatePrimitive(PrimitiveType.Cube);
                pillar.name = pillarNames[i];
                pillar.transform.parent = parent;
                pillar.transform.position = pillarPos[i];
                pillar.transform.localScale = pillarScale[i];

                Object.DestroyImmediate(pillar.GetComponent<Collider>());

                MeshRenderer mr = pillar.GetComponent<MeshRenderer>();
                Material mat = new Material(Shader.Find("Standard"));
                mat.color = pillarColor;
                mr.material = mat;

                pillar.AddComponent<BoxCollider>();
                pillar.layer = LayerMask.NameToLayer("Midground");
            }

            Debug.Log($"  ✅ Created {platformNames.Length} platforms and {pillarNames.Length} pillars");
        }

        private static void AddSimpleForegroundElements(Transform parent)
        {
            // Ground plane
            GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Ground";
            ground.transform.parent = parent;
            ground.transform.position = Vector3.zero;
            ground.transform.localScale = new Vector3(15, 1, 15);

            Object.DestroyImmediate(ground.GetComponent<Collider>());

            MeshRenderer mr = ground.GetComponent<MeshRenderer>();
            Material groundMat = new Material(Shader.Find("Standard"));
            groundMat.color = new Color(0.6f, 0.55f, 0.5f); // Brown-tan
            mr.material = groundMat;

            ground.AddComponent<BoxCollider>();
            ground.layer = LayerMask.NameToLayer("Foreground");

            // Small rocks scattered
            string[] rockNames = { "Scatter_Rock_1", "Scatter_Rock_2", "Scatter_Rock_3", "Scatter_Rock_4" };
            Vector3[] rockPos = { new Vector3(-5, 0.3f, -1), new Vector3(6, 0.3f, 0), new Vector3(-3, 0.3f, 1), new Vector3(4, 0.3f, -2) };
            Vector3[] rockScale = { new Vector3(1.5f, 1, 1), new Vector3(1.2f, 0.9f, 1), new Vector3(1, 1.2f, 0.8f), new Vector3(1.3f, 0.8f, 1.1f) };
            Color rockColor = new Color(0.5f, 0.48f, 0.45f);

            for (int i = 0; i < rockNames.Length; i++)
            {
                GameObject rock = GameObject.CreatePrimitive(PrimitiveType.Cube);
                rock.name = rockNames[i];
                rock.transform.parent = parent;
                rock.transform.position = rockPos[i];
                rock.transform.localScale = rockScale[i];

                Object.DestroyImmediate(rock.GetComponent<Collider>());

                MeshRenderer rockMr = rock.GetComponent<MeshRenderer>();
                Material rockMat = new Material(Shader.Find("Standard"));
                rockMat.color = rockColor;
                rockMr.material = rockMat;

                rock.AddComponent<BoxCollider>();
                rock.layer = LayerMask.NameToLayer("Foreground");
            }

            Debug.Log($"  ✅ Ground plane and {rockNames.Length} scatter rocks created");
        }

        private static void AddPlayer(Transform parent)
        {
            GameObject player = new GameObject("Player");
            player.transform.parent = parent;
            player.transform.position = new Vector3(0, 1, -3);

            // Visual representation
            GameObject visual = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            visual.transform.parent = player.transform;
            visual.transform.localPosition = Vector3.zero;
            visual.name = "Model";

            Object.DestroyImmediate(visual.GetComponent<Collider>());

            MeshRenderer vmr = visual.GetComponent<MeshRenderer>();
            Material playerMat = new Material(Shader.Find("Standard"));
            playerMat.color = new Color(0.2f, 0.8f, 0.3f);
            vmr.material = playerMat;

            // Physics
            CapsuleCollider collider = player.AddComponent<CapsuleCollider>();
            collider.radius = 0.5f;
            collider.height = 2f;

            Rigidbody rb = player.AddComponent<Rigidbody>();
            rb.mass = 1;
            rb.linearDamping = 5;
            rb.angularDamping = 0.05f;
            rb.useGravity = true;
            rb.constraints = RigidbodyConstraints.FreezeRotation;

            // Camera
            GameObject cameraObj = new GameObject("CameraHolder");
            cameraObj.transform.parent = player.transform;
            cameraObj.transform.localPosition = new Vector3(0, 0.6f, 0);

            Camera cam = cameraObj.AddComponent<Camera>();
            cam.orthographic = true;
            cam.orthographicSize = 5;
            cam.cullingMask = -1;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.08f, 0.08f, 0.08f, 1f);

            AudioListener listener = cameraObj.AddComponent<AudioListener>();

            // Movement controller
            player.AddComponent<PlayerController>();

            player.layer = LayerMask.NameToLayer("Default");
            Debug.Log("  ✅ Player created with built-in camera");
        }

        private static void VerifyAndFixCamera()
        {
            // Get the player's camera
            PlayerController pc = Object.FindAnyObjectByType<PlayerController>();
            if (pc != null)
            {
                Camera cam = pc.GetComponentInChildren<Camera>();
                if (cam != null)
                {
                    cam.orthographic = true;
                    cam.orthographicSize = 5;
                    cam.cullingMask = -1;
                    cam.clearFlags = CameraClearFlags.SolidColor;
                    cam.backgroundColor = new Color(0.08f, 0.08f, 0.08f, 1f);
                    Debug.Log("  ✅ Camera verified and configured");
                    return;
                }
            }

            // Fallback: find main camera
            Camera mainCam = Camera.main;
            if (mainCam == null)
            {
                mainCam = Object.FindAnyObjectByType<Camera>();
            }

            if (mainCam != null)
            {
                mainCam.orthographic = true;
                mainCam.orthographicSize = 5;
                mainCam.cullingMask = -1;
                mainCam.clearFlags = CameraClearFlags.SolidColor;
                mainCam.backgroundColor = new Color(0.08f, 0.08f, 0.08f, 1f);
                Debug.Log("  ✅ Main camera configured");
            }
        }
    }
}
