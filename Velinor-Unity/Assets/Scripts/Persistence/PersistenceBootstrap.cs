using UnityEngine;
using Velinor.Core;
using Velinor.Economy;
using Velinor.Management;
using Velinor.Inventory;

namespace Velinor.Persistence
{
    public static class PersistenceBootstrap
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void Initialize()
        {
            // Only bootstrap if we are in the Editor and not starting from TitleScene
            // or if we are in a development build and want bootstrap behavior.
#if UNITY_EDITOR
            if (UnityEngine.SceneManagement.SceneManager.GetActiveScene().name == "TitleScene") return;

            Debug.Log("[PersistenceBootstrap] Direct scene play detected. Initializing persistent systems...");

            EnsureManager<SettingsManager>("SettingsManager");
            EnsureManager<MetaProgressManager>("MetaProgressManager");
            EnsureManager<ProfileManager>("ProfileManager");
            EnsureManager<SaveCoordinator>("SaveCoordinator");

            // Subsystems
            if (AudioManager.Instance == null) CreateManager("AudioManager");
            if (GlobalStateManager.Instance == null) CreateManager("GlobalStateManager");
            if (DiaryManager.Instance == null) CreateManager("DiaryManager");
            if (CurrencySystem.Instance == null) CreateManager("CurrencySystem");
            
            // Initialize test profile if no profile is active
            if (ProfileManager.Instance.ActiveSlotIndex == -1 && ProfileManager.Instance.ActiveProfile == null)
            {
                ProfileManager.Instance.SetActiveProfile(-1); // Dedicated test profile
                SaveCoordinator.Instance.RestoreFromSnapshot();
            }
#endif
        }

        private static void EnsureManager<T>(string name) where T : MonoBehaviour
        {
            if (Object.FindAnyObjectByType<T>() == null)
            {
                CreateManager(name, typeof(T));
            }
        }

        private static void CreateManager(string name, System.Type type = null)
        {
            GameObject obj = new GameObject(name);
            if (type != null) obj.AddComponent(type);
            Object.DontDestroyOnLoad(obj);
        }
    }
}
