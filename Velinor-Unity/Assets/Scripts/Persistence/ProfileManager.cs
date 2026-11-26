using UnityEngine;
using System.IO;
using System.Collections.Generic;

namespace Velinor.Persistence
{
    public class ProfileManager : MonoBehaviour
    {
        public static ProfileManager Instance { get; private set; }

        private const string PROFILES_DIR = "profiles";
        private const int SLOT_COUNT = 3;

        private ProfileData[] slots = new ProfileData[SLOT_COUNT];
        private int activeSlotIndex = -1;
        private ProfileData testProfile;

        public int ActiveSlotIndex => activeSlotIndex;
        
        public ProfileData ActiveProfile 
        {
            get 
            {
                if (activeSlotIndex == -1) return null;
                return slots[activeSlotIndex];
            }
        }
        
        /// <summary>
        /// Returns either the active slot profile or the test profile if active.
        /// </summary>
        public ProfileData EffectiveProfile => (activeSlotIndex == -1) ? testProfile : slots[activeSlotIndex];
        public bool IsTestProfileActive => activeSlotIndex == -1 && testProfile != null;

        public void ClearActiveProfile()
        {
            activeSlotIndex = -1;
        }

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            if (transform.parent == null) DontDestroyOnLoad(gameObject);

            EnsureDirectories();
            LoadAllSlots();
        }

        private void EnsureDirectories()
        {
            string path = Path.Combine(Application.persistentDataPath, PROFILES_DIR);
            if (!Directory.Exists(path)) Directory.CreateDirectory(path);

            string testPath = Path.Combine(Application.persistentDataPath, "development");
            if (!Directory.Exists(testPath)) Directory.CreateDirectory(testPath);
        }

        private string GetSlotPath(int index)
        {
            return Path.Combine(Application.persistentDataPath, PROFILES_DIR, $"profile_{index + 1:D2}.json");
        }

        private string GetTestProfilePath()
        {
            return Path.Combine(Application.persistentDataPath, "development", "test_profile.json");
        }

        public void LoadAllSlots()
        {
            for (int i = 0; i < SLOT_COUNT; i++)
            {
                string path = GetSlotPath(i);
                if (File.Exists(path))
                {
                    try
                    {
                        slots[i] = JsonUtility.FromJson<ProfileData>(File.ReadAllText(path));
                    }
                    catch (System.Exception e)
                    {
                        Debug.LogError($"[ProfileManager] Error loading slot {i}: {e.Message}");
                        slots[i] = null;
                    }
                }
                else
                {
                    slots[i] = null;
                }
            }
        }

        public ProfileData GetSlot(int index)
        {
            if (index < 0 || index >= SLOT_COUNT) return null;
            return slots[index];
        }

        public bool CreateProfile(int slotIndex, string name)
        {
            if (slotIndex < 0 || slotIndex >= SLOT_COUNT) return false;

            ProfileData data = new ProfileData { displayName = name };
            slots[slotIndex] = data;
            SaveProfile(slotIndex);
            return true;
        }

        public void SetActiveProfile(int slotIndex)
        {
            activeSlotIndex = slotIndex;
            if (slotIndex != -1)
            {
                // Ensure loaded
                if (slots[slotIndex] == null) LoadAllSlots();
            }
            else
            {
                LoadTestProfile();
            }
        }

        public void LoadTestProfile()
        {
            string path = GetTestProfilePath();
            if (File.Exists(path))
            {
                testProfile = JsonUtility.FromJson<ProfileData>(File.ReadAllText(path));
            }
            else
            {
                testProfile = new ProfileData { displayName = "Test Profile" };
            }
        }

        public void SaveProfile(int slotIndex)
        {
            if (slotIndex < 0 || slotIndex >= SLOT_COUNT) return;
            
            if (DevelopmentOverrides.Instance != null && !DevelopmentOverrides.Instance.CanWriteProfile(false))
            {
                Debug.Log($"[ProfileManager] Save for Slot {slotIndex} suppressed.");
                return;
            }

            ProfileData data = slots[slotIndex];
            if (data == null) return;

            string path = GetSlotPath(slotIndex);
            SafeWrite(path, data);
        }

        public void SaveActiveProfile()
        {
            if (activeSlotIndex != -1)
            {
                SaveProfile(activeSlotIndex);
            }
            else if (testProfile != null)
            {
                if (DevelopmentOverrides.Instance != null && !DevelopmentOverrides.Instance.CanWriteProfile(true))
                {
                    Debug.Log("[ProfileManager] Test Profile save suppressed.");
                    return;
                }
                SafeWrite(GetTestProfilePath(), testProfile);
            }
        }

        private void SafeWrite(string path, ProfileData data)
        {
            try
            {
                string json = JsonUtility.ToJson(data, true);
                string tmpPath = path + ".tmp";
                File.WriteAllText(tmpPath, json);
                if (File.Exists(path)) File.Delete(path);
                File.Move(tmpPath, path);
                Debug.Log($"[ProfileManager] Saved: {path}");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[ProfileManager] Save Error at {path}: {e.Message}");
            }
        }

        public void DeleteProfile(int slotIndex)
        {
            if (slotIndex < 0 || slotIndex >= SLOT_COUNT) return;
            string path = GetSlotPath(slotIndex);
            if (File.Exists(path)) File.Delete(path);
            slots[slotIndex] = null;
            if (activeSlotIndex == slotIndex) activeSlotIndex = -1;
        }

        public void RenameProfile(int slotIndex, string newName)
        {
            if (slotIndex < 0 || slotIndex >= SLOT_COUNT || slots[slotIndex] == null) return;
            slots[slotIndex].displayName = newName;
            SaveProfile(slotIndex);
        }
    }
}
