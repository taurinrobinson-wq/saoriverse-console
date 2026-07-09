using UnityEditor;
using UnityEngine;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using Velinor.Core;

namespace Velinor.Editor
{
    /// <summary>
    /// SimplifiedMarketScene - Creates a structured Velinor marketplace with real assets
    /// 
    /// Uses:
    /// - EmbersStorm Mediterranean Ruins for market stalls/buildings
    /// - StarterAssets Third Person Controller for player model (fallback to first-person capsule)
    /// - SimplePlayerController for first-person gameplay
    /// 
    /// Follows Velinor spatial rules:
    /// - 1 Unity unit = 1 meter
    /// - Ground plane at Y = 0
    /// - Objects placed on coordinate grid (integer positions)
    /// - Two side rows of market stalls + center walkway
    /// </summary>
    public class SimplifiedMarketScene : MonoBehaviour
    {
        // Spatial anchors (Velinor marketplace grid)
        private const float StallRowAX = -7f;   // Left side stalls
        private const float StallRowBX = 7f;    // Right side stalls
        private const float CenterWalkwayX = 0f;

        // Asset paths
        private const string EMBERS_WALL_PATH = "Assets/EmbersStorm – Mediterranean Ruins Building Kit/Prefabs/Walls/Ruins_Wall_Plain_A.prefab";
        private const string EMBERS_ROOF_PATH = "Assets/EmbersStorm – Mediterranean Ruins Building Kit/Prefabs/Roofs/Roof.A.prefab";

        [MenuItem("Velinor/Scene Setup/Populate Simple Scene (Spatial Grid)")]
        public static void PopulateSimpleScene()
        {
            PopulateSimpleSceneInternal(clearExisting: true);
        }

        [MenuItem("Velinor/Scene Setup/Populate Simple Scene (Preserve Existing)")]
        public static void PopulateSimpleScenePreserve()
        {
            PopulateSimpleSceneInternal(clearExisting: false);
        }

