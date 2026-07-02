using UnityEngine;
using UnityEditor;
using System.Collections.Generic;

namespace Velinor.Editor
{
    /// <summary>
    /// AssetPackManager: Centralized system for managing and placing assets from selected packs
    /// Integrates 12 curated asset packs into the marketplace scene
    /// Supports: Trees, Vegetation, Stalls, Materials, Props
    /// </summary>
    public static class AssetPackManager
    {
        // ========== ASSET PACK DEFINITIONS ==========
        
        public enum AssetPackType
        {
            DreamTree2,
            DryTrees,
            EmbersStorm,
            EnglishOakSet,
            KylesRockPack,
            ScanStumps,
            Succulents,
            TheShed,
            URPTreeModels,
            CountryHouse,
            MedievalProps,
            None
        }

        /// <summary>
        /// Prop asset definitions for marketplace decorations
        /// </summary>
        public class PropAsset
        {
            public string name;
            public string prefabPath;
            public Vector3 scale;
            public AssetPackType pack;
            public string propType; // "container", "furniture", "decoration", "transport"
            public string description;

            public PropAsset(string name, string prefabPath, Vector3 scale, AssetPackType pack, string propType, string description)
            {
                this.name = name;
                this.prefabPath = prefabPath;
                this.scale = scale;
                this.pack = pack;
                this.propType = propType;
                this.description = description;
            }
        }

        /// <summary>
        /// Tree asset definitions for vegetation placement
        /// </summary>
        public class TreeAsset
        {
            public string name;
            public string prefabPath;
            public Vector3 scale;
            public AssetPackType pack;
            public string description;

            public TreeAsset(string name, string prefabPath, Vector3 scale, AssetPackType pack, string description)
            {
                this.name = name;
                this.prefabPath = prefabPath;
                this.scale = scale;
                this.pack = pack;
                this.description = description;
            }
        }

        /// <summary>
        /// Material asset definitions for surfaces
        /// </summary>
        public class MaterialAsset
        {
            public string name;
            public string materialPath;
            public AssetPackType pack;
            public string surfaceType; // "ground", "wall", "floor", "wood", "stone"
            public string description;

            public MaterialAsset(string name, string materialPath, AssetPackType pack, string surfaceType, string description)
            {
                this.name = name;
                this.materialPath = materialPath;
                this.pack = pack;
                this.surfaceType = surfaceType;
                this.description = description;
            }
        }

        // ========== TREE ASSETS ==========
        
        private static List<TreeAsset> GetTreeAssets()
        {
            List<TreeAsset> trees = new List<TreeAsset>
            {
                // Dream Tree 2
                new TreeAsset(
                    "Dream Tree 2",
                    "Assets/DreamTree2/Mesh/DreamTree.FBX",
                    new Vector3(2f, 2f, 2f),
                    AssetPackType.DreamTree2,
                    "Stylized dream tree with custom bark/leaf materials"
                ),

                // English Oak Set
                new TreeAsset(
                    "English Oak - Full Leaf",
                    "Assets/3 English Oak Set/Oak.fbx",
                    new Vector3(1.5f, 1.5f, 1.5f),
                    AssetPackType.EnglishOakSet,
                    "Fully leafed English oak tree (summer)"
                ),
                new TreeAsset(
                    "English Oak - Bare",
                    "Assets/3 English Oak Set/Bare_Oak.fbx",
                    new Vector3(1.5f, 1.5f, 1.5f),
                    AssetPackType.EnglishOakSet,
                    "Bare winter oak (seasonal variety)"
                ),
                new TreeAsset(
                    "English Oak - Bent",
                    "Assets/3 English Oak Set/Bent_Oak.fbx",
                    new Vector3(1.5f, 1.5f, 1.5f),
                    AssetPackType.EnglishOakSet,
                    "Bent oak for visual interest"
                ),

                // Dry Trees
                new TreeAsset(
                    "Dry Tree 1",
                    "Assets/Dry_Trees/Model/Dry3333.fbx",
                    new Vector3(2.5f, 2.5f, 2.5f),
                    AssetPackType.DryTrees,
                    "Dead/dying tree for arid areas"
                ),
                new TreeAsset(
                    "Dry Tree 2",
                    "Assets/Dry_Trees/Model/Dry4910.fbx",
                    new Vector3(2.5f, 2.5f, 2.5f),
                    AssetPackType.DryTrees,
                    "Low-poly dried tree variant"
                ),
            };

            return trees;
        }

