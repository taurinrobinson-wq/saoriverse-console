using UnityEngine;
using System.Collections.Generic;

namespace Velinor.Persistence.UI
{
    public class ProfileManagementPanel : MonoBehaviour
    {
        [SerializeField] private List<ProfileSlotUI> slots;
        [SerializeField] private GameObject entryPanel;
        [SerializeField] private GameObject overwritePanel;

        private void OnEnable()
        {
            RefreshSlots();
        }

        public void RefreshSlots()
        {
            if (slots == null) return;
            for (int i = 0; i < slots.Count; i++)
            {
                if (slots[i] != null)
                {
                    slots[i].Setup(i, ProfileManager.Instance.GetSlot(i));
                }
            }
        }
    }
}
