using UnityEditor;
using UnityEngine;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using Velinor.Core;

namespace Velinor.Editor
{
    /// <summary>
    /// PopulateMarketScene - Populate Marketplace with actual 3D models and player
    /// 
    /// This script populates the scene with:
    /// - Rocks and cliffs from Kyle's Rock Pack (Background layer)
    /// - Market stalls from Mediterranean Ruins Kit (Midground layer)
    /// - Ground props and debris (Foreground layer)
    /// - Player character with movement controller (Characters layer)
    /// </summary>
    public class PopulateMarketScene
    {
        [MenuItem("Velinor/Scene Setup/Populate with Real Assets")]
        public static void PopulateMarketWithAssets()
        {
            Debug.Log("\n🏗️  POPULATING MARKETPLACE SCENE WITH REAL ASSETS\n");

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

            // Step 1: Add background rocks and cliffs (distant, large)
            Debug.Log("📦 Adding background rocks...");
            AddBackgroundRocks(bgRoot);

            // Step 2: Add market stalls and buildings (midground)
            Debug.Log("🏛️  Adding market structures...");
            AddMarketStructures(mgRoot);

            // Step 3: Add foreground props (immediate area)
            Debug.Log("🪨 Adding foreground props...");
            AddForegroundProps(fgRoot);

            // Step 4: Add player character
            Debug.Log("👤 Adding player character...");
            AddPlayerCharacter(charRoot);

            Debug.Log("✅ MARKETPLACE SCENE POPULATED!\n");
            Debug.Log("🎮 Press Play to walk around in Velinor!\n");

            EditorSceneManager.MarkSceneDirty(activeScene);
        }

        private static Transform GetOrCreateContainer(string name)
        {
            Transform existing = Object.FindAnyObjectByType<Transform>();
            if (existing != null)
            {
                foreach (Transform child in existing.parent ?? existing.root)
                {
                    if (child.name == name)
                        return child;
                }
            }

            GameObject container = new GameObject(name);
            return container.transform;
        }

        private static void AddBackgroundRocks(Transform parent)
        {
            // Kyle's Rock Pack location
            string rocksPath = "Assets/Kyle's Rock Pack/Kyle Fuji/Prefabs/";
            
            // Load rock prefabs and place in background
            string[] rockPrefabs = new string[]
            {
                "boulder_1_tl.prefab",
                "boulder_2_tr.prefab",
                "boulder_3_br.prefab",
                "boulder_4_bl.prefab"
            };

            Vector3[] positions = new Vector3[]
            {
                new Vector3(-15, 5, 20),   // Left cliff
                new Vector3(15, 4, 22),   // Right cliff
                new Vector3(0, 8, 25),    // Center
                new Vector3(-8, 2, 23)    // Left cluster
            };

            float[] scales = new float[] { 2f, 2f, 2.5f, 1.8f };

            for (int i = 0; i < rockPrefabs.Length && i < positions.Length; i++)
            {
                string prefabPath = rocksPath + rockPrefabs[i];
                GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);

                if (prefab != null)
                {
                    GameObject instance = PrefabUtility.InstantiatePrefab(prefab, parent) as GameObject;
                    if (instance != null)
                    {
                        instance.name = rockPrefabs[i].Replace(".prefab", "");
                        instance.transform.position = positions[i];
                        instance.transform.localScale = Vector3.one * scales[i];
                        SetLayerRecursive(instance, LayerMask.NameToLayer("Background"));
                        Debug.Log($"  ✅ {rockPrefabs[i]} placed at {positions[i]}");
                    }
                }
                else
                {
                    Debug.LogWarning($"  ⚠️  Could not load {prefabPath}");
                }
            }
        }

