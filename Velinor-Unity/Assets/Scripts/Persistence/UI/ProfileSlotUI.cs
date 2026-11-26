using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace Velinor.Persistence.UI
{
    public class ProfileSlotUI : MonoBehaviour
    {
        [SerializeField] private int slotIndex;
        [SerializeField] private TextMeshProUGUI nameText;
        [SerializeField] private TextMeshProUGUI infoText;
        [SerializeField] private GameObject emptyState;
        [SerializeField] private GameObject occupiedState;

        private ProfileData data;

        public void Setup(int index, ProfileData profileData)
        {
            slotIndex = index;
            data = profileData;

            if (data == null)
            {
                emptyState.SetActive(true);
                occupiedState.SetActive(false);
            }
            else
            {
                emptyState.SetActive(false);
                occupiedState.SetActive(true);
                nameText.text = data.displayName;
                infoText.text = data.gameStarted ? $"{data.lastSavedScene}" : "New Game Pending";
            }
        }

        public void OnSlotClicked()
        {
            if (data == null)
            {
                // Open creation
                Object.FindAnyObjectByType<TitleScreenManager>().ConfirmProfileCreation(); // Simple auto-create for now or wire to Entry
            }
            else
            {
                // Activate
                ProfileManager.Instance.SetActiveProfile(slotIndex);
                Object.FindAnyObjectByType<TitleScreenManager>().RefreshMenuState();
            }
        }
    }
}
