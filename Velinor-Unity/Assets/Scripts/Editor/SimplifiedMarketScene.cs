using UnityEditor;
using UnityEngine;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using Velinor.Core;

namespace Velinor.Editor
{
    /// <summary>
    /// SimplifiedMarketScene - Creates a structured Velinor marketplace with spatial grid
    /// 
    /// Follows Velinor spatial rules:
    /// - 1 Unity unit = 1 meter
    /// - Ground plane at Y = 0
    /// - Objects placed on coordinate grid (integer positions)
    /// - Two side rows of market stalls + center walkway
    /// - Camera positioned at spatial anchor (0, 5, -10) with 20° tilt
    /// </summary>
    public class SimplifiedMarketScene : MonoBehaviour
    {
        // Spatial anchors (Velinor marketplace grid)
        private const float StallRowAX = -10f;  // Left side stalls
        private const float StallRowBX = 10f;   // Right side stalls
        private const float CenterWalkwayX = 0f;

        private const float CameraPositionX = 0f;
        private const float CameraPositionY = 5f;
        private const float CameraPositionZ = -10f;
        private const float CameraRotationX = 20f; // Tilted view

        [MenuItem("Velinor/Scene Setup/Populate Simple Scene (Spatial Grid)")]
        public static void PopulateSimpleScene()
        {
            Debug.Log("\n🏗️  CREATING STRUCTURED VELINOR MARKETPLACE\n");

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

            Debug.Log("📐 SPATIAL GRID LAYOUT:");
            Debug.Log("   MarketOrigin: (0, 0, 0)");
            Debug.Log("   StallRowA: X=-10 (left side stalls at Z=0,5,10)");
            Debug.Log("   StallRowB: X=+10 (right side stalls at Z=0,5,10)");
            Debug.Log("   CenterWalkway: X=0 from Z=-2 to Z=15");

            // Step 1: Ground plane
            Debug.Log("🌍 Creating ground plane...");
            CreateGroundPlane(fgRoot);

            // Step 2: Walkway (center path)
            Debug.Log("🛤️  Creating center walkway...");
            CreateCenterWalkway(fgRoot);

            // Step 3: Market stalls (Row A - left side)
            Debug.Log("🏪 Creating Row A (left side stalls)...");
            CreateStallRow(mgRoot, StallRowAX, "Stall_A");

            // Step 4: Market stalls (Row B - right side)
            Debug.Log("🏪 Creating Row B (right side stalls)...");
            CreateStallRow(mgRoot, StallRowBX, "Stall_B");

            // Step 5: Background rocks (parallax depth)
            Debug.Log("🏔️  Creating background parallax layer...");
            CreateBackgroundRocks(bgRoot);

            // Step 6: Player at market origin
            Debug.Log("👤 Adding player...");
            AddPlayer(charRoot);

            // Step 7: Main camera at anchor point
            Debug.Log("📷 Configuring main camera...");
            ConfigureMainCamera();

            // Step 8: Audio
            Debug.Log("🎵 Setting up audio...");
            SetupAudio();

            Debug.Log("\n✅ STRUCTURED MARKETPLACE READY!\n");
            Debug.Log("📐 Grid Summary:");
            Debug.Log("   Row A (X=-10): Stalls at Z=0, Z=5, Z=10");
            Debug.Log("   Row B (X=+10): Stalls at Z=0, Z=5, Z=10");
            Debug.Log("   Walkway (X=0): Center path for navigation");
            Debug.Log("   Player: Spawned at origin (0, 0.9, 0)");
            Debug.Log("   Camera: At (0, 5, -10) looking down 20°\n");
            Debug.Log("🎮 Press Play to explore\n");

            EditorSceneManager.MarkSceneDirty(activeScene);
        }