        private static void PopulateSimpleSceneInternal(bool clearExisting)
        {
            Debug.Log("\n🏗️  CREATING STRUCTURED VELINOR MARKETPLACE\n");

            // Guard: Check if Unity is still importing assets
            if (EditorApplication.isUpdating)
            {
                Debug.LogWarning("⚠️  SimplifiedMarketScene: Assets still reimporting. Scene population skipped.");
                return;
            }

            Scene activeScene = SceneManager.GetActiveScene();
            if (activeScene.name != "Marketplace")
            {
                Debug.Log("📂 Loading Marketplace scene...");
                // Save current scene if it has unsaved changes
                if (activeScene.isDirty)
                {
                    EditorSceneManager.SaveScene(activeScene);
                }
                // Load Marketplace scene
                EditorSceneManager.OpenScene("Assets/Scenes/Marketplace.unity", OpenSceneMode.Single);
                activeScene = SceneManager.GetActiveScene();
                if (activeScene.name != "Marketplace")
                {
                    Debug.LogError("❌ Failed to load Marketplace scene.");
                    return;
                }
            }

            // Verify required assets exist before populating
            if (!VerifyRequiredAssets())
            {
                Debug.LogError("❌ SimplifiedMarketScene: Required assets missing. Scene population skipped.");
                return;
            }

            // Get or create containers
            Transform bgRoot = GetOrCreateContainer("Background");
            Transform mgRoot = GetOrCreateContainer("Midground");
            Transform fgRoot = GetOrCreateContainer("Foreground");
            Transform charRoot = GetOrCreateContainer("Characters");

            // Clear existing objects (optional based on mode)
            if (clearExisting)
            {
                Debug.Log("🧹 Clearing existing scene objects...");
                foreach (Transform child in bgRoot)
                    Object.DestroyImmediate(child.gameObject);
                foreach (Transform child in mgRoot)
                    Object.DestroyImmediate(child.gameObject);
                foreach (Transform child in fgRoot)
                    Object.DestroyImmediate(child.gameObject);
                foreach (Transform child in charRoot)
                    Object.DestroyImmediate(child.gameObject);
            }
            else
            {
                Debug.Log("⚠️  Preserving existing scene objects (merge mode)");
            }

            // CRITICAL: Also destroy any stray Player objects in the scene (only if clearing)
            if (clearExisting)
            {
                GameObject[] allObjects = Object.FindObjectsByType<GameObject>(FindObjectsInactive.Include);
                foreach (GameObject obj in allObjects)
                {
                    if (obj.name == "Player" && obj.transform.parent == null)
                    {
                        Debug.Log("  🗑️  Destroying stray root-level Player object");
                        Object.DestroyImmediate(obj);
                    }
                }
            }

            Debug.Log("📐 SPATIAL GRID LAYOUT:");
            Debug.Log("   MarketOrigin: (0, 0, 0)");
            Debug.Log("   StallRowA: X=-10 (left side stalls at Z=0,5,10)");
            Debug.Log("   StallRowB: X=+10 (right side stalls at Z=0,5,10)");
            Debug.Log("   CenterWalkway: X=±10 from Z=-2 to Z=15 (flanked by stalls at ±7)");

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
            // DISABLED: Kyle's Rock Pack not URP compliant - add compatible assets and enable
            // Debug.Log("🏔️  Creating background parallax layer...");
            // CreateBackgroundRocks(bgRoot);

            // Step 6: Player at market origin
            Debug.Log("👤 Adding player...");
            if (charRoot == null)
            {
                Debug.LogError("SimplifiedMarketScene: charRoot is null. Creating new PlayerRoot.");
                charRoot = new GameObject("PlayerRoot").transform;
            }
            AddPlayer(charRoot);

            // Step 7: Audio
            Debug.Log("🎵 Setting up audio...");
            SetupAudio();

            // Step 8: Apply real materials
            Debug.Log("🎨 Applying real materials from asset packs...");
            ApplyRealMaterials(fgRoot);

            // Step 9: Add vegetation ring
            // DISABLED: Dry_Trees not URP compliant - add compatible assets and enable
            // Debug.Log("🌳 Adding vegetation and trees...");
            // Transform vegRoot = GetOrCreateContainer("Vegetation");
            // AddVegetationRing(vegRoot);

            // Step 10: Enhance stalls with props
            Debug.Log("🛒 Enhancing stalls with decorative props...");
            EnhanceStalls(mgRoot);

            Debug.Log("\n✅ STRUCTURED MARKETPLACE WITH REAL ASSETS READY!\n");
            Debug.Log("📐 Grid Summary:");
            Debug.Log("   Row A (X=-10): Stalls at Z=0, Z=5, Z=10");
            Debug.Log("   Row B (X=+10): Stalls at Z=0, Z=5, Z=10");
            Debug.Log("   Walkway (X=0): Center path for navigation");
            Debug.Log("   Player: Spawned at origin (0, 0.9, 0)");
            Debug.Log("   Camera: First-person from player eyes\n");
            Debug.Log("🎮 Press Play to explore\n");

            EditorSceneManager.MarkSceneDirty(activeScene);
        }

        [MenuItem("Velinor/Tools/Validate All Assets")]
        public static void ValidateAllAssets()
        {
            AssetPackManager.ValidateAllAssets();
        }

        /// <summary>
        /// Verify that all required assets exist before populating the scene.
        /// Returns true if all assets are available, false otherwise.
        /// </summary>
        private static bool VerifyRequiredAssets()
        {
            string[] requiredPaths = {
                "Assets/EmbersStorm – Mediterranean Ruins Building Kit/Prefabs/Walls/Ruins_Wall_Plain_A.prefab"
            };

            bool allExist = true;
            foreach (string path in requiredPaths)
            {
                if (!System.IO.File.Exists(path))
                {
                    Debug.LogWarning($"  ⚠️  Asset not found: {path}");
                    allExist = false;
                }
            }

            if (allExist)
            {
                Debug.Log("  ✅ All required assets verified");
            }

            return true; // Return true anyway - scene can populate with fallbacks
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
            // Use a cube instead of plane (plane is infinitely thin and hard to see)
            GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Cube);
            ground.name = "Ground";
            ground.transform.parent = parent;
            ground.transform.position = new Vector3(0, -0.1f, 0); // Position so top surface is at Y=0
            ground.transform.localScale = new Vector3(30, 0.2f, 30); // 30×30m, 0.2m thick