        private static void AddMarketStructures(Transform parent)
        {
            // Mediterranean Ruins Kit location (note the special dash character)
            string ruinsPath = "Assets/EmbersStorm – Mediterranean Ruins Building Kit/Prefabs/";

            // Market structure prefabs
            string[] stallPrefabs = new string[]
            {
                "Ruins_Floor_A.prefab",
                "Ruins_Floor_B.prefab",
                "Roof.A.prefab",
                "Roof.B.prefab"
            };

            Vector3[] positions = new Vector3[]
            {
                new Vector3(-8, 0, 5),    // Left market floor
                new Vector3(8, 0, 5),    // Right market floor
                new Vector3(0, 2, 8),    // Center roof
                new Vector3(-10, 2, 10)  // Left roof structure
            };

            for (int i = 0; i < stallPrefabs.Length && i < positions.Length; i++)
            {
                string prefabPath = ruinsPath + stallPrefabs[i];
                GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);

                if (prefab != null)
                {
                    GameObject instance = PrefabUtility.InstantiatePrefab(prefab, parent) as GameObject;
                    if (instance != null)
                    {
                        instance.name = stallPrefabs[i].Replace(".prefab", "");
                        instance.transform.position = positions[i];
                        instance.transform.rotation = Quaternion.Euler(0, Random.Range(0, 4) * 90f, 0);
                        SetLayerRecursive(instance, LayerMask.NameToLayer("Midground"));
                        Debug.Log($"  ✅ {stallPrefabs[i]} placed at {positions[i]}");
                    }
                }
                else
                {
                    Debug.LogWarning($"  ⚠️  Could not load {prefabPath}");
                }
            }
        }

        private static void AddForegroundProps(Transform parent)
        {
            // Kyle's Rock Pack small props
            string rocksPath = "Assets/Kyle's Rock Pack/Kyle Fuji/Prefabs/";

            string[] propPrefabs = new string[]
            {
                "boulder_1_bl.prefab",
                "boulder_2_tl.prefab",
                "boulder_3_tr.prefab"
            };

            Vector3[] positions = new Vector3[]
            {
                new Vector3(-5, 0.5f, -1),
                new Vector3(6, 0.5f, 0),
                new Vector3(-3, 0.5f, 1),
                new Vector3(4, 0.5f, -2)
            };

            for (int i = 0; i < positions.Length; i++)
            {
                int prefabIdx = i % propPrefabs.Length;
                string prefabPath = rocksPath + propPrefabs[prefabIdx];
                GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);

                if (prefab != null)
                {
                    GameObject instance = PrefabUtility.InstantiatePrefab(prefab, parent) as GameObject;
                    if (instance != null)
                    {
                        instance.name = $"Prop_{i}";
                        instance.transform.position = positions[i];
                        instance.transform.localScale = Vector3.one * 0.5f;
                        SetLayerRecursive(instance, LayerMask.NameToLayer("Foreground"));
                    }
                }
            }

            // Add ground plane
            GameObject groundPlane = new GameObject("Ground");
            groundPlane.transform.parent = parent;
            groundPlane.transform.localPosition = Vector3.zero;

            MeshFilter mf = groundPlane.AddComponent<MeshFilter>();
            mf.mesh = Resources.GetBuiltinResource<Mesh>("Cube.fbx");

            MeshRenderer mr = groundPlane.AddComponent<MeshRenderer>();
            Material groundMat = new Material(Shader.Find("Standard"));
            groundMat.color = new Color(0.6f, 0.55f, 0.5f); // Brown-tan
            mr.material = groundMat;

            MeshCollider mc = groundPlane.AddComponent<MeshCollider>();

            groundPlane.transform.localScale = new Vector3(30, 0.1f, 30);
            groundPlane.layer = LayerMask.NameToLayer("Foreground");

            Debug.Log("  ✅ Ground plane created");
        }

        private static void AddPlayerCharacter(Transform parent)
        {
            // Try to load player from StarterAssets
            string playerPath = "Assets/StarterAssets/Prefabs/PlayerCapsule.prefab";
            GameObject playerPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(playerPath);

            if (playerPrefab != null)
            {
                GameObject playerInstance = PrefabUtility.InstantiatePrefab(playerPrefab, parent) as GameObject;
                if (playerInstance != null)
                {
                    playerInstance.name = "Player";
                    playerInstance.transform.position = new Vector3(0, 1, -3);
                    playerInstance.layer = LayerMask.NameToLayer("Default");
                    SetLayerRecursive(playerInstance, LayerMask.NameToLayer("Default"));

                    // Add collider if missing
                    if (playerInstance.GetComponent<CapsuleCollider>() == null)
                    {
                        playerInstance.AddComponent<CapsuleCollider>();
                    }

                    // Add rigidbody if missing
                    if (playerInstance.GetComponent<Rigidbody>() == null)
                    {
                        Rigidbody rb = playerInstance.AddComponent<Rigidbody>();
                        rb.mass = 1;
                        rb.drag = 0;
                        rb.angularDrag = 0.05f;
                        rb.useGravity = true;
                        rb.isKinematic = false;
                        rb.constraints = RigidbodyConstraints.FreezeRotation;
                    }

                    Debug.Log("  ✅ Player character added at (0, 1, -3)");
                }
            }
            else
            {
                // Fallback: create simple player capsule
                GameObject player = new GameObject("Player");
                player.transform.parent = parent;
                player.transform.position = new Vector3(0, 1, -3);

                CapsuleCollider capsule = player.AddComponent<CapsuleCollider>();
                capsule.radius = 0.5f;
                capsule.height = 2f;

                Rigidbody rb = player.AddComponent<Rigidbody>();
                rb.mass = 1;
                rb.useGravity = true;
                rb.constraints = RigidbodyConstraints.FreezeRotation;

                // Add visual
                GameObject visual = GameObject.CreatePrimitive(PrimitiveType.Capsule);
                visual.transform.parent = player.transform;
                visual.transform.localPosition = Vector3.zero;
                visual.GetComponent<Collider>().enabled = false;
                Material playerMat = new Material(Shader.Find("Standard"));
                playerMat.color = new Color(0.2f, 0.8f, 0.3f); // Green
                visual.GetComponent<MeshRenderer>().material = playerMat;

                player.layer = LayerMask.NameToLayer("Default");
                Debug.Log("  ✅ Player character created (fallback)");
            }
        }

        private static void SetLayerRecursive(GameObject obj, int layer)
        {
            obj.layer = layer;
            foreach (Transform child in obj.transform)
            {
                SetLayerRecursive(child.gameObject, layer);
            }
        }

        [MenuItem("Velinor/Scene Setup/Clear Test Objects")]
        public static void ClearTestObjects()
        {
            // Remove test objects if they exist
            GameObject[] testObjects = new GameObject[]
            {
                GameObject.Find("Ground Plane"),
                GameObject.Find("Test Stall"),
                GameObject.Find("Test Mountain")
            };

            foreach (GameObject obj in testObjects)
            {
                if (obj != null)
                {
                    Object.DestroyImmediate(obj);
                    Debug.Log($"Removed: {obj.name}");
                }
            }

            EditorSceneManager.MarkSceneDirty(SceneManager.GetActiveScene());
            Debug.Log("✅ Test objects cleared");
        }
    }
}