        // ========== MATERIAL ASSETS ==========
        
        private static List<MaterialAsset> GetMaterialAssets()
        {
            List<MaterialAsset> materials = new List<MaterialAsset>
            {
                // Kyle's Rock Pack - Ground materials
                new MaterialAsset(
                    "Rock - Arid 1",
                    "Assets/Kyle's Rock Pack/Kyle Fuji/Materials/M_arid_rocks_1.mat",
                    AssetPackType.KylesRockPack,
                    "ground",
                    "Desert/arid stone texture"
                ),
                new MaterialAsset(
                    "Rock - Arid 2",
                    "Assets/Kyle's Rock Pack/Kyle Fuji/Materials/M_arid_rocks_2.mat",
                    AssetPackType.KylesRockPack,
                    "ground",
                    "Arid stone variant 2"
                ),
                new MaterialAsset(
                    "Rock - Mossy 1",
                    "Assets/Kyle's Rock Pack/Kyle Fuji/Materials/M_mossy_rocks_1.mat",
                    AssetPackType.KylesRockPack,
                    "ground",
                    "Moss-covered stones (forest aesthetic)"
                ),
                new MaterialAsset(
                    "Rock - Snow 1",
                    "Assets/Kyle's Rock Pack/Kyle Fuji/Materials/M_snow_rocks_1.mat",
                    AssetPackType.KylesRockPack,
                    "ground",
                    "Snow-covered rocks (winter)"
                ),

                // The Shed - Rustic materials
                new MaterialAsset(
                    "The Shed - Main",
                    "Assets/Blackant Master Studio/The Shed/The Shed Optimized/Materials/The Shed.mat",
                    AssetPackType.TheShed,
                    "wall",
                    "Wooden shed texture (rustic)"
                ),
                new MaterialAsset(
                    "The Shed - Wood",
                    "Assets/Blackant Master Studio/The Shed/The Shed Optimized/Materials/The SHed Tools_Dif.mat",
                    AssetPackType.TheShed,
                    "wood",
                    "Rough wood material"
                ),

                // EmbersStorm - Mediterranean materials


                // Dream Tree 2 - Grass/Ground
                new MaterialAsset(
                    "Grass - Dream Texture",
                    "Assets/DreamTree2/Materials/grass 01.mat",
                    AssetPackType.DreamTree2,
                    "ground",
                    "Stylized grass material"
                ),

                // Dry Trees - Bark texture

            };

            return materials;
        }

        // ========== PROP ASSETS ==========
        
