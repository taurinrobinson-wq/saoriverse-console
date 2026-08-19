using UnityEngine;
using System.Collections;

/// <summary>
/// Manages the placement of glyphs into the panel.
/// Handles the transition from sealed to unsealed overlay with rumble and dust effects.
/// </summary>
public class GlyphPlacementManager : MonoBehaviour
{
    [SerializeField] private GameObject screenRumbleOverlay;
    [SerializeField] private GameObject sealedOverlay;
    [SerializeField] private GameObject unsealedOverlay;
    [SerializeField] private GameObject doorAnimationController;

    private bool readyToPlace = false;
    private GlyphSelectable selectedGlyph = null;
    private int glyphsPlaced = 0;
    private const int GLYPHS_NEEDED = 3;

    private void Update()
    {
        if (readyToPlace && Input.GetKeyDown(KeyCode.E) && selectedGlyph != null)
        {
            StartCoroutine(PlaceGlyph());
        }
    }

    public void SelectGlyph(string glyphName, GlyphSelectable glyph)
    {
        // Deselect previous if any
        if (selectedGlyph != null)
            selectedGlyph.Deselect();

        selectedGlyph = glyph;
        readyToPlace = true;

        Debug.Log($"Glyph selected: {glyphName}");
    }

    private IEnumerator PlaceGlyph()
    {
        readyToPlace = false;
        glyphsPlaced++;

        Debug.Log($"Placing glyph {glyphsPlaced}/{GLYPHS_NEEDED}");

        // If all glyphs placed, trigger the full sequence
        if (glyphsPlaced >= GLYPHS_NEEDED)
        {
            yield return StartCoroutine(TriggerDoorOpening());
        }

        selectedGlyph = null;
    }

    private IEnumerator TriggerDoorOpening()
    {
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

        // Trigger door animation
        if (doorAnimationController != null)
        {
            DoorAnimationController doorAnim = doorAnimationController.GetComponent<DoorAnimationController>();
            if (doorAnim != null)
                doorAnim.OpenDoor();
        }
    }

    public void EnablePlacement()
    {
        readyToPlace = true;
    }

    public void ResetPlacement()
    {
        readyToPlace = false;
        selectedGlyph = null;
        glyphsPlaced = 0;
    }
}
