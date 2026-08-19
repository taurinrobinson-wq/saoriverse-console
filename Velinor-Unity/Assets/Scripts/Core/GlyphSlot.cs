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

        public bool isFilled { get; private set; }
        public GlyphUI glyphUI { get; private set; }

        private void Start()
        {
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

        private void OnDestroy()
        {
            if (button != null)
            {
                button.onClick.RemoveListener(OnSlotClicked);
            }
        }
    }
}
