using UnityEngine;
using UnityEngine.UI;

namespace Velinor.Core
{
    /// <summary>
    /// Represents a slot in the triglyph panel (puzzle solution area).
    /// Allows placement of selected glyphs for puzzle solving.
    /// </summary>
    public class TriglyphSlot : MonoBehaviour
    {
        [SerializeField] private Image slotImage;
        [SerializeField] private Button button;
    [SerializeField] public int slotIndex;  // 0, 1, or 2
        public bool isFilled { get; private set; }
        public GlyphUI placedGlyph { get; private set; }

        private void Start()
        {
            if (button != null)
            {
                button.onClick.AddListener(OnSlotClicked);
            }

            Clear();
        }

        /// <summary>
        /// Place a glyph in this triglyph slot.
        /// </summary>
        public void SetGlyph(GlyphUI glyph)
        {
            if (glyph == null)
            {
                Clear();
                return;
            }

            placedGlyph = glyph;
            isFilled = true;

            if (slotImage != null && glyph.iconImage != null)
            {
                slotImage.sprite = glyph.iconImage.sprite;
                slotImage.color = Color.white;
            }

            Debug.Log($"[TriglyphSlot {slotIndex}] Placed {glyph.glyphData.glyphName}");
        }

        /// <summary>
        /// Clear this triglyph slot.
        /// </summary>
        public void Clear()
        {
            placedGlyph = null;
            isFilled = false;

            if (slotImage != null)
            {
                slotImage.sprite = null;
                slotImage.color = emptySlotColor;
            }

            Debug.Log($"[TriglyphSlot {slotIndex}] Cleared");
        }

        private void OnSlotClicked()
        {
            Debug.Log($"[TriglyphSlot {slotIndex}] Clicked");

            // Get the triglyph controller (or similar system)
            var triglyph = FindAnyObjectByType<GlyphPlacementManager>();
            if (triglyph != null)
            {
                triglyph.OnTriglyphSlotClicked(this);
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
