using UnityEngine;

namespace Velinor.Persistence
{
    [CreateAssetMenu(menuName = "Velinor/Persistence/Development Overrides")]
    public class DevelopmentOverrides : ScriptableObject
    {
        private static DevelopmentOverrides instance;
        public static DevelopmentOverrides Instance
        {
            get
            {
#if UNITY_EDITOR
                if (instance == null)
                {
                    instance = Resources.Load<DevelopmentOverrides>("DevelopmentOverrides");
                }
                return instance;
#else
                return null;
#endif
            }
        }

        [Header("Save Protection")]
        public bool disableAllSaveWrites = true;
        public bool allowGlobalSettingsWrites = false;
        public bool allowGlobalMetaWrites = false;
        public bool allowProductionProfileWrites = false;
        public bool allowTestProfileWrites = true;

        [Header("Profile Bypass")]
        public bool useDedicatedTestProfile = false;
        public bool bypassProfileRequirement = false;

        [Header("Progression Overrides")]
        public bool unlockEverything = false;
        public bool unlockInventory = false;
        public bool unlockAllSchematics = false;
        public bool grantAllTools = false;
        public bool ignoreCraftingRequirements = false;
        public int startingBits = 0;

        [Header("Narrative Overrides")]
        public bool skipTitleIntro = false;
        public bool markGameCompleted = false;

        public bool CanWriteSettings()
        {
#if UNITY_EDITOR
            if (disableAllSaveWrites) return false;
            return allowGlobalSettingsWrites;
#else
            return true;
#endif
        }

        public bool CanWriteMeta()
        {
#if UNITY_EDITOR
            if (disableAllSaveWrites) return false;
            return allowGlobalMetaWrites;
#else
            return true;
#endif
        }

        public bool CanWriteProfile(bool isTestProfile)
        {
#if UNITY_EDITOR
            if (disableAllSaveWrites) return false;
            return isTestProfile ? allowTestProfileWrites : allowProductionProfileWrites;
#else
            return true;
#endif
        }

        public bool IsInventoryUnlocked(bool productionState)
        {
#if UNITY_EDITOR
            return productionState || unlockEverything || unlockInventory;
#else
            return productionState;
#endif
        }

        public bool IsSchematicLearned(bool productionState)
        {
#if UNITY_EDITOR
            return productionState || unlockEverything || unlockAllSchematics;
#else
            return productionState;
#endif
        }
    }
}
