using UnityEngine;
using UnityEditor;
using UnityEngine.UI;
using Velinor.Persistence.UI;

namespace Velinor.Persistence.Editor
{
    public class TitleScreenSetupTool : EditorWindow
    {
        [MenuItem("Velinor/Setup/Title Screen Overlays")]
        public static void ShowWindow() => GetWindow<TitleScreenSetupTool>("Title Setup");

        private void OnGUI()
        {
            if (GUILayout.Button("Create Persistence Managers"))
            {
                CreateManagers();
            }

            if (GUILayout.Button("Fix Title Screen Wiring"))
            {
                FixWiring();
            }
        }

        private void CreateManagers()
        {
            EnsureManager<SettingsManager>("SettingsManager");
            EnsureManager<MetaProgressManager>("MetaProgressManager");
            EnsureManager<ProfileManager>("ProfileManager");
            EnsureManager<SaveCoordinator>("SaveCoordinator");
        }

        private void FixWiring()
        {
            var tsm = Object.FindAnyObjectByType<TitleScreenManager>();
            if (tsm == null) { Debug.LogError("TitleScreenManager not found"); return; }

            SerializedObject so = new SerializedObject(tsm);
            
            // Fix Settings Panel
            GameObject canvas = GameObject.Find("Canvas");
            if (canvas != null)
            {
                Transform existingSettings = canvas.transform.Find("SettingsPanel");
                if (existingSettings == null)
                {
                    GameObject settingsPanel = new GameObject("SettingsPanel");
                    settingsPanel.transform.SetParent(canvas.transform, false);
                    settingsPanel.AddComponent<RectTransform>();
                    settingsPanel.AddComponent<SettingsPanelUI>();
                    settingsPanel.SetActive(false);
                    so.FindProperty("settingsPanel").objectReferenceValue = settingsPanel;
                }
            }

            so.ApplyModifiedProperties();
            Debug.Log("Title Screen wiring updated.");
        }

        private void EnsureManager<T>(string name) where T : MonoBehaviour
        {
            if (Object.FindAnyObjectByType<T>() == null)
            {
                GameObject obj = new GameObject(name);
                obj.AddComponent<T>();
                Undo.RegisterCreatedObjectUndo(obj, "Create " + name);
            }
        }
    }
}
