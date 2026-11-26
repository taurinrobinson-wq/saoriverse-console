using UnityEngine;
using System.Collections.Generic;
using Velinor.Core;
using Velinor.Inventory;
using Velinor.Economy;
using Velinor.Management;

namespace Velinor.Persistence
{
    public class SaveCoordinator : MonoBehaviour
    {
        public static SaveCoordinator Instance { get; private set; }

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            if (transform.parent == null) DontDestroyOnLoad(gameObject);
        }

        /// <summary>
        /// Creates a valid continue point for the active profile.
        /// Should be called after initial gameplay setup is complete.
        /// </summary>
        public void CreateFirstValidCheckpoint()
        {
            ProfileData data = ProfileManager.Instance.ActiveProfile;
            if (data == null) return;

            data.gameStarted = true;
            data.hasValidContinuePoint = true;
            CaptureSnapshot();
            
            Debug.Log("[SaveCoordinator] First valid continue point established.");
        }

        public void SaveCheckpoint()
        {
            CaptureSnapshot();
            Debug.Log("[SaveCoordinator] Checkpoint saved.");
        }
        public void CaptureSnapshot()
        {
            ProfileData data = ProfileManager.Instance.ActiveProfile;
            if (data == null) return;

            // 1. Economy
            if (CurrencySystem.Instance != null)
                data.bits = CurrencySystem.Instance.CurrentBits;

            // 2. Inventory
            if (InventoryService.Instance != null)
            {
                data.inventory.Clear();
                foreach (var kvp in InventoryService.Instance.GetAll())
                {
                    data.inventory.Add(new InventoryItemEntry { itemId = kvp.Key, quantity = kvp.Value });
                }
                data.learnedSchematics = new List<string>(InventoryService.Instance.GetLearnedSchematics());
            }

            // 3. Stats
            // Capture tone and remnants from StatManager (needs implementation of accessors)
            
            // 4. Narrative (Flags & Diary)
            data.gameFlags.Clear();
            foreach (var flag in GameFlags.GetAllFlags())
                data.gameFlags.Add(new FlagEntry { key = flag.Key, value = flag.Value });

            if (DiaryManager.Instance != null)
            {
                data.diaryEntries.Clear();
                foreach (var entry in DiaryManager.Instance.GetEntries())
                    data.diaryEntries.Add(new DiaryEntryData { timestamp = entry.timestamp, content = entry.content });
            }

            // 5. Codex
            if (CodexManager.Instance != null)
            {
                data.codexTags = new List<string>(CodexManager.Instance.State.ActiveTags);
                data.resolvedGlyphs = new List<string>(CodexManager.Instance.State.ResolvedGlyphIds);
                data.codexResonance = CodexManager.Instance.State.ResonanceLevel;
            }

            // 6. Progression
            data.lastSavedScene = UnityEngine.SceneManagement.SceneManager.GetActiveScene().name;
            // data.lastSpawnID = ... (needs logic to determine last spawn)

            data.lastSaveTimestampTicks = System.DateTime.Now.Ticks;
            
            ProfileManager.Instance.SaveActiveProfile();
        }

        /// <summary>
        /// Restores all participating systems from the current active profile.
        /// </summary>
        public void RestoreFromSnapshot()
        {
            ProfileData data = ProfileManager.Instance.ActiveProfile;
            if (data == null) return;

            // 1. Economy
            if (CurrencySystem.Instance != null)
                CurrencySystem.Instance.SetBits(data.bits);

            // 2. Inventory
            if (InventoryService.Instance != null)
            {
                List<InventoryEntryData> invList = new List<InventoryEntryData>();
                foreach (var entry in data.inventory)
                    invList.Add(new InventoryEntryData { itemId = entry.itemId, quantity = entry.quantity });
                
                InventoryService.Instance.LoadSaveData(invList);
                
                foreach (var sch in data.learnedSchematics)
                    InventoryService.Instance.LearnSchematic(sch);
            }

            // 3. Narrative
            GameFlags.Clear();
            foreach (var flag in data.gameFlags)
                GameFlags.Set(flag.key, flag.value);

            if (DiaryManager.Instance != null)
            {
                DiaryManager.Instance.RestoreEntries(data.diaryEntries);
            }

            // 4. Codex
            if (CodexManager.Instance != null)
            {
                // Needs restore logic in CodexState
            }
            
            Debug.Log($"[SaveCoordinator] Restored state from profile: {data.displayName}");
        }
    }
}
