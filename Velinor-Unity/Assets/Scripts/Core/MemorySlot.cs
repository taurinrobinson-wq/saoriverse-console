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
        private const float DOUBLE_CLICK_THRESHOLD = 0.25f;
        
        // Track if we're waiting for a potential double-click
        private bool isWaitingForDoubleClick = false;
        private System.Collections.Coroutine doubleClickCoroutine;

        public bool IsFilled => isFilled;
        public MemoryFragment MemoryFragment => memoryFragment;
        public bool IsSelected => isSelected;

        private void OnEnable()
        {
            // Initialize components early, before Start() is called
            // This ensures slotImage and button are ready when PopulateFromManager() is called
            EnsureComponentsInitialized();
        }

        public void EnsureComponentsInitialized()
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

            if (button != null && button.onClick.GetPersistentEventCount() == 0)
            {
                button.onClick.AddListener(OnSlotClicked);
            }
        }

        private void Start()
        {
            // Ensure components are initialized (in case OnEnable didn't run)
            EnsureComponentsInitialized();

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
                Debug.Log($"[MemorySlot] ✓ Set sprite '{fragment.icon.name}' on {gameObject.name}");
            }
            else if (slotImage == null)
            {
                Debug.LogError($"[MemorySlot] ✗ CANNOT SET SPRITE: slotImage is null on {gameObject.name}!");
            }
            else if (fragment.icon == null)
            {
                Debug.LogWarning($"[MemorySlot] ✗ CANNOT SET SPRITE: fragment.icon is null for '{fragment.fragmentID}'");
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

            // If we're already waiting for a double-click, this is the second click
            if (isWaitingForDoubleClick)
            {
                // Cancel the pending single-click coroutine
                if (doubleClickCoroutine != null)
                {
                    StopCoroutine(doubleClickCoroutine);
                    doubleClickCoroutine = null;
                }
                isWaitingForDoubleClick = false;
                
                // This is a double-click
                OnMemoryDoubleClicked();
                return;
            }

            // This is the first click - start waiting for a potential second click
            isWaitingForDoubleClick = true;
            doubleClickCoroutine = StartCoroutine(WaitForSecondClick());
        }

        private System.Collections.IEnumerator WaitForSecondClick()
        {
            // Wait for the double-click threshold time
            yield return new WaitForSeconds(DOUBLE_CLICK_THRESHOLD);

            // If we get here, no second click came in - treat as single click
            isWaitingForDoubleClick = false;
            doubleClickCoroutine = null;
            OnMemorySingleClicked();
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
            // Clean up any pending coroutines
            if (doubleClickCoroutine != null)
            {
                StopCoroutine(doubleClickCoroutine);
                doubleClickCoroutine = null;
            }

            if (button != null)
            {
                button.onClick.RemoveListener(OnSlotClicked);
            }
        }
    }
}
