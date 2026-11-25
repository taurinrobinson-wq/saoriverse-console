using UnityEngine;
using UnityEngine.SceneManagement;
using Velinor.Inventory;
using Velinor.Economy;

namespace Velinor.UI
{
    [DisallowMultipleComponent]
    public class InventoryUIBootstrap : MonoBehaviour
    {
        [Header("Inventory")]
        [SerializeField] private ItemDatabase itemDatabase;

        private UIPersistenceManager persistence;
        private UnityEngine.EventSystems.EventSystem ownedEventSystem;
        private bool subscribed;

        private void Awake()
        {
            persistence = GetComponent<UIPersistenceManager>();
            EnsureReady();
        }

        public bool EnsureReady()
        {
            if (persistence == null) persistence = GetComponent<UIPersistenceManager>();
            if (persistence != null && !persistence.EnsureOwnership()) return false;
            if (itemDatabase == null)
            {
                Debug.LogError("[InventoryUIBootstrap] Assign the inventory database on UI_Canvas.", this);
                return false;
            }
            var inventoryService = InventoryService.EnsureInstance(itemDatabase);
            Velinor.Interactions.ToolSystem.EnsureInstance(inventoryService);
            CurrencySystem.EnsureInstance();
            EnsureEventSystem();
            if (!subscribed)
            {
                SceneManager.sceneLoaded += OnSceneLoaded;
                SceneManager.sceneUnloaded += OnSceneUnloaded;
                subscribed = true;
            }
            return true;
        }

        private void OnSceneLoaded(Scene scene, LoadSceneMode mode) => EnsureEventSystem();
        private void OnSceneUnloaded(Scene scene) => EnsureEventSystem();

        private void EnsureEventSystem()
        {
            // Prefer a scene-owned EventSystem; never disable or delete it.
            UnityEngine.EventSystems.EventSystem sceneSystem = null;
            foreach (var candidate in FindObjectsByType<UnityEngine.EventSystems.EventSystem>(FindObjectsInactive.Exclude))
            {
                if (candidate != ownedEventSystem && candidate.isActiveAndEnabled)
                {
                    sceneSystem = candidate;
                    break;
                }
            }
            if (sceneSystem != null)
            {
                if (ownedEventSystem != null) ownedEventSystem.gameObject.SetActive(false);
                return;
            }
            if (ownedEventSystem == null)
            {
                var root = new GameObject("UI_EventSystem_Runtime");
                root.SetActive(false);
                ownedEventSystem = root.AddComponent<UnityEngine.EventSystems.EventSystem>();
                var module = root.AddComponent<UnityEngine.InputSystem.UI.InputSystemUIInputModule>();
                module.AssignDefaultActions();
                DontDestroyOnLoad(root);
            }
            ownedEventSystem.gameObject.SetActive(true);
        }

        private void OnDestroy()
        {
            if (subscribed)
            {
                SceneManager.sceneLoaded -= OnSceneLoaded;
                SceneManager.sceneUnloaded -= OnSceneUnloaded;
            }
            if (ownedEventSystem != null) Destroy(ownedEventSystem.gameObject);
        }
    }
}