        private static List<PropAsset> GetPropAssets()
        {
            List<PropAsset> props = new List<PropAsset>
            {
                // Medieval Props Pack 01 - Containers
                new PropAsset(
                    "Barrel",
                    "Assets/Medieval Props Pack 01/Universal Render Pipeline(URP)/Prefabs/Barrel 01.prefab",
                    new Vector3(1f, 1f, 1f),
                    AssetPackType.MedievalProps,
                    "container",
                    "Wooden barrel for stall storage"
                ),
                new PropAsset(
                    "Clay Pot",
                    "Assets/Medieval Props Pack 01/Universal Render Pipeline(URP)/Prefabs/Clay Pot.prefab",
                    new Vector3(0.8f, 0.8f, 0.8f),
                    AssetPackType.MedievalProps,
                    "container",
                    "Large clay storage pot"
                ),
                new PropAsset(
                    "Wooden Box 01",
                    "Assets/Medieval Props Pack 01/Universal Render Pipeline(URP)/Prefabs/Wooden Box 01.prefab",
                    new Vector3(1f, 1f, 1f),
                    AssetPackType.MedievalProps,
                    "container",
                    "Storage crate for market goods"
                ),
                new PropAsset(
                    "Crate 01",
                    "Assets/Medieval Props Pack 01/Universal Render Pipeline(URP)/Prefabs/Crate_01.prefab",
                    new Vector3(0.9f, 0.9f, 0.9f),
                    AssetPackType.MedievalProps,
                    "container",
                    "Wooden shipping crate"
                ),
                new PropAsset(
                    "Crate 02",
                    "Assets/Medieval Props Pack 01/Universal Render Pipeline(URP)/Prefabs/Crate_02.prefab",
                    new Vector3(0.9f, 0.9f, 0.9f),
                    AssetPackType.MedievalProps,
                    "container",
                    "Wooden shipping crate (variant)"
                ),
                new PropAsset(
                    "Bucket",
                    "Assets/Medieval Props Pack 01/Universal Render Pipeline(URP)/Prefabs/Wooden_Bucket_1.prefab",
                    new Vector3(0.7f, 0.7f, 0.7f),
                    AssetPackType.MedievalProps,
                    "container",
                    "Wooden water bucket"
                ),

                // Medieval Props Pack 01 - Furniture
                new PropAsset(
                    "Table",
                    "Assets/Medieval Props Pack 01/Universal Render Pipeline(URP)/Prefabs/Old_Table.prefab",
                    new Vector3(1.2f, 1.2f, 1.2f),
                    AssetPackType.MedievalProps,
                    "furniture",
                    "Old wooden market table"
                ),
                new PropAsset(
                    "Handcart",
                    "Assets/Medieval Props Pack 01/Universal Render Pipeline(URP)/Prefabs/Handcart.prefab",
                    new Vector3(1.1f, 1.1f, 1.1f),
                    AssetPackType.MedievalProps,
                    "transport",
                    "Medieval merchant handcart with barrel"
                ),
                new PropAsset(
                    "Tent",
                    "Assets/Medieval Props Pack 01/Universal Render Pipeline(URP)/Prefabs/Tent.prefab",
                    new Vector3(1.3f, 1.3f, 1.3f),
                    AssetPackType.MedievalProps,
                    "furniture",
                    "Market stall tent/canopy"
                ),
                new PropAsset(
                    "Palette",
                    "Assets/Medieval Props Pack 01/Universal Render Pipeline(URP)/Prefabs/Palette.prefab",
                    new Vector3(1f, 1f, 1f),
                    AssetPackType.MedievalProps,
                    "furniture",
                    "Wooden palette for goods display"
                ),

                // Medieval Props Pack 01 - Decorations
                new PropAsset(
                    "Clay Mug",
                    "Assets/Medieval Props Pack 01/Universal Render Pipeline(URP)/Prefabs/Clay Mug 2.prefab",
                    new Vector3(0.5f, 0.5f, 0.5f),
                    AssetPackType.MedievalProps,
                    "decoration",
                    "Clay drinking mug (display)"
                ),
                new PropAsset(
                    "Vase 1",
                    "Assets/Medieval Props Pack 01/Universal Render Pipeline(URP)/Prefabs/Vase_1.prefab",
                    new Vector3(0.8f, 0.8f, 0.8f),
                    AssetPackType.MedievalProps,
                    "decoration",
                    "Decorative clay vase"
                ),
                new PropAsset(
                    "Vase 2",
                    "Assets/Medieval Props Pack 01/Universal Render Pipeline(URP)/Prefabs/Vase_2.prefab",
                    new Vector3(0.7f, 0.7f, 0.7f),
                    AssetPackType.MedievalProps,
                    "decoration",
                    "Decorative clay vase (variant)"
                ),
                new PropAsset(
                    "Rope",
                    "Assets/Medieval Props Pack 01/Universal Render Pipeline(URP)/Prefabs/Rope.prefab",
                    new Vector3(1f, 1f, 1f),
                    AssetPackType.MedievalProps,
                    "decoration",
                    "Coiled rope for stall decoration"
                ),
            };

            return props;
        }

