using UnityEngine;

/// <summary>
/// Handles glyph panel interaction and door activation.
/// Player presses E to activate glyphs, which unlocks doors/chambers.
/// </summary>
public class GlyphPanel : MonoBehaviour
{
    [Header("Door Link")]
    [SerializeField] private DoorController linkedDoor;

    [Header("VFX")]
    [SerializeField] private GlyphVFX glyphVFX;

    private bool playerInside = false;

    private void OnTriggerEnter2D(Collider2D other)
    {
        if (other.CompareTag("Player"))
            playerInside = true;
    }

    private void OnTriggerExit2D(Collider2D other)
    {
        if (other.CompareTag("Player"))
            playerInside = false;
    }

    private void Update()
    {
        if (playerInside && Input.GetKeyDown(KeyCode.E))
        {
            ActivateGlyph();
        }
    }

    private void ActivateGlyph()
    {
        Debug.Log("[GlyphPanel] Glyph activated!");

        // Play VFX
        if (glyphVFX != null)
            glyphVFX.PlayVFX();

        // Open the linked door
        if (linkedDoor != null)
            linkedDoor.OpenDoor();
    }
}
