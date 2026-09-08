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
        [SerializeField] private Image _iconImage;
        [SerializeField] private TextMeshProUGUI nameText;
        [SerializeField] private GameObject glowHighlight;
        [SerializeField] private Button button;

        public GlyphData glyphData { get; private set; }
        public bool isCollected { get; set; }
        public Image iconImage => _iconImage;
        public GameObject glowHighlightChild => glowHighlight;

        private void Start()
        {
            if (button != null)
            {
                button.onClick.AddListener(OnButtonClicked);
            }
        }

        private void OnEnable()
        {
            Debug.Log($"[GlyphUI] {gameObject.name} OnEnable - now visible");
        }

        private void OnDisable()
        {
            Debug.LogWarning($"[GlyphUI] {gameObject.name} OnDisable - BEING HIDDEN!");
            Debug.LogWarning($"[GlyphUI] Stack trace: {System.Environment.StackTrace}");
        }

        /// <summary>
        /// Initialize this glyph UI with glyph data.
        /// </summary>
        public void Initialize(GlyphData data)
        {
            glyphData = data;

            if (_iconImage != null && data.icon != null)
            {
                _iconImage.sprite = data.icon;
            }
            else if (_iconImage == null)
            {
                Debug.LogWarning($"[GlyphUI] _iconImage is not assigned on {gameObject.name}!");
            }
            else if (data.icon == null)
            {
                Debug.LogWarning($"[GlyphUI] GlyphData {data.glyphName} has no icon sprite assigned!");
            }

            if (nameText != null)
            {
                nameText.text = data.glyphName;
            }

            if (glowHighlight != null)
            {
                glowHighlight.SetActive(false);
                Debug.Log($"[GlyphUI] {data.glyphName} - glowHighlight FOUND and deactivated");
            }
            else
            {
                Debug.LogError($"[GlyphUI] {data.glyphName} - glowHighlight IS NULL! Not assigned in Inspector!");
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

                // Ensure the Image component is enabled
                Image highlightImage = glowHighlight.GetComponent<Image>();
                if (highlightImage != null)
                {
                    highlightImage.enabled = true;
                    highlightImage.color = new Color(1f, 1f, 0f, 0.5f);
                    Debug.Log($"[GlyphUI] {glyphData.glyphName} selected - highlight activated");
                }
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

                // Also disable the Image component to be thorough
                Image highlightImage = glowHighlight.GetComponent<Image>();
                if (highlightImage != null)
                {
                    highlightImage.enabled = false;
                    Debug.Log($"[GlyphUI] {glyphData.glyphName} deselected - glowHighlight + Image DEACTIVATED");
                }
            }
            else
            {
                Debug.LogWarning($"[GlyphUI] {glyphData.glyphName} deselected but glowHighlight is NULL!");
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
