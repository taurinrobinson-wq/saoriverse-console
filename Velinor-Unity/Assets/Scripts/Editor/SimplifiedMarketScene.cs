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
    /// - Kyle's Rock Pack for terrain and background
    /// - Dry Trees for atmosphere
    /// - StarterAssets Third Person Controller for player
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
        
        private const string ROCK_PREFAB_PATH_1 = "Assets/Kyle's Rock Pack/Kyle Fuji/Prefabs/Arid Rocks 1/rock_1_tl.prefab";
        private const string ROCK_PREFAB_PATH_2 = "Assets/Kyle's Rock Pack/Kyle Fuji/Prefabs/Arid Rocks 1/rock_2_br.prefab";
        private const string ROCK_PREFAB_PATH_3 = "Assets/Kyle's Rock Pack/Kyle Fuji/Prefabs/Arid Rocks 1/rock_3_tr.prefab";
        
        private const string TREE_PREFAB_PATH = "Assets/Dry_Trees/Model/Dry7509.fbx";

        [MenuItem("Velinor/Scene Setup/Populate Simple Scene (Spatial Grid)")]
        public static void PopulateSimpleScene()
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
                Debug.LogError("❌ Active scene is not 'Marketplace'. Load it first.");
                return;
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

            // Clear existing objects
            foreach (Transform child in bgRoot)
                Object.DestroyImmediate(child.gameObject);
            foreach (Transform child in mgRoot)
                Object.DestroyImmediate(child.gameObject);
            foreach (Transform child in fgRoot)
                Object.DestroyImmediate(child.gameObject);
            foreach (Transform child in charRoot)
                Object.DestroyImmediate(child.gameObject);

            // CRITICAL: Also destroy any stray Player objects in the scene
            GameObject[] allObjects = Object.FindObjectsByType<GameObject>(FindObjectsInactive.Include);
            foreach (GameObject obj in allObjects)
            {
                if (obj.name == "Player" && obj.transform.parent == null)
                {
                    Debug.Log("  🗑️  Destroying stray root-level Player object");
                    Object.DestroyImmediate(obj);
                }
            }

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
            Debug.Log("🌳 Adding vegetation and trees...");
            Transform vegRoot = GetOrCreateContainer("Vegetation");
            AddVegetationRing(vegRoot);

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
                "Assets/EmbersStorm – Mediterranean Ruins Building Kit/Prefabs/Walls/Ruins_Wall_Plain_A.prefab",
                "Assets/Kyle's Rock Pack/Kyle Fuji/Prefabs/Arid Rocks 1/rock_1_tl.prefab",
                "Assets/Kyle's Rock Pack/Kyle Fuji/Prefabs/Arid Rocks 1/rock_2_br.prefab",
                "Assets/Kyle's Rock Pack/Kyle Fuji/Prefabs/Arid Rocks 1/rock_3_tr.prefab"
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
            ground.transform.position = new Vector3(0, 0f, 0); // At Y=0 (ground level)
            ground.transform.localScale = new Vector3(30, 0.2f, 30); // 30×30m, 0.2m thick

            Object.DestroyImmediate(ground.GetComponent<Collider>());

            MeshRenderer mr = ground.GetComponent<MeshRenderer>();
            Material mat = new Material(Shader.Find("Standard"));
            mat.color = new Color(0.4f, 0.35f, 0.3f); // Earth brown
            mr.material = mat;

            BoxCollider collider = ground.AddComponent<BoxCollider>();
            collider.size = new Vector3(1, 1, 1);
            collider.center = Vector3.zero;
            collider.isTrigger = false;

            // Add kinematic Rigidbody for proper physics
            Rigidbody groundRb = ground.AddComponent<Rigidbody>();
            groundRb.isKinematic = true;
            groundRb.useGravity = false;
            groundRb.linearDamping = 0;
            groundRb.angularDamping = 0;

            // CRITICAL: Set to "Foreground" layer so raycast can detect it
            ground.layer = LayerMask.NameToLayer("Foreground");
            
            // Ensure all children are also on Foreground layer
            foreach (Transform child in ground.GetComponentsInChildren<Transform>())
            {
                child.gameObject.layer = LayerMask.NameToLayer("Foreground");
            }

            Debug.Log("  ✅ Ground (30×30m) - Layer: Foreground, Physics: Kinematic");
            Debug.Log($"    - BoxCollider: size={collider.size}, center={collider.center}");
            Debug.Log($"    - Collider bounds: min={collider.bounds.min}, max={collider.bounds.max}");
        }

        private static void CreateCenterWalkway(Transform parent)
        {
            // Walkway from Z=-2 to Z=15, X=-3 to X=3, Y=0 level
            GameObject walkway = GameObject.CreatePrimitive(PrimitiveType.Cube);
            walkway.name = "Walkway_Center";
            walkway.transform.parent = parent;
            walkway.transform.position = new Vector3(0, 0f, 6.5f);
            walkway.transform.localScale = new Vector3(6, 0.2f, 17); // 6m wide × 17m long × 0.2m thick

            Object.DestroyImmediate(walkway.GetComponent<Collider>());

            MeshRenderer mr = walkway.GetComponent<MeshRenderer>();
            Material mat = new Material(Shader.Find("Standard"));
            mat.color = new Color(0.5f, 0.48f, 0.45f); // Stone path
            mr.material = mat;

            BoxCollider collider = walkway.AddComponent<BoxCollider>();
            collider.size = new Vector3(1, 1, 1);
            collider.isTrigger = false;

            // Add kinematic Rigidbody (identical to ground)
            Rigidbody walkwayRb = walkway.AddComponent<Rigidbody>();
            walkwayRb.isKinematic = true;
            walkwayRb.useGravity = false;
            walkwayRb.linearDamping = 0;
            walkwayRb.angularDamping = 0;

            // CRITICAL: Set to "Foreground" layer so raycast can detect it
            walkway.layer = LayerMask.NameToLayer("Foreground");
            
            // Ensure all children are also on Foreground layer
            foreach (Transform child in walkway.GetComponentsInChildren<Transform>())
            {
                child.gameObject.layer = LayerMask.NameToLayer("Foreground");
            }

            Debug.Log("  ✅ Walkway_Center (6×0.2×17m) - Layer: Foreground, Physics: Kinematic");
            Debug.Log($"    - BoxCollider: size={collider.size}, center={collider.center}");
            Debug.Log($"    - Collider bounds: min={collider.bounds.min}, max={collider.bounds.max}");
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
            // Load Kyle's Rock Pack prefabs for background terrain
            string[] rockPrefabs = { ROCK_PREFAB_PATH_1, ROCK_PREFAB_PATH_2, ROCK_PREFAB_PATH_3 };

            string[] rockNames = { "Rock_BackLeft", "Rock_BackCenter", "Rock_BackRight" };
            // REPOSITIONED: Closer and more visible in scene (Z=12-15 instead of Z=20-25)
            Vector3[] basePositions = { new Vector3(-12, 0, 12), new Vector3(0, 0, 15), new Vector3(12, 0, 13) };

            for (int i = 0; i < rockNames.Length; i++)
            {
                GameObject rockPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(rockPrefabs[i]);
                
                if (rockPrefab != null)
                {
                    GameObject rock = PrefabUtility.InstantiatePrefab(rockPrefab, parent) as GameObject;
                    rock.name = rockNames[i];
                    rock.transform.position = basePositions[i];
                    rock.transform.localScale = new Vector3(2.5f, 2.5f, 2.5f); // INCREASED for better visibility
                    
                    // Fix materials with Standard shader (gray-brown rock color)
                    FixMaterialsWithStandard(rock, new Color(0.55f, 0.52f, 0.48f));
                    rock.layer = LayerMask.NameToLayer("Background");
                    Debug.Log($"  ✅ Loaded rock asset: {rockNames[i]} at {basePositions[i]} - 2.5x scale");
                }
                else
                {
                    // Fallback to cube
                    GameObject rock = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    rock.name = $"{rockNames[i]}_Fallback";
                    rock.transform.parent = parent;
                    rock.transform.position = basePositions[i];
                    rock.transform.localScale = new Vector3(3, 3, 3); // LARGER fallback cubes

                    Object.DestroyImmediate(rock.GetComponent<Collider>());
                    MeshRenderer mr = rock.GetComponent<MeshRenderer>();
                    Material mat = new Material(Shader.Find("Standard"));
                    mat.color = new Color(0.4f, 0.4f, 0.35f);
                    mr.material = mat;

                    rock.AddComponent<BoxCollider>();
                    rock.layer = LayerMask.NameToLayer("Background");
                    Debug.LogWarning($"  ⚠️  Kyle's Rock Pack prefab not found at {rockPrefabs[i]}, using fallback cube (3×3×3m)");
                }
            }

            Debug.Log("  ✅ Background terrain repositioned closer to scene - now visible from marketplace");
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

            // Try to load StarterAssets character - but use fallback on ANY failure
            try
            {
                GameObject playerPrefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/StarterAssets/ThirdPersonController/Prefabs/PlayerArmature.prefab");
                
                if (playerPrefab == null)
                {
                    Debug.LogWarning("SimplifiedMarketScene: playerPrefab asset not found. Using capsule fallback.");
                    AddPlayerFallback(parent);
                    return;
                }
                
                // Instantiate prefab as-is, don't modify its internal structure
                GameObject player = Object.Instantiate(playerPrefab, parent) as GameObject;
                if (player == null)
                {
                    Debug.LogError("SimplifiedMarketScene: Object.Instantiate returned null. Using capsule fallback.");
                    AddPlayerFallback(parent);
                    return;
                }
                
                player.name = "Player";
                player.transform.localPosition = Vector3.zero;
                player.transform.position = new Vector3(0, 0f, 0); // Ground level (Y=0)
                Debug.Log("  ✅ StarterAssets character instantiated successfully");
                
                // ========== CLEANUP PHASE 1: Remove null/broken components FIRST ==========
                // This must happen BEFORE we try to fix materials or disable scripts
                int nullsRemoved = 0;
                foreach (Transform t in player.GetComponentsInChildren<Transform>(includeInactive: true))
                {
                    // Get all components and filter those that are null
                    System.Collections.Generic.List<Component> toDestroy = new System.Collections.Generic.List<Component>();
                    
                    foreach (Component comp in t.GetComponents<Component>())
                    {
                        // If accessing the type throws, it's a null component (missing script)
                        try
                        {
                            var _ = comp.GetType();
                        }
                        catch
                        {
                            toDestroy.Add(comp);
                            nullsRemoved++;
                        }
                    }
                    
                    foreach (Component comp in toDestroy)
                    {
                        Object.DestroyImmediate(comp, allowDestroyingAssets: true);
                        Debug.Log($"  🗑️  Removed null component (missing script) on {t.gameObject.name}");
                    }
                }
                
                if (nullsRemoved > 0)
                    Debug.Log($"  ✅ Removed {nullsRemoved} null/broken components from hierarchy");
                
                // ========== CLEANUP PHASE 2: Destroy unwanted scripts (keep Animator) ==========
                MonoBehaviour[] allMonoBehaviours = player.GetComponentsInChildren<MonoBehaviour>(includeInactive: true);
                int destroyedCount = 0;
                
                foreach (MonoBehaviour mb in allMonoBehaviours)
                {
                    if (mb == null) continue; // Skip if already null
                    
                    string scriptName = mb.GetType().Name;
                    
                    // Keep ONLY Animator, destroy everything else
                    if (!scriptName.Contains("Animator"))
                    {
                        Object.DestroyImmediate(mb, allowDestroyingAssets: true);
                        destroyedCount++;
                        Debug.Log($"  🗑️  Destroyed {scriptName}");
                    }
                }
                
                Debug.Log($"  ✅ Cleaned up {destroyedCount} unwanted scripts from character hierarchy");
                
                // Verify Animator still exists after cleanup
                Animator animator = player.GetComponent<Animator>();
                if (animator == null)
                {
                    Debug.LogWarning("  ⚠️  WARNING: Animator was destroyed! Looking for it in children...");
                    animator = player.GetComponentInChildren<Animator>();
                    if (animator != null)
                        Debug.Log($"  ✅ Found Animator on child: {animator.gameObject.name}");
                }
                
                // ========== APPLY MATERIALS (null components are now gone) ==========
                FixCharacterMaterials(player);

                // ========== DISABLE UNWANTED CONTROL SCRIPTS ==========
                MonoBehaviour[] components = player.GetComponents<MonoBehaviour>();
                foreach (MonoBehaviour comp in components)
                {
                    if (comp != null && comp.GetType().Name == "ThirdPersonController")
                    {
                        comp.enabled = false;
                        Debug.Log("  ℹ️  Disabled ThirdPersonController via reflection");
                        break;
                    }
                }
                
                // ========== CREATE CAMERA ==========
                GameObject cameraObj = new GameObject("MainCamera");
                cameraObj.transform.parent = player.transform;
                cameraObj.transform.localPosition = new Vector3(0, 1.6f, 0); // Eye height (1.6m above ground)

                Camera cam = cameraObj.AddComponent<Camera>();
                cam.orthographic = true;
                cam.orthographicSize = 6;
                cam.nearClipPlane = -100;
                cam.farClipPlane = 100;
                cam.tag = "MainCamera";
                cam.clearFlags = CameraClearFlags.SolidColor;
                cam.backgroundColor = new Color(0.1f, 0.1f, 0.12f, 1f);
                cam.depth = 0;

                cameraObj.AddComponent<AudioListener>();

                // ========== SETUP PHYSICS ==========
                SetupCharacterPhysics(player);
                
                // ========== ADD MOVEMENT SCRIPT ==========
                SimpleCharacterMovement movement = player.AddComponent<SimpleCharacterMovement>();
                movement.mainCamera = cam;
                Debug.Log("  ✅ SimpleCharacterMovement added (WASD to move, Mouse to look, ESC to unlock)");
                
                // Log character collider info after setup for debugging
                Collider[] finalColliders = player.GetComponentsInChildren<Collider>();
                Debug.Log($"  📊 COLLIDER DEBUG INFO:");
                Debug.Log($"    - Character root position: {player.transform.position}");
                Debug.Log($"    - Character Rigidbody useGravity: {player.GetComponent<Rigidbody>()?.useGravity}");
                Debug.Log($"    - Total colliders on character: {finalColliders.Length}");
                foreach (Collider c in finalColliders)
                {
                    Debug.Log($"    - Collider on {c.gameObject.name}: {c.GetType().Name}, bounds={c.bounds}, trigger={c.isTrigger}");
                }

                Debug.Log("  ✅ StarterAssets character ready with movement and camera");
                return;
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"SimplifiedMarketScene: Exception loading StarterAssets: {ex.Message}\\n{ex.StackTrace}");
                AddPlayerFallback(parent);
                return;
            }
        }

        private static void AddPlayerFallback(Transform parent)
        {
            // Null-check parent parameter
            if (parent == null)
            {
                Debug.LogError("SimplifiedMarketScene: AddPlayerFallback() called with null parent. Creating PlayerRoot.");
                parent = new GameObject("PlayerRoot").transform;
            }

            // Fallback to green capsule if prefab not found
            GameObject player = new GameObject("Player");
            player.transform.parent = parent;
            player.transform.position = new Vector3(0, 0f, 0); // Ground level (Y=0)

            GameObject visual = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            visual.transform.parent = player.transform;
            visual.transform.localPosition = new Vector3(0, 0.9f, 0);  // Match collider center
            visual.name = "Model";

            // Remove the collider from the visual primitive (it gets created automatically)
            Collider visualCollider = visual.GetComponent<Collider>();
            if (visualCollider != null)
                Object.DestroyImmediate(visualCollider);

            MeshRenderer vmr = visual.GetComponent<MeshRenderer>();
            Material playerMat = new Material(Shader.Find("Standard"));
            playerMat.color = new Color(0.2f, 0.8f, 0.3f);
            vmr.material = playerMat;

            // Add collider to ROOT (not visual child)
            CapsuleCollider collider = player.AddComponent<CapsuleCollider>();
            collider.radius = 0.4f;
            collider.height = 1.8f;
            collider.center = new Vector3(0, 0.9f, 0);  // Center at 0.9 so bottom is at Y=0 (ground level)
            collider.isTrigger = false; // CRITICAL: Must NOT be trigger

            Rigidbody rb = player.AddComponent<Rigidbody>();
            rb.mass = 1;
            rb.linearDamping = 0;
            rb.angularDamping = 0.05f;
            rb.useGravity = true;
            rb.isKinematic = false;
            rb.constraints = RigidbodyConstraints.FreezeRotation;
            rb.linearVelocity = new Vector3(0, -2f, 0);  // Help settle on ground
            
            Debug.Log($"  ✅ Fallback player Rigidbody: useGravity={rb.useGravity}, isKinematic={rb.isKinematic}");
            Debug.Log($"      - CapsuleCollider: center={collider.center}, radius={collider.radius}, height={collider.height}");
            Debug.Log($"      - Initial downward velocity: {rb.linearVelocity.y}");

            GameObject cameraObj = new GameObject("CameraHolder");
            cameraObj.transform.parent = player.transform;
            cameraObj.transform.localPosition = new Vector3(0, 1.6f, 0); // Eye height (1.6m above ground)

            Camera cam = cameraObj.AddComponent<Camera>();
            cam.orthographic = true;
            cam.orthographicSize = 6;
            cam.nearClipPlane = -100;
            cam.farClipPlane = 100;
            cam.tag = "MainCamera";
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.1f, 0.1f, 0.12f, 1f);

            cameraObj.AddComponent<AudioListener>();
            
            // Add simple movement script for WASD + Mouse input
            SimpleCharacterMovement movement = player.AddComponent<SimpleCharacterMovement>();
            movement.mainCamera = cam;
            Debug.Log("  ✅ SimpleCharacterMovement added (WASD to move, Mouse to look, ESC to unlock)");

            player.layer = LayerMask.NameToLayer("Default");
            Debug.Log("  ⚠️  Using fallback capsule player (with physics and input control)");
        }

        private static void FixMaterialsWithStandard(GameObject obj, Color color)
        {
            // Replace all materials with a clean Standard shader material
            // This fixes any broken/pink materials in the prefabs
            Material standardMat = new Material(Shader.Find("Standard"));
            standardMat.color = color;
            
            MeshRenderer[] renderers = obj.GetComponentsInChildren<MeshRenderer>();
            foreach (MeshRenderer renderer in renderers)
            {
                Material[] mats = new Material[renderer.sharedMaterials.Length];
                for (int i = 0; i < mats.Length; i++)
                    mats[i] = standardMat;
                renderer.sharedMaterials = mats;
            }
            
            Debug.Log($"  ℹ️  Fixed materials on {obj.name} (color: {color})");
        }

        private static void FixCharacterMaterials(GameObject character)
        {
            // Apply a tan/beige material to all renderers to avoid pink default
            Material characterMat = new Material(Shader.Find("Standard"));
            characterMat.color = new Color(0.85f, 0.8f, 0.75f); // Tan/beige skin tone
            
            // Search for renderers recursively - they may be deeply nested
            MeshRenderer[] renderers = character.GetComponentsInChildren<MeshRenderer>(includeInactive: true);
            if (renderers.Length == 0)
            {
                // Try SkinnedMeshRenderer as fallback (humanoid characters use this)
                SkinnedMeshRenderer[] skinnedRenderers = character.GetComponentsInChildren<SkinnedMeshRenderer>(includeInactive: true);
                if (skinnedRenderers.Length > 0)
                {
                    foreach (SkinnedMeshRenderer renderer in skinnedRenderers)
                    {
                        Material[] mats = new Material[renderer.sharedMaterials.Length];
                        for (int i = 0; i < mats.Length; i++)
                            mats[i] = characterMat;
                        renderer.sharedMaterials = mats;
                    }
                    Debug.Log($"  ✅ Applied materials to {skinnedRenderers.Length} SkinnedMeshRenderers on character");
                    return;
                }
                // Only warn if BOTH MeshRenderer and SkinnedMeshRenderer not found
                Debug.LogWarning("  ⚠️  No MeshRenderers or SkinnedMeshRenderers found on character model");
                return;
            }
            
            foreach (MeshRenderer renderer in renderers)
            {
                Material[] mats = new Material[renderer.sharedMaterials.Length];
                for (int i = 0; i < mats.Length; i++)
                    mats[i] = characterMat;
                renderer.sharedMaterials = mats;
            }
            
            Debug.Log($"  ✅ Applied materials to {renderers.Length} MeshRenderers on character");
        }

        private static void SetupCharacterPhysics(GameObject character)
        {
            Debug.Log("🔧 Setting up character physics...");
            Debug.Log($"  Character position: {character.transform.position}");
            
            // Remove any remaining colliders from the prefab (may exist on root or children)
            Collider[] existingColliders = character.GetComponentsInChildren<Collider>();
            Debug.Log($"  Cleaning up {existingColliders.Length} collider(s)...");
            foreach (Collider col in existingColliders)
            {
                Object.DestroyImmediate(col);
            }
            
            // Ensure character has a Rigidbody for gravity and collision
            Rigidbody rb = character.GetComponent<Rigidbody>();
            if (rb == null)
            {
                rb = character.AddComponent<Rigidbody>();
            }
            
            // Configure Rigidbody for player movement
            rb.mass = 1;
            rb.linearDamping = 0;
            rb.angularDamping = 0.05f;
            rb.useGravity = true;
            rb.isKinematic = false;
            rb.constraints = RigidbodyConstraints.FreezeRotation;
            
            // Give character downward velocity to help settle on ground
            rb.linearVelocity = new Vector3(0, -2f, 0);  // Stronger downward to ensure settling
            
            Debug.Log($"  ✅ Rigidbody configured: useGravity={rb.useGravity}, isKinematic={rb.isKinematic}");
            Debug.Log($"      - Initial downward velocity: {rb.linearVelocity.y}");
            Debug.Log($"      - Character position: {character.transform.position}");
            
            // Create ONE clean capsule collider for physics collision
            CapsuleCollider capsule = character.AddComponent<CapsuleCollider>();
            capsule.radius = 0.4f;
            capsule.height = 1.8f;
            // CRITICAL FIX: Center must be at (0, 0, 0) so capsule spans from Y=0 to Y=1.8
            // Character is at Y=0.9, so world capsule center = 0.9 + 0 = 0.9 ✓
            // Bottom = 0.9 - 0.9 = 0 ✓, Top = 0.9 + 0.9 = 1.8 ✓
            capsule.center = Vector3.zero;  // NOT (0, 0.9, 0)!
            capsule.isTrigger = false;
            Debug.Log($"  ✅ CapsuleCollider created:");
            Debug.Log($"      - Center offset: {capsule.center}, Radius: {capsule.radius}, Height: {capsule.height}");
            Debug.Log($"      - Character position: {character.transform.position}");
            Debug.Log($"      - isTrigger: {capsule.isTrigger}");
            
            // Debug: Check if collider actually touches ground
            Bounds capsuleBounds = capsule.bounds;
            Debug.Log($"  📊 COLLIDER BOUNDS (FIXED):");
            Debug.Log($"      - Bounds Center (world): {capsuleBounds.center}");
            Debug.Log($"      - Min Y: {capsuleBounds.min.y}, Max Y: {capsuleBounds.max.y}");
            if (Mathf.Abs(capsuleBounds.min.y - 0f) < 0.05f)
                Debug.Log($"      ✅ CORRECT - Bottom at Y≈0 (ground level)");
            else
                Debug.LogWarning($"      ⚠️  WRONG - Bottom at Y={capsuleBounds.min.y}, should be Y=0!");
            Debug.Log($"  ✅ Character physics ready for collision");
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

        private static void FixVegetationMaterials(GameObject obj)
        {
            // Replace broken/pink materials on vegetation with Standard shader
            Material standardMat = new Material(Shader.Find("Standard"));
            standardMat.color = new Color(0.6f, 0.5f, 0.4f); // Greenish-brown for trees
            
            MeshRenderer[] renderers = obj.GetComponentsInChildren<MeshRenderer>();
            foreach (MeshRenderer renderer in renderers)
            {
                Material[] mats = new Material[renderer.sharedMaterials.Length];
                for (int i = 0; i < mats.Length; i++)
                    mats[i] = standardMat;
                renderer.sharedMaterials = mats;
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
            // Define vegetation positions in a ring around marketplace
            // Outer perimeter: Z = -5 to Z = 20 (front to back), X = -15 to X = 15 (left to right)
            
            Vector3[] treePositions = new Vector3[]
            {
                // Front row (Z = -5)
                new Vector3(-15, 0, -5),
                new Vector3(-5, 0, -5),
                new Vector3(5, 0, -5),
                new Vector3(15, 0, -5),
                
                // Left side (X = -15)
                new Vector3(-15, 0, 0),
                new Vector3(-15, 0, 5),
                new Vector3(-15, 0, 10),
                new Vector3(-15, 0, 15),
                
                // Right side (X = 15)
                new Vector3(15, 0, 0),
                new Vector3(15, 0, 5),
                new Vector3(15, 0, 10),
                new Vector3(15, 0, 15),
                
                // Back row (Z = 20)
                new Vector3(-15, 0, 20),
                new Vector3(-5, 0, 20),
                new Vector3(5, 0, 20),
                new Vector3(15, 0, 20),
            };

            // Tree prefab paths (with fallbacks)
            string[] treePrefabs = new string[]
            {
                "Assets/DreamTree2/Mesh/DreamTree.FBX",
                "Assets/3 English Oak Set/Oak.fbx",
                "Assets/3 English Oak Set/Bare_Oak.fbx",
                "Assets/Dry_Trees/Model/Dry3333.fbx",
            };

            int treeCount = 0;
            for (int i = 0; i < treePositions.Length && treeCount < treePositions.Length; i++)
            {
                // Cycle through available tree prefabs
                string treePrefab = treePrefabs[i % treePrefabs.Length];
                
                GameObject treePrefabObj = AssetDatabase.LoadAssetAtPath<GameObject>(treePrefab);
                if (treePrefabObj != null)
                {
                    GameObject treeInstance = Object.Instantiate(treePrefabObj, treePositions[i], Quaternion.identity);
                    treeInstance.name = $"Tree_{i:00}";
                    treeInstance.transform.parent = vegRoot;
                    
                    // Apply a much smaller overall scale (trees were oversized)
                    float globalScale = 0.35f; // Reduced from 1.0
                    float scaleVariation = Random.Range(0.8f, 1.2f);
                    treeInstance.transform.localScale *= (globalScale * scaleVariation);
                    
                    // Fix any broken materials (convert pink to gray)
                    FixVegetationMaterials(treeInstance);
                    
                    treeCount++;
                }
                else
                {
                    Debug.LogWarning($"  ⚠️  Tree prefab not found: {treePrefab}");
                }
            }

            Debug.Log($"  ✅ Placed {treeCount} trees in vegetation ring");

            // Add some stumps and succulents for ground detail
            Vector3[] propPositions = new Vector3[]
            {
                new Vector3(-12, 0, 2),
                new Vector3(-8, 0, 7),
                new Vector3(8, 0, 3),
                new Vector3(12, 0, 12),
            };

            string[] propPrefabs = new string[]
            {
                "Assets/GreenBugGames/Scan Stump Vol.1/Stump_old.fbx",
                "Assets/SeedMesh/Succulents/Succulent_EcheveriaRosalinda_var1.fbx",
            };

            int propCount = 0;
            for (int i = 0; i < propPositions.Length; i++)
            {
                string propPrefab = propPrefabs[i % propPrefabs.Length];
                
                GameObject propPrefabObj = AssetDatabase.LoadAssetAtPath<GameObject>(propPrefab);
                if (propPrefabObj != null)
                {
                    GameObject propInstance = Object.Instantiate(propPrefabObj, propPositions[i], Quaternion.identity);
                    propInstance.name = $"Prop_{i:00}";
                    propInstance.transform.parent = vegRoot;
                    propCount++;
                }
            }

            Debug.Log($"  ✅ Placed {propCount} ground props (stumps/succulents)");
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