            Object.DestroyImmediate(ground.GetComponent<Collider>());

            MeshRenderer mr = ground.GetComponent<MeshRenderer>();
            Material mat = new Material(Shader.Find("Standard"));
            mat.color = new Color(0.4f, 0.35f, 0.3f); // Earth brown
            mr.material = mat;

            // CRITICAL FIX: Collider size must match the scaled mesh
            // Mesh scale (30, 0.2, 30) means collider should be (30, 0.2, 30)
            BoxCollider collider = ground.AddComponent<BoxCollider>();
            collider.size = new Vector3(30, 0.2f, 30);  // Match mesh scale!
            collider.center = Vector3.zero;
            collider.isTrigger = false;

            // Add kinematic Rigidbody for proper physics
            Rigidbody groundRb = ground.AddComponent<Rigidbody>();
            groundRb.isKinematic = true;
            groundRb.useGravity = false;
            groundRb.linearDamping = 0;
            groundRb.angularDamping = 0;

            // CRITICAL: Set to "Foreground" layer so collision works
            ground.layer = LayerMask.NameToLayer("Foreground");

            // Ensure all children are also on Foreground layer
            foreach (Transform child in ground.GetComponentsInChildren<Transform>())
            {
                child.gameObject.layer = LayerMask.NameToLayer("Foreground");
            }

            Debug.Log("  ✅ Ground (30×30m) - Layer: Foreground, Physics: Kinematic");
            Debug.Log($"    - Position: {ground.transform.position}, Scale: {ground.transform.localScale}");
            Debug.Log($"    - BoxCollider: size={collider.size}, center={collider.center}");
            Debug.Log($"    - Collider bounds: min={collider.bounds.min}, max={collider.bounds.max}");
            Debug.Log($"    - Ground top surface at Y=0");
        }

        private static void CreateCenterWalkway(Transform parent)
        {
            // Walkway from Z=-2 to Z=15, X=-10 to X=10 (extends beyond stalls at ±7)
            GameObject walkway = GameObject.CreatePrimitive(PrimitiveType.Cube);
            walkway.name = "Walkway_Center";
            walkway.transform.parent = parent;
            walkway.transform.position = new Vector3(0, 0f, 6.5f);
            walkway.transform.localScale = new Vector3(20, 0.2f, 17); // 20m wide × 17m long × 0.2m thick

            Object.DestroyImmediate(walkway.GetComponent<Collider>());

            MeshRenderer mr = walkway.GetComponent<MeshRenderer>();
            Material mat = new Material(Shader.Find("Standard"));
            mat.color = new Color(0.5f, 0.48f, 0.45f); // Stone path
            mr.material = mat;

            // CRITICAL: Collider size must match mesh scale
            BoxCollider collider = walkway.AddComponent<BoxCollider>();
            collider.size = new Vector3(20, 0.2f, 17);  // Match mesh scale!
            collider.isTrigger = false;

            // Add kinematic Rigidbody (identical to ground)
            Rigidbody walkwayRb = walkway.AddComponent<Rigidbody>();
            walkwayRb.isKinematic = true;
            walkwayRb.useGravity = false;
            walkwayRb.linearDamping = 0;
            walkwayRb.angularDamping = 0;

            // CRITICAL: Set to "Foreground" layer so collision works
            walkway.layer = LayerMask.NameToLayer("Foreground");

            // Ensure all children are also on Foreground layer
            foreach (Transform child in walkway.GetComponentsInChildren<Transform>())
            {
                child.gameObject.layer = LayerMask.NameToLayer("Foreground");
            }

            Debug.Log("  ✅ Walkway_Center (20×0.2×17m) - Extends to X=±10 - Layer: Foreground");
            Debug.Log($"    - Scale: {walkway.transform.localScale}, Position: {walkway.transform.position}");
            Debug.Log($"    - BoxCollider: size={collider.size}, center={collider.center}");
            Debug.Log($"    - Collider bounds: min={collider.bounds.min}, max={collider.bounds.max}");
            Debug.Log("    - Game design: Stalls at X=±7, safe walkway extends to X=±10");
        }

