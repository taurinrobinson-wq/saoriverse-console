using UnityEngine;

namespace Velinor.Persistence
{
    public static class EffectiveState
    {
        public static bool IsInventoryUnlocked(bool productionState)
        {
            if (DevelopmentOverrides.Instance != null && (DevelopmentOverrides.Instance.unlockEverything || DevelopmentOverrides.Instance.unlockInventory))
                return true;
            return productionState;
        }

        public static bool IsSchematicLearned(string schematicId, bool productionState)
        {
            if (DevelopmentOverrides.Instance != null && (DevelopmentOverrides.Instance.unlockEverything || DevelopmentOverrides.Instance.unlockAllSchematics))
                return true;
            return productionState;
        }

        public static bool GetFlag(string key, bool productionValue)
        {
            // Future: add per-flag overrides if needed
            return productionValue;
        }
    }
}
