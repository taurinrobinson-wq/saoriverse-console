using UnityEngine;
using UnityEngine.UI;
using Velinor.Core;

/// <summary>
/// Allows testing of glyph collection and placement by toggling glyphs on/off.
/// This is a development/testing tool to verify codex and triglyph mechanics.
/// </summary>
public class GlyphTestingController : MonoBehaviour
{
    [Header("Testing Toggles")]
    [SerializeField] public Toggle sorrowToggle;
    [SerializeField] public Toggle remembranceToggle;
    [SerializeField] public Toggle legacyToggle;

    [Header("Glyph Data")]
    [SerializeField] public GlyphData sorrowData;
    [SerializeField] public GlyphData remembranceData;
    [SerializeField] public GlyphData legacyData;

    [Header("Controllers")]
    [SerializeField] public CodexController codexController;

    private void Start()
    {
        // Find CodexController if not assigned
        if (codexController == null)
        {
            codexController = FindAnyObjectByType<CodexController>();
            if (codexController == null)
            {
                Debug.LogError("[GlyphTestingController] CodexController not found!");
                return;
            }
        }

        // Add listeners to toggles
        if (sorrowToggle != null)
            sorrowToggle.onValueChanged.AddListener(OnSorrowToggled);

        if (remembranceToggle != null)
            remembranceToggle.onValueChanged.AddListener(OnRemembranceToggled);

        if (legacyToggle != null)
            legacyToggle.onValueChanged.AddListener(OnLegacyToggled);

        Debug.Log("[GlyphTestingController] Initialized with testing toggles");
    }

    private void OnSorrowToggled(bool isOn)
    {
        if (sorrowData == null)
        {
            Debug.LogError("[GlyphTestingController] Sorrow glyph data not assigned!");
            return;
        }

        if (isOn)
        {
            Debug.Log("[GlyphTestingController] Adding Sorrow glyph");
            codexController.AddGlyph(sorrowData);
        }
        else
        {
            Debug.Log("[GlyphTestingController] Removing Sorrow glyph");
            codexController.RemoveGlyph(sorrowData);
        }
    }

    private void OnRemembranceToggled(bool isOn)
    {
        if (remembranceData == null)
        {
            Debug.LogError("[GlyphTestingController] Remembrance glyph data not assigned!");
            return;
        }

        if (isOn)
        {
            Debug.Log("[GlyphTestingController] Adding Remembrance glyph");
            codexController.AddGlyph(remembranceData);
        }
        else
        {
            Debug.Log("[GlyphTestingController] Removing Remembrance glyph");
            codexController.RemoveGlyph(remembranceData);
        }
    }

    private void OnLegacyToggled(bool isOn)
    {
        if (legacyData == null)
        {
            Debug.LogError("[GlyphTestingController] Legacy glyph data not assigned!");
            return;
        }

        if (isOn)
        {
            Debug.Log("[GlyphTestingController] Adding Legacy glyph");
            codexController.AddGlyph(legacyData);
        }
        else
        {
            Debug.Log("[GlyphTestingController] Removing Legacy glyph");
            codexController.RemoveGlyph(legacyData);
        }
    }

    private void OnDestroy()
    {
        if (sorrowToggle != null)
            sorrowToggle.onValueChanged.RemoveListener(OnSorrowToggled);

        if (remembranceToggle != null)
            remembranceToggle.onValueChanged.RemoveListener(OnRemembranceToggled);

        if (legacyToggle != null)
            legacyToggle.onValueChanged.RemoveListener(OnLegacyToggled);
    }
}
