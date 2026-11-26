using UnityEngine;
using System.IO;
using System.Collections.Generic;

namespace Velinor.Persistence
{
    public class MetaProgressManager : MonoBehaviour
    {
        public static MetaProgressManager Instance { get; private set; }

        private string metaPath;
        private MetaProgress metaProgress;

        public MetaProgress Data => metaProgress;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            if (transform.parent == null) DontDestroyOnLoad(gameObject);

            metaPath = Path.Combine(Application.persistentDataPath, "meta_progress.json");
            LoadMeta();
        }

        public void LoadMeta()
        {
            if (File.Exists(metaPath))
            {
                try
                {
                    string json = File.ReadAllText(metaPath);
                    metaProgress = JsonUtility.FromJson<MetaProgress>(json);
                }
                catch (System.Exception e)
                {
                    Debug.LogError($"[MetaProgressManager] Load Error: {e.Message}");
                    metaProgress = new MetaProgress();
                }
            }
            else
            {
                metaProgress = new MetaProgress();
            }
        }

        public void SaveMeta()
        {
            if (DevelopmentOverrides.Instance != null && !DevelopmentOverrides.Instance.CanWriteMeta())
            {
                Debug.Log("[MetaProgressManager] Save suppressed by DevelopmentOverrides.");
                return;
            }

            try
            {
                string json = JsonUtility.ToJson(metaProgress, true);
                File.WriteAllText(metaPath, json);
                Debug.Log("[MetaProgressManager] Meta progress saved.");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[MetaProgressManager] Save Error: {e.Message}");
            }
        }

        public void UnlockAsset(string assetId)
        {
            if (!metaProgress.unlockedAssetIds.Contains(assetId))
            {
                metaProgress.unlockedAssetIds.Add(assetId);
                SaveMeta();
            }
        }

        public void UnlockNpc(string npcId)
        {
            if (!metaProgress.unlockedNpcIds.Contains(npcId))
            {
                metaProgress.unlockedNpcIds.Add(npcId);
                SaveMeta();
            }
        }

        public void SetGameCompleted(bool completed)
        {
            metaProgress.gameCompleted = completed;
            SaveMeta();
        }
    }
}