        private static Transform GetOrCreateContainer(string name)
        {
            // Find ALL instances of this container name (handles duplicates)
            GameObject[] allObjects = Object.FindObjectsByType<GameObject>(FindObjectsInactive.Include);
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

        private static void CreateGroundPlane(Transform parent)
        {
            GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Ground";
            ground.transform.parent = parent;
            ground.transform.position = Vector3.zero; // Y=0 world ground level
            ground.transform.localScale = new Vector3(10, 1, 10); // 20×20 meter plane

            Object.DestroyImmediate(ground.GetComponent<Collider>());

            MeshRenderer mr = ground.GetComponent<MeshRenderer>();
            Material mat = new Material(Shader.Find("Standard"));
            mat.color = new Color(0.4f, 0.35f, 0.3f); // Earth brown
            mr.material = mat;

            BoxCollider collider = ground.AddComponent<BoxCollider>();
            collider.size = new Vector3(10, 0.1f, 10);

            ground.layer = LayerMask.NameToLayer("Foreground");
            Debug.Log("  ✅ Ground plane at Y=0, 20×20m");
        }

        private static void CreateCenterWalkway(Transform parent)
        {
            // Walkway from Z=-2 to Z=15, X=-3 to X=3, Y=0.01f (slightly above ground)
            GameObject walkway = GameObject.CreatePrimitive(PrimitiveType.Plane);
            walkway.name = "Walkway_Center";
            walkway.transform.parent = parent;
            walkway.transform.position = new Vector3(0, 0.01f, 6.5f); // Centered on Z-axis
            walkway.transform.localScale = new Vector3(3, 1, 8.5f); // 6m wide × 17m long

            Object.DestroyImmediate(walkway.GetComponent<Collider>());

            MeshRenderer mr = walkway.GetComponent<MeshRenderer>();
            Material mat = new Material(Shader.Find("Standard"));
            mat.color = new Color(0.5f, 0.48f, 0.45f); // Stone path
            mr.material = mat;

            BoxCollider collider = walkway.AddComponent<BoxCollider>();
            collider.size = new Vector3(3, 0.05f, 8.5f);

            walkway.layer = LayerMask.NameToLayer("Foreground");
            Debug.Log("  ✅ Center walkway: (-3,0,-2) to (3,0,15)");
        }

        private static void CreateStallRow(Transform parent, float stallX, string stallPrefix)
        {
            // Three stalls per row at Z=0, Z=5, Z=10
            // All at Y=0.5 (half-height, snapped to grid)
            float[] stallZPositions = { 0f, 5f, 10f };

            for (int i = 0; i < stallZPositions.Length; i++)
            {
                GameObject stall = GameObject.CreatePrimitive(PrimitiveType.Cube);
                stall.name = $"{stallPrefix}{i + 1}";
                stall.transform.parent = parent;
                stall.transform.position = new Vector3(stallX, 0.5f, stallZPositions[i]);
                stall.transform.localScale = new Vector3(1, 1, 1); // Standard 1×1×1 stall (snapped to grid)

                Object.DestroyImmediate(stall.GetComponent<Collider>());

                MeshRenderer mr = stall.GetComponent<MeshRenderer>();
                Material mat = new Material(Shader.Find("Standard"));
                mat.color = new Color(0.65f, 0.6f, 0.5f); // Tan wood
                mr.material = mat;

                stall.AddComponent<BoxCollider>();
                stall.layer = LayerMask.NameToLayer("Midground");
            }

            string sideLabel = stallX < 0 ? "left (X=-10)" : "right (X=+10)";
            Debug.Log($"  ✅ Created 3 stalls ({sideLabel}) at Z=0, Z=5, Z=10");
        }

        private static void CreateBackgroundRocks(Transform parent)
        {
            // Distant parallax rocks at Z=25+ for depth perception
            // Positioned to frame the marketplace without blocking view
            string[] rockNames = { "Rock_BackLeft", "Rock_BackCenter", "Rock_BackRight" };
            Vector3[] positions = { new Vector3(-8, 3, 25), new Vector3(0, 4, 28), new Vector3(8, 3, 26) };
            Vector3[] scales = { new Vector3(2, 3, 2), new Vector3(2.5f, 3.5f, 2.5f), new Vector3(2, 3, 2) };

            for (int i = 0; i < rockNames.Length; i++)
            {
                GameObject rock = GameObject.CreatePrimitive(PrimitiveType.Cube);
                rock.name = rockNames[i];
                rock.transform.parent = parent;
                rock.transform.position = positions[i];
                
                // Enforce 3-unit maximum dimension rule
                Vector3 scale = scales[i];
                if (scale.x > 3 || scale.y > 3 || scale.z > 3)
                {
                    Debug.LogWarning($"  ⚠️  {rockNames[i]} scale {scale} exceeds 3m limit, clamping");
                    scale.x = Mathf.Min(scale.x, 3);
                    scale.y = Mathf.Min(scale.y, 3);
                    scale.z = Mathf.Min(scale.z, 3);
                }
                rock.transform.localScale = scale;

                Object.DestroyImmediate(rock.GetComponent<Collider>());

                MeshRenderer mr = rock.GetComponent<MeshRenderer>();
                Material mat = new Material(Shader.Find("Standard"));
                mat.color = new Color(0.4f, 0.4f, 0.35f); // Gray stone
                mr.material = mat;

                rock.AddComponent<BoxCollider>();
                rock.layer = LayerMask.NameToLayer("Background");
            }

            Debug.Log("  ✅ Background parallax rocks at Z=25+ (depth layer)");
        }

        private static void AddPlayer(Transform parent)
        {
            // Player spawns at market origin on the ground
            GameObject player = new GameObject("Player");
            player.transform.parent = parent;
            player.transform.position = new Vector3(0, 0.9f, 0); // Y=0.9 (standing on ground, 1.8m height)

            // Visual: Green capsule (character height 1.8m)
            GameObject visual = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            visual.transform.parent = player.transform;
            visual.transform.localPosition = Vector3.zero;
            visual.name = "Model";

            Object.DestroyImmediate(visual.GetComponent<Collider>());

            MeshRenderer vmr = visual.GetComponent<MeshRenderer>();
            Material playerMat = new Material(Shader.Find("Standard"));
            playerMat.color = new Color(0.2f, 0.8f, 0.3f); // Green
            vmr.material = playerMat;

            // Physics
            CapsuleCollider collider = player.AddComponent<CapsuleCollider>();
            collider.radius = 0.4f;
            collider.height = 1.8f; // Standard character height

            Rigidbody rb = player.AddComponent<Rigidbody>();
            rb.mass = 1;
            rb.linearDamping = 5;
            rb.angularDamping = 0.05f;
            rb.useGravity = true;
            rb.constraints = RigidbodyConstraints.FreezeRotation;

            // Camera (eye-level)
            GameObject cameraObj = new GameObject("CameraHolder");
            cameraObj.transform.parent = player.transform;
            cameraObj.transform.localPosition = new Vector3(0, 0.9f, 0); // Eyes at 1.8m height

            Camera cam = cameraObj.AddComponent<Camera>();
            cam.orthographic = true;
            cam.orthographicSize = 6;
            cam.nearClipPlane = -100;
            cam.farClipPlane = 100;
            cam.cullingMask = -1;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.1f, 0.1f, 0.12f, 1f);

            cameraObj.AddComponent<AudioListener>();
            player.AddComponent<PlayerController>();

            player.layer = LayerMask.NameToLayer("Default");
            Debug.Log("  ✅ Player spawned at market origin (0, 0.9, 0) - height 1.8m");
        }