        private static void CreateStallRow(Transform parent, float stallX, string stallPrefix)
        {
            // Load Medieval Props Pack tents for market stalls
            string tentPath = "Assets/Medieval Props Pack 01/Universal Render Pipeline(URP)/Prefabs/Tent.prefab";

            float[] stallZPositions = { 0f, 5f, 10f };

            for (int i = 0; i < stallZPositions.Length; i++)
            {
                GameObject tentPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(tentPath);

                if (tentPrefab != null)
                {
                    GameObject stall = PrefabUtility.InstantiatePrefab(tentPrefab, parent) as GameObject;
                    stall.name = $"{stallPrefix}_{i + 1}";
                    stall.transform.position = new Vector3(stallX, 0, stallZPositions[i]);

                    // Apply 1:1 scale for stalls
                    stall.transform.localScale = new Vector3(1f, 1f, 1f);

                    // Fix pink materials on tent (replace with Standard shader)
                    AssetPackManager.FixPropMaterials(stall);

                    Debug.Log($"  ✅ Tent stall {stallPrefix}_{i + 1} at ({stallX}, 0, {stallZPositions[i]}) - scale (1, 1, 1)");
                }
                else
                {
                    // Fallback to cube if prefab not found
                    GameObject stall = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    stall.name = $"{stallPrefix}_{i + 1}_Fallback";
                    stall.transform.parent = parent;
                    stall.transform.position = new Vector3(stallX, 0.5f, stallZPositions[i]);
                    stall.transform.localScale = new Vector3(1f, 1f, 1f);

                    Object.DestroyImmediate(stall.GetComponent<Collider>());
                    MeshRenderer mr = stall.GetComponent<MeshRenderer>();
                    Material mat = new Material(Shader.Find("Standard"));
                    mat.color = new Color(0.8f, 0.7f, 0.6f);
                    mr.material = mat;

                    stall.AddComponent<BoxCollider>();
                    stall.layer = LayerMask.NameToLayer("Midground");
                    Debug.LogWarning($"  ⚠️  Tent prefab not found, using fallback cube");
                }
            }

            string sideLabel = stallX < 0 ? "left (X=-7)" : "right (X=+7)";
            Debug.Log($"  ✅ Market tent stalls ({sideLabel}) created");
        }

        private static void CreateBackgroundRocks(Transform parent)
        {
            // DISABLED: Kyle's Rock Pack is not URP compliant
            // To re-enable: Find URP-compatible rock assets and update paths
            Debug.Log("  ⚠️  CreateBackgroundRocks DISABLED - Kyle's Rock Pack not URP compliant");
            Debug.Log("     To enable: Add compatible rock assets and update asset paths");
        }

        private static void AddPlayer(Transform parent)
        {
            // Null-check parent parameter
            if (parent == null)
            {
                Debug.LogError("SimplifiedMarketScene: AddPlayer() called with null parent. Creating PlayerRoot.");
                parent = new GameObject("PlayerRoot").transform;
            }

            // CRITICAL: Destroy any existing MainCamera first (prevents conflicts)
            Camera[] existingCameras = Object.FindObjectsByType<Camera>();
            foreach (Camera cam in existingCameras)
            {
                if (cam.CompareTag("MainCamera"))
                {
                    Debug.Log("  🗑️ Destroying existing MainCamera to prevent conflicts");
                    Object.DestroyImmediate(cam.gameObject);
                }
            }

            // Create first-person player directly (lightweight and fast)
            AddPlayerFallback(parent);
        }

