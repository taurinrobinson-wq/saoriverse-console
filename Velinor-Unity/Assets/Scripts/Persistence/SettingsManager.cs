using UnityEngine;
using System.IO;
using Velinor.Core;

namespace Velinor.Persistence
{
    public class SettingsManager : MonoBehaviour
    {
        public static SettingsManager Instance { get; private set; }

        private string settingsPath;
        private GlobalSettings savedSettings;
        private GlobalSettings workingSettings;
        private GlobalSettings prePreviewSettings;

        public GlobalSettings Working => workingSettings;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            if (transform.parent == null) DontDestroyOnLoad(gameObject);

            settingsPath = Path.Combine(Application.persistentDataPath, "settings.json");
            LoadSettings();
        }

        public void LoadSettings()
        {
            if (File.Exists(settingsPath))
            {
                try
                {
                    string json = File.ReadAllText(settingsPath);
                    savedSettings = JsonUtility.FromJson<GlobalSettings>(json);
                }
                catch (System.Exception e)
                {
                    Debug.LogError($"[SettingsManager] Load Error: {e.Message}");
                    savedSettings = new GlobalSettings();
                }
            }
            else
            {
                savedSettings = new GlobalSettings();
            }

            // Copy to working state
            workingSettings = JsonUtility.FromJson<GlobalSettings>(JsonUtility.ToJson(savedSettings));
            ApplySettings(savedSettings);
        }

        public void SaveSettings()
        {
            if (DevelopmentOverrides.Instance != null && !DevelopmentOverrides.Instance.CanWriteSettings())
            {
                Debug.Log("[SettingsManager] Save suppressed by DevelopmentOverrides.");
                return;
            }

            try
            {
                savedSettings = JsonUtility.FromJson<GlobalSettings>(JsonUtility.ToJson(workingSettings));
                string json = JsonUtility.ToJson(savedSettings, true);
                File.WriteAllText(settingsPath, json);
                Debug.Log("[SettingsManager] Settings saved.");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[SettingsManager] Save Error: {e.Message}");
            }
        }

        public void CancelChanges()
        {
            workingSettings = JsonUtility.FromJson<GlobalSettings>(JsonUtility.ToJson(savedSettings));
            ApplySettings(savedSettings);
        }

        public void ResetToDefaults()
        {
            workingSettings = new GlobalSettings();
            // Don't save yet, just apply working state
            ApplySettings(workingSettings);
        }

        public void ApplySettings(GlobalSettings settings)
        {
            // Apply Audio
            if (AudioManager.Instance != null)
            {
                AudioManager.Instance.SetMusicVolume(settings.musicVolume);
                // Assume SetSfxVolume is added or exists
                // AudioManager.Instance.SetSfxVolume(settings.sfxVolume);
            }

            // Apply Display
            if (Screen.width != settings.resolutionWidth || Screen.height != settings.resolutionHeight || Screen.fullScreen != settings.isFullscreen)
            {
                Screen.SetResolution(settings.resolutionWidth, settings.resolutionHeight, settings.isFullscreen);
            }
        }

        public void PreviewDisplayChange(int width, int height, bool fullscreen)
        {
            prePreviewSettings = JsonUtility.FromJson<GlobalSettings>(JsonUtility.ToJson(workingSettings));
            
            workingSettings.resolutionWidth = width;
            workingSettings.resolutionHeight = height;
            workingSettings.isFullscreen = fullscreen;

            ApplySettings(workingSettings);
        }

        public void KeepDisplayChange()
        {
            prePreviewSettings = null;
            // Working settings already updated
        }

        public void RevertDisplayChange()
        {
            if (prePreviewSettings != null)
            {
                workingSettings = prePreviewSettings;
                ApplySettings(workingSettings);
                prePreviewSettings = null;
            }
        }

        public void SetMusicVolume(float volume)
        {
            workingSettings.musicVolume = volume;
            if (AudioManager.Instance != null) AudioManager.Instance.SetMusicVolume(volume);
        }

        public void SetSfxVolume(float volume)
        {
            workingSettings.sfxVolume = volume;
            // if (AudioManager.Instance != null) AudioManager.Instance.SetSfxVolume(volume);
        }
    }
}