        private static void ConfigureMainCamera()
        {
            // Create main camera at fixed spatial anchor
            GameObject cameraGO = new GameObject("MainCamera");
            cameraGO.transform.position = new Vector3(CameraPositionX, CameraPositionY, CameraPositionZ);
            cameraGO.transform.rotation = Quaternion.Euler(CameraRotationX, 0, 0); // 20° tilt for overview

            Camera cam = cameraGO.AddComponent<Camera>();
            cam.orthographic = true;
            cam.orthographicSize = 6;
            cam.nearClipPlane = -100;
            cam.farClipPlane = 100;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.1f, 0.1f, 0.12f, 1f);
            cam.tag = "MainCamera";

            // DO NOT add AudioListener here - player's camera already has one!
            // Only one AudioListener allowed per scene

            Debug.Log($"  ✅ Main camera at ({CameraPositionX}, {CameraPositionY}, {CameraPositionZ})");
            Debug.Log($"     Rotation: ({CameraRotationX}°, 0°, 0°) tilted down");
            Debug.Log($"     Orthographic size: 6");
        }

        private static void SetupAudio()
        {
            // Find or create AudioManager
            AudioManager audioManager = Object.FindAnyObjectByType<AudioManager>();
            if (audioManager == null)
            {
                GameObject audioManagerGO = new GameObject("AudioManager");
                audioManager = audioManagerGO.AddComponent<AudioManager>();
                Debug.Log("  ✅ Created AudioManager");
            }

            // Find or create MarketSceneAudioSetup
            MarketSceneAudioSetup sceneAudio = Object.FindAnyObjectByType<MarketSceneAudioSetup>();
            if (sceneAudio == null)
            {
                GameObject sceneAudioGO = new GameObject("MarketSceneAudio");
                sceneAudio = sceneAudioGO.AddComponent<MarketSceneAudioSetup>();
                Debug.Log("  ✅ Created MarketSceneAudioSetup (Glass Horizon will loop)");
            }
            else
            {
                Debug.Log("  ✅ Audio system ready");
            }
        }
    }
}