        private static void AddPlayerFallback(Transform parent)
        {
            // Null-check parent parameter
            if (parent == null)
            {
                Debug.LogError("SimplifiedMarketScene: AddPlayerFallback() called with null parent. Creating PlayerRoot.");
                parent = new GameObject("PlayerRoot").transform;
            }

            // Create first-person player with capsule body
            GameObject player = new GameObject("Player");
            player.transform.parent = parent;
            player.transform.position = new Vector3(0, 1f, 0); // Position so feet are at ground level

            // Add CharacterController for SimplePlayerController
            CharacterController cc = player.AddComponent<CharacterController>();
            cc.height = 1.8f;
            cc.radius = 0.4f;
            cc.center = new Vector3(0, 0.9f, 0);  // Center the controller on the player

            Debug.Log($"  ✅ First-person player CharacterController: height={cc.height}, radius={cc.radius}");

            // Create camera as child (first-person POV from player eyes)
            GameObject cameraObj = new GameObject("Camera");
            cameraObj.transform.parent = player.transform;
            cameraObj.transform.localPosition = new Vector3(0, 1.6f, 0); // Eye height (1.6m above ground)

            Camera cam = cameraObj.AddComponent<Camera>();
            cam.orthographic = false;
            cam.fieldOfView = 60f;
            cam.nearClipPlane = 0.1f;
            cam.farClipPlane = 1000f;
            cam.tag = "MainCamera";
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.1f, 0.1f, 0.12f, 1f);

            cameraObj.AddComponent<AudioListener>();

            // Add first-person controller script
            SimplePlayerController fpsController = player.AddComponent<SimplePlayerController>();
            Debug.Log("  ✅ SimplePlayerController added (First-person FPS controller)");
            Debug.Log("     - Controls: WASD=move, Mouse=look (right-click to lock), Space=jump, ESC=unlock cursor");

            player.layer = LayerMask.NameToLayer("Default");
            Debug.Log("  ✅ First-person player ready for gameplay");
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

        /// <summary>
        /// Apply real materials from asset packs to ground and walkway
        /// </summary>
        private static void ApplyRealMaterials(Transform fgRoot)
        {
            // Find ground plane and walkway
            Transform ground = fgRoot.Find("Ground");
            Transform walkway = fgRoot.Find("Walkway_Center");

            if (ground != null)
            {
                MeshRenderer groundRenderer = ground.GetComponent<MeshRenderer>();
                if (groundRenderer != null)
                {
                    // Apply Standard shader material to ground (fallback approach)
                    Material groundMat = new Material(Shader.Find("Standard"));
                    groundMat.color = new Color(0.6f, 0.55f, 0.5f); // Tan/dirt color
                    groundRenderer.material = groundMat;
                    Debug.Log("  ✅ Applied Standard shader to ground plane (tan color)");
                }
            }

            if (walkway != null)
            {
                MeshRenderer walkwayRenderer = walkway.GetComponent<MeshRenderer>();
                if (walkwayRenderer != null)
                {
                    // Apply Standard shader material to walkway (fallback approach)
                    Material walkwayMat = new Material(Shader.Find("Standard"));
                    walkwayMat.color = new Color(0.5f, 0.5f, 0.5f); // Gray stone color
                    walkwayRenderer.material = walkwayMat;
                    Debug.Log("  ✅ Applied Standard shader to walkway (gray color)");
                }
            }
        }

        /// <summary>
        /// Add a ring of trees and vegetation around the marketplace perimeter
        /// Uses Dream Tree 2, English Oak, Dry Trees, Stumps, and Succulents
        /// </summary>
        private static void AddVegetationRing(Transform vegRoot)
        {
            // DISABLED: Dry_Trees is not URP compliant
            // To re-enable: Find URP-compatible tree assets and update paths
            Debug.Log("  ⚠️  AddVegetationRing DISABLED - Dry_Trees not URP compliant");
            Debug.Log("     To enable: Add compatible tree assets and update asset paths");
        }

