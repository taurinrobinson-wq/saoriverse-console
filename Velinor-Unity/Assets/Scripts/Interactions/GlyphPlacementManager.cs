using UnityEngine;
using TMPro;
using System.Collections;
using System.Collections.Generic;
using UnityEngine.UI;
using Velinor.Core;

/// <summary>
/// Manages the complete glyph placement workflow.
/// Tracks selected glyphs, shows placement slots, handles door activation sequence.
/// </summary>
public class GlyphPlacementManager : MonoBehaviour
{
    [SerializeField] private GameObject screenRumbleOverlay;
    [SerializeField] private GameObject sealedOverlay;
    [SerializeField] private GameObject unsealedOverlay;
    [SerializeField] private GameObject doorAnimationController;
    [SerializeField] private TextMeshProUGUI statusMessage; // "Door Activated Stand Clear"
    [SerializeField] private TextMeshProUGUI placementPrompt; // "Press E to place selected glyphs"
    [SerializeField] private GameObject triglyphPanelUI; // The panel container
    [SerializeField] private GameObject codexUI; // The codex panel

    // Placement slot references (for visual feedback when glyphs are placed)
    [SerializeField] private Image glyphSlot_Sorrow;
    [SerializeField] private Image glyphSlot_Remembrance;
    [SerializeField] private Image glyphSlot_Legacy;

    private List<GlyphSelectable> selectedGlyphs = new List<GlyphSelectable>();
    private GlyphSelectable currentSelectedGlyph = null;
    private const int GLYPHS_NEEDED = 3;

    private void Update()
    {
        // If we have glyphs selected and can place, show prompt and handle E key
        if (selectedGlyphs.Count > 0 && selectedGlyphs.Count < GLYPHS_NEEDED && Input.GetKeyDown(KeyCode.E))
        {
            PlaceSelectedGlyph();
        }
    }

    /// <summary>
    /// Called when a glyph is clicked/selected in the codex
    /// </summary>
    public void SelectGlyph(string glyphName, GlyphSelectable glyph)
    {
        // Don't allow duplicates
        foreach (var g in selectedGlyphs)
        {
            if (g.GlyphName == glyphName)
            {
                Debug.Log($"Glyph {glyphName} already selected!");
                return;
            }
        }

        currentSelectedGlyph = glyph;

        // Show placement prompt
        if (placementPrompt != null)
            placementPrompt.text = $"Press E to place {glyphName}";

        Debug.Log($"Selected: {glyphName}. Total selected: {selectedGlyphs.Count + 1}");
    }

    /// <summary>
    /// Called when E is pressed to place the selected glyph
    /// </summary>
    private void PlaceSelectedGlyph()
    {
        if (currentSelectedGlyph == null)
            return;

        selectedGlyphs.Add(currentSelectedGlyph);
        string glyphName = currentSelectedGlyph.GlyphName;

        Debug.Log($"Placing: {glyphName}. Count: {selectedGlyphs.Count}/{GLYPHS_NEEDED}");

        // Show visual feedback in the placement slots
        if (glyphName.Contains("Sorrow") && glyphSlot_Sorrow != null)
        {
            glyphSlot_Sorrow.enabled = true;
        }
        else if (glyphName.Contains("Remembrance") && glyphSlot_Remembrance != null)
        {
            glyphSlot_Remembrance.enabled = true;
        }
        else if (glyphName.Contains("Legacy") && glyphSlot_Legacy != null)
        {
            glyphSlot_Legacy.enabled = true;
        }

        // Clear prompt
        if (placementPrompt != null)
            placementPrompt.text = "";

        currentSelectedGlyph = null;

        // If all 3 glyphs are placed, trigger the door opening
        if (selectedGlyphs.Count >= GLYPHS_NEEDED)
        {
            StartCoroutine(TriggerDoorOpening());
        }
    }

    /// <summary>
    /// Full sequence: message -> rumble -> overlay transition -> door animation
    /// </summary>
    private IEnumerator TriggerDoorOpening()
    {
        // Show status message
        if (statusMessage != null)
        {
            statusMessage.text = "Door Activated\nStand Clear";
            statusMessage.enabled = true;
        }

        yield return new WaitForSeconds(2f);

        // Close the panels
        if (triglyphPanelUI != null)
            triglyphPanelUI.SetActive(false);

        if (codexUI != null)
            codexUI.SetActive(false);

        // Activate screen rumble
        if (screenRumbleOverlay != null)
            screenRumbleOverlay.SetActive(true);

        yield return new WaitForSeconds(1.5f);

        // Transition overlays
        if (sealedOverlay != null)
            sealedOverlay.SetActive(false);

        if (unsealedOverlay != null)
            unsealedOverlay.SetActive(true);

        // Deactivate rumble
        if (screenRumbleOverlay != null)
            screenRumbleOverlay.SetActive(false);

        // Hide status message
        if (statusMessage != null)
            statusMessage.enabled = false;

        // Trigger door animation
        if (doorAnimationController != null)
        {
            DoorAnimationController doorAnim = doorAnimationController.GetComponent<DoorAnimationController>();
            if (doorAnim != null)
                doorAnim.OpenDoor();
        }
    }

    public void ResetPlacement()
    {
        selectedGlyphs.Clear();
        currentSelectedGlyph = null;

        // Hide slot visuals
        if (glyphSlot_Sorrow != null)
            glyphSlot_Sorrow.enabled = false;
        if (glyphSlot_Remembrance != null)
            glyphSlot_Remembrance.enabled = false;
        if (glyphSlot_Legacy != null)
            glyphSlot_Legacy.enabled = false;

        if (placementPrompt != null)
            placementPrompt.text = "";
        if (statusMessage != null)
            statusMessage.enabled = false;
    }

    /// <summary>
    /// Called when a TriglyphSlot is clicked.
    /// Places the currently selected glyph from CodexController into the slot.
    /// </summary>
    public void OnTriglyphSlotClicked(TriglyphSlot slot)
    {
        if (slot == null)
        {
            Debug.LogError("[GlyphPlacementManager] TriglyphSlot is null!");
            return;
        }

        // Get the currently selected glyph from CodexController
        CodexController codexController = FindAnyObjectByType<CodexController>();
        if (codexController == null)
        {
            Debug.LogError("[GlyphPlacementManager] CodexController not found!");
            return;
        }

        // Note: Need to access selectedGlyph from CodexController
        // For now, this is a placeholder - will need to expose selectedGlyph as public property
        Debug.Log($"[GlyphPlacementManager] Triglyph slot clicked at slot {slot.slotIndex}");
    }
}
