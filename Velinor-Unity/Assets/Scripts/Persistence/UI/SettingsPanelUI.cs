using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace Velinor.Persistence.UI
{
    public class SettingsPanelUI : MonoBehaviour
    {
        [SerializeField] private Slider musicSlider;
        [SerializeField] private Slider sfxSlider;
        [SerializeField] private TMP_Dropdown resolutionDropdown;
        [SerializeField] private Toggle fullscreenToggle;
        [SerializeField] private Button confirmButton;

        private void OnEnable()
        {
            if (SettingsManager.Instance == null) return;
            
            var working = SettingsManager.Instance.Working;
            if (musicSlider != null) musicSlider.value = working.musicVolume;
            if (sfxSlider != null) sfxSlider.value = working.sfxVolume;
            if (fullscreenToggle != null) fullscreenToggle.isOn = working.isFullscreen;
            
            // Populate and set resolution dropdown
        }

        public void OnMusicChanged(float val)
        {
            SettingsManager.Instance.SetMusicVolume(val);
        }

        public void OnConfirm()
        {
            SettingsManager.Instance.SaveSettings();
        }

        public void OnCancel()
        {
            SettingsManager.Instance.CancelChanges();
        }
    }
}