        /// <summary>
        /// Get all available tree assets
        /// </summary>
        public static List<TreeAsset> GetAllTrees()
        {
            return GetTreeAssets();
        }

        /// <summary>
        /// Get all available materials
        /// </summary>
        public static List<MaterialAsset> GetAllMaterials()
        {
            return GetMaterialAssets();
        }

        /// <summary>
        /// Get all available prop assets
        /// </summary>
        public static List<PropAsset> GetAllProps()
        {
            return GetPropAssets();
        }

        /// <summary>
        /// Get props by type (container, furniture, decoration, transport)
        /// </summary>
        public static List<PropAsset> GetPropsByType(string propType)
        {
            List<PropAsset> results = new List<PropAsset>();
            foreach (var prop in GetPropAssets())
            {
                if (prop.propType == propType)
                    results.Add(prop);
            }
            return results;
        }

        /// <summary>
        /// Get props by asset pack
        /// </summary>
        public static List<PropAsset> GetPropsByPack(AssetPackType pack)
        {
            List<PropAsset> results = new List<PropAsset>();
            foreach (var prop in GetPropAssets())
            {
                if (prop.pack == pack)
                    results.Add(prop);
            }
            return results;
        }

        /// <summary>
        /// Place a prop in the scene
        /// </summary>
        public static GameObject PlaceProp(PropAsset asset, Vector3 position, Transform parent = null)
        {
            GameObject prefab = LoadAsset(asset.prefabPath);
            if (prefab == null)
                return null;

            GameObject instance = Object.Instantiate(prefab, position, Quaternion.identity);
            instance.name = asset.name;
            instance.transform.localScale = asset.scale;
            
            if (parent != null)
                instance.transform.parent = parent;

            // Fix any broken materials on the prop
            FixPropMaterials(instance);

            return instance;
        }

        /// <summary>
        /// Fix broken/pink materials on a prop by replacing with Standard shader
        /// </summary>
        private static void FixPropMaterials(GameObject prop)
        {
            // Create a default material with Standard shader for props
            Material standardMat = new Material(Shader.Find("Standard"));
            standardMat.color = new Color(0.7f, 0.7f, 0.7f); // Light gray for props
            
            MeshRenderer[] renderers = prop.GetComponentsInChildren<MeshRenderer>();
            foreach (MeshRenderer renderer in renderers)
            {
                Material[] mats = new Material[renderer.sharedMaterials.Length];
                for (int i = 0; i < mats.Length; i++)
                    mats[i] = standardMat;
                renderer.sharedMaterials = mats;
            }
        }

        /// <summary>
        /// Get materials by surface type
        /// </summary>
        public static List<MaterialAsset> GetMaterialsByType(string surfaceType)
        {
            List<MaterialAsset> results = new List<MaterialAsset>();
            foreach (var mat in GetMaterialAssets())
            {
                if (mat.surfaceType == surfaceType)
                    results.Add(mat);
            }
            return results;
        }

        /// <summary>
        /// Load a prefab from asset pack
        /// </summary>
        public static GameObject LoadAsset(string prefabPath)
        {
            Object prefab = AssetDatabase.LoadAssetAtPath<Object>(prefabPath);
            if (prefab == null)
            {
                Debug.LogError($"❌ FAILED TO LOAD: {prefabPath}");
                return null;
            }
            Debug.Log($"✅ Loaded: {prefabPath}");
            return prefab as GameObject;
        }

