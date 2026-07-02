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
            None
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
                    "Assets/DreamTree2/Model/DreamTree.fbx",
                    new Vector3(2f, 2f, 2f),
                    AssetPackType.DreamTree2,
                    "Stylized dream tree with custom bark/leaf materials"
                ),

                // English Oak Set
                new TreeAsset(
                    "English Oak - Full Leaf",
                    "Assets/3 English Oak Set/Models/Oak.fbx",
                    new Vector3(1.5f, 1.5f, 1.5f),
                    AssetPackType.EnglishOakSet,
                    "Fully leafed English oak tree (summer)"
                ),
                new TreeAsset(
                    "English Oak - Bare",
                    "Assets/3 English Oak Set/Models/Bare_Oak.fbx",
                    new Vector3(1.5f, 1.5f, 1.5f),
                    AssetPackType.EnglishOakSet,
                    "Bare winter oak (seasonal variety)"
                ),
                new TreeAsset(
                    "English Oak - Bent",
                    "Assets/3 English Oak Set/Models/Bent_Oak.fbx",
                    new Vector3(1.5f, 1.5f, 1.5f),
                    AssetPackType.EnglishOakSet,
                    "Bent oak for visual interest"
                ),

                // Dry Trees
                new TreeAsset(
                    "Dry Tree 1",
                    "Assets/Dry_Trees/Dry3333.fbx",
                    new Vector3(2.5f, 2.5f, 2.5f),
                    AssetPackType.DryTrees,
                    "Dead/dying tree for arid areas"
                ),
                new TreeAsset(
                    "Dry Tree 2",
                    "Assets/Dry_Trees/Dry4910.fbx",
                    new Vector3(2.5f, 2.5f, 2.5f),
                    AssetPackType.DryTrees,
                    "Low-poly dried tree variant"
                ),

                // URP Tree Models
                new TreeAsset(
                    "URP Tree Variant 1",
                    "Assets/Tree_Packs/URP_Tree_Pack/Models/Tree1.fbx",
                    new Vector3(1.2f, 1.2f, 1.2f),
                    AssetPackType.URPTreeModels,
                    "URP-optimized tree model (check path)"
                ),

                // Stumps (from Scan Stumps)
                new TreeAsset(
                    "Tree Stump - Fresh",
                    "Assets/GreenBugGames/Stump_fresh.fbx",
                    new Vector3(1f, 1f, 1f),
                    AssetPackType.ScanStumps,
                    "Photogrammetry fresh tree stump"
                ),
                new TreeAsset(
                    "Tree Stump - Old",
                    "Assets/GreenBugGames/Stump_old.fbx",
                    new Vector3(1f, 1f, 1f),
                    AssetPackType.ScanStumps,
                    "Weathered old stump (seating/props)"
                ),

                // Succulents/Ground Vegetation
                new TreeAsset(
                    "Succulent Plant",
                    "Assets/SeedMesh/Succulents/Succulent_01.fbx",
                    new Vector3(0.5f, 0.5f, 0.5f),
                    AssetPackType.Succulents,
                    "Small decorative succulent plant"
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
                    "Assets/Kyle's Rock Pack/Materials/M_arid_rocks_1.mat",
                    AssetPackType.KylesRockPack,
                    "ground",
                    "Desert/arid stone texture"
                ),
                new MaterialAsset(
                    "Rock - Arid 2",
                    "Assets/Kyle's Rock Pack/Materials/M_arid_rocks_2.mat",
                    AssetPackType.KylesRockPack,
                    "ground",
                    "Arid stone variant 2"
                ),
                new MaterialAsset(
                    "Rock - Mossy 1",
                    "Assets/Kyle's Rock Pack/Materials/M_mossy_rocks_1.mat",
                    AssetPackType.KylesRockPack,
                    "ground",
                    "Moss-covered stones (forest aesthetic)"
                ),
                new MaterialAsset(
                    "Rock - Snow 1",
                    "Assets/Kyle's Rock Pack/Materials/M_snow_rocks_1.mat",
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
                new MaterialAsset(
                    "Brick - Mediterranean",
                    "Assets/EmbersStorm – Mediterranean Ruins Building Kit/Materials/Bricks037.mat",
                    AssetPackType.EmbersStorm,
                    "wall",
                    "Mediterranean red bricks"
                ),
                new MaterialAsset(
                    "Tiles - Mediterranean",
                    "Assets/EmbersStorm – Mediterranean Ruins Building Kit/Materials/Tiles038.mat",
                    AssetPackType.EmbersStorm,
                    "floor",
                    "Ceramic tiles (marketplace walkway)"
                ),
                new MaterialAsset(
                    "Plaster - Mediterranean",
                    "Assets/EmbersStorm – Mediterranean Ruins Building Kit/Materials/PaintedPlaster010.mat",
                    AssetPackType.EmbersStorm,
                    "wall",
                    "Aged plaster wall"
                ),

                // Country House - Interior materials
                new MaterialAsset(
                    "Wood - Country House",
                    "Assets/ALP_Assets/Materials/OldHouseMapWood01.mat",
                    AssetPackType.CountryHouse,
                    "wood",
                    "Old European wood texture"
                ),
                new MaterialAsset(
                    "Glass - Interior",
                    "Assets/ALP_Assets/Materials/Glass.mat",
                    AssetPackType.CountryHouse,
                    "wall",
                    "Aged glass (windows/doors)"
                ),

                // Dream Tree 2 - Grass/Ground
                new MaterialAsset(
                    "Grass - Dream Texture",
                    "Assets/DreamTree2/Materials/grass 01.mat",
                    AssetPackType.DreamTree2,
                    "ground",
                    "Stylized grass material"
                ),

                // Dry Trees - Bark texture
                new MaterialAsset(
                    "Bark - Dead Tree",
                    "Assets/Dry_Trees/Bark.mat",
                    AssetPackType.DryTrees,
                    "wood",
                    "Dry/dead bark texture"
                ),
            };

            return materials;
        }

        // ========== HELPER METHODS ==========

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
        /// Get trees by asset pack
        /// </summary>
        public static List<TreeAsset> GetTreesByPack(AssetPackType pack)
        {
            List<TreeAsset> results = new List<TreeAsset>();
            foreach (var tree in GetTreeAssets())
            {
                if (tree.pack == pack)
                    results.Add(tree);
            }
            return results;
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
                Debug.LogWarning($"  ⚠️  Asset not found: {prefabPath}");
                return null;
            }
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
            
            foreach (var tree in GetAllTrees())
            {
                Debug.Log($"  🌳 {tree.name} ({tree.pack}) - {tree.description}");
            }

            foreach (var mat in GetAllMaterials())
            {
                Debug.Log($"  🎨 {mat.name} ({mat.surfaceType}) - {mat.description}");
            }
            
            Debug.Log("================================");
        }
    }
}
