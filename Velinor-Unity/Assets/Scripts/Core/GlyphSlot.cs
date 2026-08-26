using UnityEngine;
using UnityEngine.UI;

namespace Velinor.Core
{
    /// <summary>
    /// Represents a slot in the codex grid where a glyph can be placed.
    /// Manages visual representation and interaction.
    /// </summary>
    public class GlyphSlot : MonoBehaviour
    {
        [SerializeField] private Image slotImage;
        [SerializeField] private Button button;
        [SerializeField] private Color emptySlotColor = new Color(0.3f, 0.3f, 0.3f, 0.5f);
        [SerializeField] private Color selectedColor = new Color(1f, 1f, 0.5f, 1f); // Yellow-tinted for selection
        [SerializeField] private Color highlightColor = new Color(1.2f, 1.2f, 1.2f, 1f); // Brightened

        public bool isFilled { get; private set; }
        public GlyphUI glyphUI { get; private set; }
        public bool isSelected { get; private set; }

        private void Start()
        {
            // Auto-find Image if not assigned
            if (slotImage == null)
            {
                slotImage = GetComponent<Image>();
                if (slotImage == null)
                {
                    Debug.LogWarning($"[GlyphSlot] No Image component found on {gameObject.name}!");
                }
            }

            // Auto-find or create Button if not assigned
            if (button == null)
            {
                button = GetComponent<Button>();
                if (button == null)
                {
                    button = gameObject.AddComponent<Button>();
                    Debug.Log($"[GlyphSlot] Created Button component on {gameObject.name}");
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
        /// Place a glyph in this slot.
        /// </summary>
        public void SetGlyph(GlyphUI glyph)
        {
            if (glyph == null)
            {
                Clear();
                return;
            }

            glyphUI = glyph;
            isFilled = true;

            if (slotImage != null && glyph.iconImage != null)
            {
                slotImage.sprite = glyph.iconImage.sprite;
                slotImage.color = Color.white;
            }

            Debug.Log($"[GlyphSlot] Set glyph {glyph.glyphData.glyphName}");
        }

        /// <summary>
        /// Clear the glyph from this slot.
        /// </summary>
        public void Clear()
        {
            glyphUI = null;
            isFilled = false;

            if (slotImage != null)
            {
                slotImage.sprite = null;
                slotImage.color = emptySlotColor;
            }

            Debug.Log("[GlyphSlot] Cleared");
        }

        private void OnSlotClicked()
        {
            Debug.Log("[GlyphSlot] Slot clicked");

            var codexController = FindAnyObjectByType<CodexController>();
            if (codexController != null)
            {
                codexController.OnSlotClicked(this);
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
                Debug.Log($"[GlyphSlot] {gameObject.name} highlighted");
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
                    Debug.Log($"[GlyphSlot] {gameObject.name} unhighlighted - restored to white");
                }
                else
                {
                    slotImage.color = emptySlotColor;
                    Debug.Log($"[GlyphSlot] {gameObject.name} unhighlighted - restored to empty color");
                }
            }
            else
            {
                Debug.LogWarning($"[GlyphSlot] {gameObject.name} - slotImage is null in Unhighlight!");
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