        /// <summary>
        /// Load a material from asset pack
        /// </summary>
        public static Material LoadMaterial(string materialPath)
        {
            Material mat = AssetDatabase.LoadAssetAtPath<Material>(materialPath);
            if (mat == null)
            {
                Debug.LogWarning($"  ⚠️  Material not found: {materialPath}");
                return null;
            }
            return mat;
        }

        /// <summary>
        /// Create and position a tree in the scene
        /// </summary>
        public static GameObject PlaceTree(TreeAsset asset, Vector3 position, Transform parent = null)
        {
            GameObject prefab = LoadAsset(asset.prefabPath);
            if (prefab == null)
                return null;

            GameObject instance = Object.Instantiate(prefab, position, Quaternion.identity);
            instance.name = asset.name;
            instance.transform.localScale = asset.scale;
            
            if (parent != null)
                instance.transform.parent = parent;

            // Fix any broken materials on the tree
            FixPropMaterials(instance);

            return instance;
        }

        /// <summary>
        /// Apply material to a renderer
        /// </summary>
        public static void ApplyMaterial(GameObject target, Material material)
        {
            Renderer renderer = target.GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.material = material;
            }
        }

        /// <summary>
        /// Log available assets summary
        /// </summary>
        public static void LogAssetsAvailable()
        {
            Debug.Log("====== ASSET PACK MANAGER ======");
            Debug.Log($"✅ Trees available: {GetAllTrees().Count}");
            Debug.Log($"✅ Materials available: {GetAllMaterials().Count}");
            Debug.Log($"✅ Props available: {GetAllProps().Count}");
            
            foreach (var tree in GetAllTrees())
            {
                Debug.Log($"  🌳 {tree.name} ({tree.pack}) - {tree.description}");
            }

            foreach (var mat in GetAllMaterials())
            {
                Debug.Log($"  🎨 {mat.name} ({mat.surfaceType}) - {mat.description}");
            }

            foreach (var prop in GetAllProps())
            {
                Debug.Log($"  🏺 {prop.name} ({prop.propType}) - {prop.description}");
            }
            
            Debug.Log("================================");
        }

        /// <summary>
        /// Validate all asset paths and report which ones are missing
        /// </summary>
        public static void ValidateAllAssets()
        {
            Debug.Log("\n🔍 VALIDATING ALL ASSET PATHS...\n");
            
            int foundCount = 0;
            int missingCount = 0;

            // Validate trees
            foreach (var tree in GetAllTrees())
            {
                Object obj = AssetDatabase.LoadAssetAtPath<Object>(tree.prefabPath);
                if (obj != null)
                {
                    Debug.Log($"✅ TREE: {tree.name}");
                    foundCount++;
                }
                else
                {
                    Debug.LogError($"❌ MISSING TREE: {tree.name} at {tree.prefabPath}");
                    missingCount++;
                }
            }

            // Validate materials
            foreach (var mat in GetAllMaterials())
            {
                Object obj = AssetDatabase.LoadAssetAtPath<Object>(mat.materialPath);
                if (obj != null)
                {
                    Debug.Log($"✅ MATERIAL: {mat.name}");
                    foundCount++;
                }
                else
                {
                    Debug.LogError($"❌ MISSING MATERIAL: {mat.name} at {mat.materialPath}");
                    missingCount++;
                }
            }

            // Validate props
            foreach (var prop in GetAllProps())
            {
                Object obj = AssetDatabase.LoadAssetAtPath<Object>(prop.prefabPath);
                if (obj != null)
                {
                    Debug.Log($"✅ PROP: {prop.name}");
                    foundCount++;
                }
                else
                {
                    Debug.LogError($"❌ MISSING PROP: {prop.name} at {prop.prefabPath}");
                    missingCount++;
                }
            }

            Debug.Log($"\n📊 VALIDATION COMPLETE: {foundCount} found, {missingCount} MISSING\n");
        }
    }
}