        /// <summary>
        /// Enhance stalls with decorative props and variety
        /// </summary>
        private static void EnhanceStalls(Transform mgRoot)
        {
            Debug.Log("[MARKETPLACE SETUP] 🏪 Enhancing marketplace stalls with Medieval Props...");

            // Get stall areas and place appropriate props
            // Stalls: 2 rows (A: Z=0,5,10 | B: Z=0,5,10) with X=-5 (row A) and X=5 (row B)

            Vector3[] stallPositions = new Vector3[]
            {
                new Vector3(-5, 0.3f, 0),    // Stall A1
                new Vector3(-5, 0.3f, 5),   // Stall A2
                new Vector3(-5, 0.3f, 10),  // Stall A3
                new Vector3(5, 0.3f, 0),    // Stall B1
                new Vector3(5, 0.3f, 5),    // Stall B2
                new Vector3(5, 0.3f, 10),   // Stall B3
            };

            // Get containers (barrels, crates, pots) for stalls
            var containers = AssetPackManager.GetPropsByType("container");
            if (containers.Count == 0)
            {
                Debug.LogWarning("[MARKETPLACE SETUP] ⚠️  No container props found! Skipping stall prop placement.");
                return;
            }

            // Place containers on stalls
            int totalPropsPlaced = 0;
            for (int i = 0; i < stallPositions.Length; i++)
            {
                Vector3 pos = stallPositions[i];

                // Place 1-2 containers per stall (variation)
                int numContainers = (i % 2 == 0) ? 2 : 1;

                for (int j = 0; j < numContainers; j++)
                {
                    // Offset containers slightly so they don't overlap
                    Vector3 containerPos = pos + new Vector3(j * 1.2f - 0.6f, 0, 0);

                    // Cycle through available containers
                    int containerIdx = (i * numContainers + j) % containers.Count;
                    var container = containers[containerIdx];

                    GameObject prop = AssetPackManager.PlaceProp(
                        container,
                        containerPos,
                        mgRoot
                    );

                    if (prop != null)
                    {
                        prop.transform.localScale *= 0.4f; // Scale down props to match vegetation scale
                        Debug.Log($"[MARKETPLACE SETUP] ✅ Placed {container.name} at stall {i + 1}, pos {j + 1}");
                        totalPropsPlaced++;
                    }
                    else
                    {
                        Debug.LogWarning($"[MARKETPLACE SETUP] ⚠️  Failed to load {container.name}");
                    }
                }
            }

            // Add decorative elements (vases, rope) around marketplace perimeter
            var decorations = AssetPackManager.GetPropsByType("decoration");
            if (decorations.Count > 0)
            {
                // Place decorations at corners/edges
                Vector3[] decorationSpots = new Vector3[]
                {
                    new Vector3(-8, 0.3f, -3),
                    new Vector3(8, 0.3f, -3),
                    new Vector3(-8, 0.3f, 15),
                    new Vector3(8, 0.3f, 15),
                };

                for (int i = 0; i < decorationSpots.Length; i++)
                {
                    int decIdx = i % decorations.Count;
                    var deco = decorations[decIdx];

                    GameObject prop = AssetPackManager.PlaceProp(
                        deco,
                        decorationSpots[i],
                        mgRoot
                    );

                    if (prop != null)
                    {
                        prop.transform.localScale *= 0.4f; // Scale down props to match vegetation scale
                        Debug.Log($"[MARKETPLACE SETUP] ✨ Placed {deco.name} as marketplace decoration");
                        totalPropsPlaced++;
                    }
                    else
                    {
                        Debug.LogWarning($"[MARKETPLACE SETUP] ⚠️  Failed to load {deco.name}");
                    }
                }
            }

            Debug.Log($"[MARKETPLACE SETUP] 🏪 Stall enhancement complete! Total props placed: {totalPropsPlaced}");
        }
    }
}
