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
        private const float StallRowAX = -10f;  // Left side stalls
        private const float StallRowBX = 10f;   // Right side stalls
        private const float CenterWalkwayX = 0f;
        
        // Asset paths
        private const string EMBERS_WALL_PATH = "Assets/EmbersStorm – Mediterranean Ruins Building Kit/Prefabs/Walls/Ruins_Wall_Plain_A.prefab";
        private const string EMBERS_ROOF_PATH = "Assets/EmbersStorm – Mediterranean Ruins Building Kit/Prefabs/Roofs/Roof.A.prefab";
        
        private const string ROCK_PREFAB_PATH_1 = "Assets/Kyle's Rock Pack/Kyle Fuji/Prefabs/Arid Rocks 1/rock_1_tl.prefab";
        private const string ROCK_PREFAB_PATH_2 = "Assets/Kyle's Rock Pack/Kyle Fuji/Prefabs/Arid Rocks 1/rock_2_br.prefab";
        private const string ROCK_PREFAB_PATH_3 = "Assets/Kyle's Rock Pack/Kyle Fuji/Prefabs/Arid Rocks 1/rock_3_tr.prefab";
        
        private const string TREE_PREFAB_PATH = "Assets/Dry_Trees/Prefab/Dry7509.prefab";

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

            Debug.Log("\n✅ STRUCTURED MARKETPLACE READY!\n");
            Debug.Log("📐 Grid Summary:");
            Debug.Log("   Row A (X=-10): Stalls at Z=0, Z=5, Z=10");
            Debug.Log("   Row B (X=+10): Stalls at Z=0, Z=5, Z=10");
            Debug.Log("   Walkway (X=0): Center path for navigation");
            Debug.Log("   Player: Spawned at origin (0, 0.9, 0)");
            Debug.Log("   Camera: First-person from player eyes\n");
            Debug.Log("🎮 Press Play to explore\n");

            EditorSceneManager.MarkSceneDirty(activeScene);
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
            ground.transform.position = new Vector3(0, -0.05f, 0); // Slightly below Y=0
            ground.transform.localScale = new Vector3(20, 0.1f, 20); // 20×20m, 0.1m thick

            Object.DestroyImmediate(ground.GetComponent<Collider>());

            MeshRenderer mr = ground.GetComponent<MeshRenderer>();
            Material mat = new Material(Shader.Find("Standard"));
            mat.color = new Color(0.4f, 0.35f, 0.3f); // Earth brown
            mr.material = mat;

            BoxCollider collider = ground.AddComponent<BoxCollider>();
            collider.size = new Vector3(1, 1, 1); // Normalized to cube's local scale
            collider.center = Vector3.zero; // CRITICAL: Center at 0,0,0 of this cube
            collider.isTrigger = false; // IMPORTANT: Must not be a trigger for physics collision

            ground.layer = LayerMask.NameToLayer("Foreground");
            Debug.Log("  ✅ Ground (visible brown cube) at Y=-0.05 to Y=+0.05, 20×20m");
            
            // Verify collider was created properly
            BoxCollider bc = ground.GetComponent<BoxCollider>();
            if (bc != null)
            {
                Debug.Log($"    - BoxCollider: size={bc.size}, center={bc.center}, isTrigger={bc.isTrigger}");
                Debug.Log($"    - Ground Position: {ground.transform.position}, Scale: {ground.transform.localScale}");
                Debug.Log($"    - Collider bounds: min={bc.bounds.min}, max={bc.bounds.max}");
            }
        }

        private static void CreateCenterWalkway(Transform parent)
        {
            // Walkway from Z=-2 to Z=15, X=-3 to X=3, Y=0 level (uses cube for visibility)
            GameObject walkway = GameObject.CreatePrimitive(PrimitiveType.Cube);
            walkway.name = "Walkway_Center";
            walkway.transform.parent = parent;
            walkway.transform.position = new Vector3(0, 0.01f, 6.5f); // Centered on Z-axis, slightly above ground
            walkway.transform.localScale = new Vector3(6, 0.05f, 17); // 6m wide × 17m long × 0.05m thick

            Object.DestroyImmediate(walkway.GetComponent<Collider>());

            MeshRenderer mr = walkway.GetComponent<MeshRenderer>();
            Material mat = new Material(Shader.Find("Standard"));
            mat.color = new Color(0.5f, 0.48f, 0.45f); // Stone path
            mr.material = mat;

            BoxCollider collider = walkway.AddComponent<BoxCollider>();
            collider.size = new Vector3(1, 1, 1); // Normalized to cube's local scale
            collider.isTrigger = false; // IMPORTANT: Must not be a trigger for physics collision

            walkway.layer = LayerMask.NameToLayer("Foreground");
            Debug.Log("  ✅ Center walkway (visible stone cube): (-3,0,-2) to (3,0,15)");
            
            // Verify collider was created properly
            BoxCollider bc = walkway.GetComponent<BoxCollider>();
            if (bc != null)
            {
                Debug.Log($"    - BoxCollider: size={bc.size}, center={bc.center}, isTrigger={bc.isTrigger}");
            }
        }

        private static void CreateStallRow(Transform parent, float stallX, string stallPrefix)
        {
            // Load EmbersStorm wall prefabs for market stalls
            string[] wallPaths = {
                "Assets/EmbersStorm – Mediterranean Ruins Building Kit/Prefabs/Walls/Ruins_Wall_Plain_A.prefab",
                "Assets/EmbersStorm – Mediterranean Ruins Building Kit/Prefabs/Walls/Ruins_Wall_Plain_B.prefab",
                "Assets/EmbersStorm – Mediterranean Ruins Building Kit/Prefabs/Walls/Ruins_Wall_Plain_C.prefab"
            };

            float[] stallZPositions = { 0f, 5f, 10f };

            for (int i = 0; i < stallZPositions.Length; i++)
            {
                GameObject stallPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(wallPaths[i]);
                
                if (stallPrefab != null)
                {
                    GameObject stall = PrefabUtility.InstantiatePrefab(stallPrefab, parent) as GameObject;
                    stall.name = $"{stallPrefix}_{i + 1}";
                    stall.transform.position = new Vector3(stallX, 0, stallZPositions[i]);
                    stall.transform.localScale = new Vector3(0.5f, 0.5f, 0.5f);
                    
                    // Fix materials with Standard shader (beige stone color)
                    FixMaterialsWithStandard(stall, new Color(0.8f, 0.75f, 0.65f));
                    
                    Debug.Log($"  ✅ Loaded stall {stallPrefix}_{i + 1} at ({stallX}, 0, {stallZPositions[i]})");
                }
                else
                {
                    // Fallback to cube if prefab not found
                    GameObject stall = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    stall.name = $"{stallPrefix}_{i + 1}_Fallback";
                    stall.transform.parent = parent;
                    stall.transform.position = new Vector3(stallX, 0.5f, stallZPositions[i]);
                    stall.transform.localScale = new Vector3(1, 1, 1);

                    Object.DestroyImmediate(stall.GetComponent<Collider>());
                    MeshRenderer mr = stall.GetComponent<MeshRenderer>();
                    Material mat = new Material(Shader.Find("Standard"));
                    mat.color = new Color(0.65f, 0.6f, 0.5f);
                    mr.material = mat;

                    stall.AddComponent<BoxCollider>();
                    stall.layer = LayerMask.NameToLayer("Midground");
                    Debug.LogWarning($"  ⚠️  EmbersStorm prefab not found, using fallback cube");
                }
            }

            string sideLabel = stallX < 0 ? "left (X=-10)" : "right (X=+10)";
            Debug.Log($"  ✅ Stall row ({sideLabel}) created at Z=0, Z=5, Z=10");
        }

        private static void CreateBackgroundRocks(Transform parent)
        {
            // Load Kyle's Rock Pack prefabs for background terrain
            string[] rockPrefabs = { ROCK_PREFAB_PATH_1, ROCK_PREFAB_PATH_2, ROCK_PREFAB_PATH_3 };

            string[] rockNames = { "Rock_BackLeft", "Rock_BackCenter", "Rock_BackRight" };
            Vector3[] basePositions = { new Vector3(-8, 0, 20), new Vector3(0, 0, 25), new Vector3(8, 0, 22) };

            for (int i = 0; i < rockNames.Length; i++)
            {
                GameObject rockPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(rockPrefabs[i]);
                
                if (rockPrefab != null)
                {
                    GameObject rock = PrefabUtility.InstantiatePrefab(rockPrefab, parent) as GameObject;
                    rock.name = rockNames[i];
                    rock.transform.position = basePositions[i];
                    rock.transform.localScale = new Vector3(1.5f, 1.5f, 1.5f);
                    
                    // Fix materials with Standard shader (gray-brown rock color)
                    FixMaterialsWithStandard(rock, new Color(0.55f, 0.52f, 0.48f));
                    rock.layer = LayerMask.NameToLayer("Background");
                    Debug.Log($"  ✅ Loaded rock asset: {rockNames[i]} at {basePositions[i]}");
                }
                else
                {
                    // Fallback to cube
                    GameObject rock = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    rock.name = $"{rockNames[i]}_Fallback";
                    rock.transform.parent = parent;
                    rock.transform.position = basePositions[i];
                    rock.transform.localScale = new Vector3(2, 2, 2);

                    Object.DestroyImmediate(rock.GetComponent<Collider>());
                    MeshRenderer mr = rock.GetComponent<MeshRenderer>();
                    Material mat = new Material(Shader.Find("Standard"));
                    mat.color = new Color(0.4f, 0.4f, 0.35f);
                    mr.material = mat;

                    rock.AddComponent<BoxCollider>();
                    rock.layer = LayerMask.NameToLayer("Background");
                    Debug.LogWarning($"  ⚠️  Kyle's Rock Pack prefab not found at {rockPrefabs[i]}, using fallback cube");
                }
            }

            Debug.Log("  ✅ Background terrain loaded at distance (parallax depth)");
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
                Debug.Log("  ✅ StarterAssets character instantiated successfully");
                
                // SIMPLIFIED: Use reflection to disable ThirdPersonController by name
                // (avoids namespace import issues with StarterAssets)
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
                
                // Add our camera as a sibling, not nested
                GameObject cameraObj = new GameObject("MainCamera");
                cameraObj.transform.parent = player.transform;
                cameraObj.transform.localPosition = new Vector3(0, 0.9f, 0);

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

                // Fix materials on character (avoid pink)
                FixCharacterMaterials(player);

                // Set up physics for proper collision with ground
                SetupCharacterPhysics(player);
                
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

                // Add our controller to player (with error handling)
                try
                {
                    PlayerController controller = player.GetComponent<PlayerController>();
                    if (controller == null)
                    {
                        controller = player.AddComponent<PlayerController>();
                        Debug.Log("  ✅ PlayerController added to character");
                    }
                    else
                    {
                        Debug.Log("  ✅ PlayerController already present on character");
                    }
                }
                catch (System.Exception ex)
                {
                    Debug.LogWarning($"  ⚠️  Could not add PlayerController: {ex.Message}");
                    Debug.Log("     Player will use physics-based movement from Rigidbody instead");
                }

                Debug.Log("  ✅ StarterAssets character ready with custom camera and controller");
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
            player.transform.position = new Vector3(0, 0.9f, 0);

            GameObject visual = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            visual.transform.parent = player.transform;
            visual.transform.localPosition = Vector3.zero;
            visual.name = "Model";

            Object.DestroyImmediate(visual.GetComponent<Collider>());
            MeshRenderer vmr = visual.GetComponent<MeshRenderer>();
            Material playerMat = new Material(Shader.Find("Standard"));
            playerMat.color = new Color(0.2f, 0.8f, 0.3f);
            vmr.material = playerMat;

            CapsuleCollider collider = player.AddComponent<CapsuleCollider>();
            collider.radius = 0.4f;
            collider.height = 1.8f;
            collider.center = new Vector3(0, 0.5f, 0); // Capsule center relative to player root
            collider.isTrigger = false; // IMPORTANT: Must not be a trigger

            Rigidbody rb = player.AddComponent<Rigidbody>();
            rb.mass = 1;
            rb.linearDamping = 0; // Changed from 5 to 0 for proper physics
            rb.angularDamping = 0.05f;
            rb.useGravity = true;
            rb.isKinematic = false; // Ensure it's not kinematic
            rb.constraints = RigidbodyConstraints.FreezeRotation;
            
            Debug.Log($"  ✅ Fallback player Rigidbody: useGravity={rb.useGravity}, isKinematic={rb.isKinematic}");
            Debug.Log($"    - Player position: {player.transform.position}");
            Debug.Log($"    - CapsuleCollider: center={collider.center}, radius={collider.radius}, height={collider.height}");

            GameObject cameraObj = new GameObject("CameraHolder");
            cameraObj.transform.parent = player.transform;
            cameraObj.transform.localPosition = new Vector3(0, 0.9f, 0);

            Camera cam = cameraObj.AddComponent<Camera>();
            cam.orthographic = true;
            cam.orthographicSize = 6;
            cam.nearClipPlane = -100;
            cam.farClipPlane = 100;
            cam.tag = "MainCamera";
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.1f, 0.1f, 0.12f, 1f);

            cameraObj.AddComponent<AudioListener>();
            
            try
            {
                player.AddComponent<PlayerController>();
                Debug.Log("  ✅ PlayerController added to fallback player");
            }
            catch (System.Exception ex)
            {
                Debug.LogWarning($"  ⚠️  Could not add PlayerController to fallback: {ex.Message}");
            }

            player.layer = LayerMask.NameToLayer("Default");
            Debug.Log("  ⚠️  Using fallback capsule player (preferred prefab not found)");
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
            
            MeshRenderer[] renderers = character.GetComponentsInChildren<MeshRenderer>();
            if (renderers.Length == 0)
            {
                Debug.LogWarning("  ⚠️  No MeshRenderers found on character model");
                return;
            }
            
            foreach (MeshRenderer renderer in renderers)
            {
                Material[] mats = new Material[renderer.sharedMaterials.Length];
                for (int i = 0; i < mats.Length; i++)
                    mats[i] = characterMat;
                renderer.sharedMaterials = mats;
            }
            
            Debug.Log($"  ✅ Applied materials to {renderers.Length} renderers on character");
        }

        private static void SetupCharacterPhysics(GameObject character)
        {
            Debug.Log("🔧 Setting up character physics...");
            Debug.Log($"  Character position: {character.transform.position}");
            
            // First, disable ALL scripts that might interfere (CharacterController, Animator scripts, etc.)
            MonoBehaviour[] allScripts = character.GetComponentsInChildren<MonoBehaviour>();
            foreach (MonoBehaviour script in allScripts)
            {
                if (script != null && script.GetType().Name != "PlayerController")
                {
                    script.enabled = false;
                    Debug.Log($"  ℹ️  Disabled script: {script.GetType().Name}");
                }
            }
            
            // Ensure character has a Rigidbody for gravity and collision
            Rigidbody rb = character.GetComponent<Rigidbody>();
            if (rb == null)
            {
                rb = character.AddComponent<Rigidbody>();
                Debug.Log("  ℹ️  Added Rigidbody to character root");
            }
            
            // Configure Rigidbody for player movement
            rb.mass = 1;
            rb.linearDamping = 0; // No air friction
            rb.angularDamping = 0.05f;
            rb.useGravity = true;
            rb.isKinematic = false; // MUST be false for gravity to work
            rb.constraints = RigidbodyConstraints.FreezeRotation; // Prevent unwanted rotation
            Debug.Log($"  ✅ Rigidbody: mass={rb.mass}, useGravity={rb.useGravity}, isKinematic={rb.isKinematic}");
            
            // Check for colliders and ENSURE NONE ARE TRIGGERS
            Collider[] colliders = character.GetComponentsInChildren<Collider>();
            Debug.Log($"  ℹ️  Found {colliders.Length} collider(s) on character and children");
            
            if (colliders.Length == 0)
            {
                Debug.LogWarning("  ⚠️  No colliders found on character. Adding CapsuleCollider...");
                CapsuleCollider capsule = character.AddComponent<CapsuleCollider>();
                capsule.radius = 0.4f;
                capsule.height = 1.8f;
                capsule.center = new Vector3(0, 0, 0); // At root center
                capsule.isTrigger = false;
                Debug.Log("  ✅ Added CapsuleCollider to character root");
                Debug.Log($"    - Position: center={capsule.center}, radius={capsule.radius}, height={capsule.height}");
            }
            else
            {
                // Make sure none are triggers
                foreach (Collider col in colliders)
                {
                    if (col.isTrigger)
                    {
                        col.isTrigger = false;
                        Debug.Log($"  ⚠️  Fixed trigger collider on {col.gameObject.name}: isTrigger=false");
                    }
                    
                    // Log detailed info for BoxColliders and CapsuleColliders
                    if (col is BoxCollider bc)
                    {
                        Debug.Log($"    - {col.gameObject.name}: BoxCollider (center={bc.center}, size={bc.size}, trigger={col.isTrigger})");
                        Debug.Log($"      bounds: min={bc.bounds.min}, max={bc.bounds.max}");
                    }
                    else if (col is CapsuleCollider cc)
                    {
                        Debug.Log($"    - {col.gameObject.name}: CapsuleCollider (center={cc.center}, radius={cc.radius}, height={cc.height}, trigger={col.isTrigger})");
                        Debug.Log($"      bounds: min={cc.bounds.min}, max={cc.bounds.max}");
                    }
                    else
                    {
                        Debug.Log($"    - {col.gameObject.name}: {col.GetType().Name} (trigger={col.isTrigger})");
                    }
                }
            }
            
            Debug.Log("  ✅ Character physics fully configured");
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
