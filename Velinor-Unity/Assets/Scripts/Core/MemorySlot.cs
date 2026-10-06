using UnityEngine;
using UnityEngine.UI;
using Velinor.Core;
using Velinor.UI.Codex;

namespace Velinor.Core
{
    /// <summary>
    /// Represents a slot in the Mind Log grid where a memory fragment can be displayed.
    /// Mirrors the GlyphSlot system for consistency.
    /// </summary>
    public class MemorySlot : MonoBehaviour
    {
        [SerializeField] private Image slotImage;
        [SerializeField] private Button button;
        [SerializeField] private Color emptySlotColor = new Color(0.3f, 0.3f, 0.3f, 0.5f);
        [SerializeField] private Color selectedColor = new Color(1f, 1f, 0.5f, 1f); // Yellow-tinted for selection

        private MemoryFragment memoryFragment;
        private bool isFilled;
        private bool isSelected;
        private float lastClickTime = -1f;
        private const float DOUBLE_CLICK_THRESHOLD = 0.3f;

        public bool IsFilled => isFilled;
        public MemoryFragment MemoryFragment => memoryFragment;
        public bool IsSelected => isSelected;

        private void Start()
        {
            // Auto-find Image if not assigned
            if (slotImage == null)
            {
                slotImage = GetComponent<Image>();
                if (slotImage == null)
                {
                    Debug.LogWarning($"[MemorySlot] No Image component found on {gameObject.name}!");
                }
            }

            // Auto-find or create Button if not assigned
            if (button == null)
            {
                button = GetComponent<Button>();
                if (button == null)
                {
                    button = gameObject.AddComponent<Button>();
                    Debug.Log($"[MemorySlot] Created Button component on {gameObject.name}");
                }
            }

            if (button != null)
            {
                button.onClick.AddListener(OnSlotClicked);
            }

            // Initialize slot as empty
            Clear();
        }

        /// <summary>
        /// Place a memory fragment in this slot.
        /// </summary>
        public void SetMemory(MemoryFragment fragment)
        {
            if (fragment == null)
            {
                Clear();
                return;
            }

            memoryFragment = fragment;
            isFilled = true;

            // Set the slot image to the memory's icon
            if (slotImage != null && fragment.icon != null)
            {
                slotImage.sprite = fragment.icon;
                slotImage.color = Color.white;
            }

            Debug.Log($"[MemorySlot] Set memory '{fragment.fragmentID}' in slot {gameObject.name}");
        }

        /// <summary>
        /// Clear the memory from this slot.
        /// </summary>
        public void Clear()
        {
            memoryFragment = null;
            isFilled = false;

            if (slotImage != null)
            {
                slotImage.sprite = null;
                slotImage.color = emptySlotColor;
            }

            Debug.Log("[MemorySlot] Cleared");
        }

        private void OnSlotClicked()
        {
            if (!isFilled)
            {
                Debug.Log("[MemorySlot] Clicked on empty slot, ignoring");
                return;
            }

            // Detect double-click
            float currentTime = Time.unscaledTime;
            bool isDoubleClick = (currentTime - lastClickTime) <= DOUBLE_CLICK_THRESHOLD;
            lastClickTime = currentTime;

            if (isDoubleClick)
            {
                OnMemoryDoubleClicked();
            }
            else
            {
                OnMemorySingleClicked();
            }
        }

        private void OnMemorySingleClicked()
        {
            Debug.Log($"[MemorySlot] Single-clicked memory '{memoryFragment.fragmentID}'");
            
            // Toggle selection
            if (isSelected)
            {
                Unhighlight();
            }
            else
            {
                Highlight();
            }

            // Update the synopsis text display
            var memoryGridController = FindAnyObjectByType<MemoryGridController>();
            if (memoryGridController != null)
            {
                memoryGridController.OnMemorySingleClicked(this, memoryFragment);
            }
        }

        private void OnMemoryDoubleClicked()
        {
            Debug.Log($"[MemorySlot] Double-clicked memory '{memoryFragment.fragmentID}' - opening expanded view");
            
            // Ensure it's selected first
            if (!isSelected)
            {
                Highlight();
            }

            var memoryGridController = FindAnyObjectByType<MemoryGridController>();
            if (memoryGridController != null)
            {
                Debug.Log("[MemorySlot] Found MemoryGridController, calling OnMemoryDoubleClicked");
                memoryGridController.OnMemoryDoubleClicked(this, memoryFragment);
            }
            else
            {
                Debug.LogError("[MemorySlot] MemoryGridController NOT FOUND! Did you add the MemoryGridController script to a GameObject?");
            }
        }

        /// <summary>
        /// Highlight this slot to show it's selected.
        /// </summary>
        public void Highlight()
        {
            isSelected = true;
            if (slotImage != null && isFilled)
            {
                slotImage.color = selectedColor;
                Debug.Log($"[MemorySlot] {gameObject.name} highlighted");
            }
        }

        /// <summary>
        /// Remove highlight from this slot.
        /// </summary>
        public void Unhighlight()
        {
            isSelected = false;
            if (slotImage != null)
            {
                if (isFilled)
                {
                    slotImage.color = Color.white;
                    Debug.Log($"[MemorySlot] {gameObject.name} unhighlighted - restored to white");
                }
                else
                {
                    slotImage.color = emptySlotColor;
                    Debug.Log($"[MemorySlot] {gameObject.name} unhighlighted - restored to empty color");
                }
            }
        }

        private void OnDestroy()
        {
            if (button != null)
            {
                button.onClick.RemoveListener(OnSlotClicked);
            }
        }
    }
}
