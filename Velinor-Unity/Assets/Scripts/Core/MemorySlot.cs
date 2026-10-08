using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using Velinor.Core;
using Velinor.UI.Codex;

namespace Velinor.Core
{
    /// <summary>
    /// Represents a slot in the Mind Log grid where a memory fragment can be displayed.
    /// Handles single-click (show summary) and double-click (open expanded view) via eventData.clickCount.
    /// </summary>
    public class MemorySlot : MonoBehaviour, IPointerClickHandler
    {
        [SerializeField] private Image slotImage;
        [SerializeField] private Color emptySlotColor = new Color(0.3f, 0.3f, 0.3f, 0.5f);
        [SerializeField] private Color selectedColor = new Color(1f, 1f, 0.5f, 1f); // Yellow-tinted for selection

        private MemoryFragment memoryFragment;
        private bool isFilled;
        private bool isSelected;
        
        // Double-click detection: Manual timing with Invoke()
        private float doubleClickInterval = 0.25f;
        private bool isSingleClickPending = false;

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
                    return;
                }
            }

            // CRITICAL: Ensure the Image component is properly configured for rendering
            if (slotImage != null)
            {
                // Make sure the Image component itself is enabled
                if (!slotImage.enabled)
                {
                    slotImage.enabled = true;
                    Debug.Log($"[MemorySlot] Enabled Image component on {gameObject.name}");
                }

                // Ensure the Image Type is set to "Simple" for basic rendering
                if (slotImage.type != Image.Type.Simple)
                {
                    slotImage.type = Image.Type.Simple;
                    Debug.Log($"[MemorySlot] Set Image Type to Simple on {gameObject.name}");
                }

                // Ensure raycast target is enabled so the component can receive events
                if (!slotImage.raycastTarget)
                {
                    slotImage.raycastTarget = true;
                    Debug.Log($"[MemorySlot] Enabled Raycast Target on {gameObject.name}");
                }

                // Check for Canvas Group visibility blockers
                CanvasGroup canvasGroup = GetComponent<CanvasGroup>();
                if (canvasGroup != null && canvasGroup.alpha < 1f)
                {
                    Debug.LogWarning($"[MemorySlot] ⚠ Canvas Group on {gameObject.name} has alpha={canvasGroup.alpha} (less than 1), which will make visuals invisible!");
                }

                // Check parent Canvas Group
                CanvasGroup parentCanvasGroup = transform.parent?.GetComponent<CanvasGroup>();
                if (parentCanvasGroup != null && parentCanvasGroup.alpha < 1f)
                {
                    Debug.LogWarning($"[MemorySlot] ⚠ Parent Canvas Group has alpha={parentCanvasGroup.alpha}, which will affect visibility of {gameObject.name}!");
                }

                // Check and log the initial state for debugging
                Debug.Log($"[MemorySlot] {gameObject.name} initialized - Image enabled: {slotImage.enabled}, Type: {slotImage.type}, Raycast: {slotImage.raycastTarget}, Sprite: {(slotImage.sprite != null ? slotImage.sprite.name : "None")}");
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
                
                // CRITICAL: Enable the Image component in case it was disabled
                slotImage.enabled = true;
                
                // Ensure native size is preserved or set to preserve aspect
                if (slotImage.GetComponent<LayoutElement>() == null)
                {
                    slotImage.preserveAspect = true;
                }
                
                Debug.Log($"[MemorySlot] ✓ Set sprite '{fragment.icon.name}' on {gameObject.name}");
                
                // Mark layout for rebuild to ensure UI updates
                LayoutRebuilder.MarkLayoutForRebuild(slotImage.GetComponent<RectTransform>());
                
                // Also check if parent needs layout rebuild
                RectTransform parentRect = slotImage.GetComponent<RectTransform>().parent as RectTransform;
                if (parentRect != null)
                {
                    LayoutRebuilder.MarkLayoutForRebuild(parentRect);
                }
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

        /// <summary>
        /// Handle pointer clicks using manual double-click detection with Invoke().
        /// Single-click: show summary (delayed by doubleClickInterval to wait for potential second click)
        /// Double-click: open expanded view (cancels pending single-click)
        /// </summary>
        public void OnPointerClick(PointerEventData eventData)
        {
            if (!isFilled)
            {
                Debug.Log("[MemorySlot] Clicked on empty slot, ignoring");
                return;
            }

            // Get the CodexViewController to track which slot was last clicked
            var codexViewController = FindAnyObjectByType<CodexViewController>();
            if (codexViewController == null)
            {
                Debug.LogError("[MemorySlot] Could not find CodexViewController!");
                return;
            }

            // If clicking a DIFFERENT slot, cancel any pending double-click on the old slot
            if (codexViewController.LastClickedSlot != this)
            {
                // Cancel pending single-click on the previous slot
                if (codexViewController.LastClickedSlot != null)
                {
                    codexViewController.LastClickedSlot.CancelPendingSingleClick();
                }
                // Update to current slot
                codexViewController.LastClickedSlot = this;
            }

            // If no single-click is pending, start one
            if (!isSingleClickPending)
            {
                isSingleClickPending = true;
                Invoke(nameof(ExecuteSingleClick), doubleClickInterval);
            }
            else
            {
                // Second click within the interval = double-click
                CancelPendingSingleClick();
                OnMemoryDoubleClicked();
            }
        }

        private void ExecuteSingleClick()
        {
            isSingleClickPending = false;
            OnMemorySingleClicked();
        }

        private void CancelPendingSingleClick()
        {
            if (isSingleClickPending)
            {
                CancelInvoke(nameof(ExecuteSingleClick));
                isSingleClickPending = false;
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
            CancelPendingSingleClick();
        }
    }
}
