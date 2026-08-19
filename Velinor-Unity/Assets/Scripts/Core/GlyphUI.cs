using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace Velinor.Core
{
    /// <summary>
    /// Represents a single glyph in the codex UI.
    /// Shows glyph icon, name, and selection highlight.
    /// </summary>
    public class GlyphUI : MonoBehaviour
    {
        [SerializeField] private Image iconImage;
        [SerializeField] private TextMeshProUGUI nameText;
        [SerializeField] private GameObject glowHighlight;
        [SerializeField] private Button button;

        public GlyphData glyphData { get; private set; }
        public bool isCollected { get; set; }

        private void Start()
        {
            if (button != null)
            {
                button.onClick.AddListener(OnButtonClicked);
            }
        }

        /// <summary>
        /// Initialize this glyph UI with glyph data.
        /// </summary>
        public void Initialize(GlyphData data)
        {
            glyphData = data;

            if (iconImage != null && data.icon != null)
            {
                iconImage.sprite = data.icon;
            }

            if (nameText != null)
            {
                nameText.text = data.glyphName;
            }

            if (glowHighlight != null)
            {
                glowHighlight.SetActive(false);
            }

            isCollected = false;

            Debug.Log($"[GlyphUI] Initialized with {data.glyphName}");
        }

        /// <summary>
        /// Show selection highlight.
        /// </summary>
        public void Select()
        {
            if (glowHighlight != null)
            {
                glowHighlight.SetActive(true);
                Debug.Log($"[GlyphUI] {glyphData.glyphName} selected");
            }
        }

        /// <summary>
        /// Hide selection highlight.
        /// </summary>
        public void Deselect()
        {
            if (glowHighlight != null)
            {
                glowHighlight.SetActive(false);
                Debug.Log($"[GlyphUI] {glyphData.glyphName} deselected");
            }
        }

        private void OnButtonClicked()
        {
            Debug.Log($"[GlyphUI] Button clicked for {glyphData.glyphName}");
            
            // Find and notify CodexController
            var codexController = FindAnyObjectByType<CodexController>();
            if (codexController != null)
            {
                codexController.OnGlyphSelected(this);
            }
        }

        private void OnDestroy()
        {
            if (button != null)
            {
                button.onClick.RemoveListener(OnButtonClicked);
            }
        }
    }
}
