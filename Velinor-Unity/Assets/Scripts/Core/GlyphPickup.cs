using UnityEngine;
using Velinor.Core;

/// <summary>
/// Represents a glyph collectible in the game world.
/// When the player touches it, the glyph is added to the codex.
/// </summary>
public class GlyphPickup : MonoBehaviour
{
    [SerializeField] private GlyphData glyphData;
    [SerializeField] private bool hasBeenCollected = false;

    private void OnTriggerEnter(Collider other)
    {
        Debug.Log($"[GlyphPickup] Collision detected with: {other.gameObject.name}, Tag: {other.tag}");

        // Check if the object that entered has a tag or component indicating it's the player
        if (other.CompareTag("Player") || other.GetComponent<PlayerController>() != null)
        {
            Debug.Log("[GlyphPickup] Player detected! Collecting...");
            CollectGlyph();
        }
        else
        {
            Debug.Log($"[GlyphPickup] Collision with {other.gameObject.name} but not player");
        }
    }

    private void CollectGlyph()
    {
        if (hasBeenCollected)
        {
            return;
        }

        if (glyphData == null)
        {
            Debug.LogError($"[GlyphPickup] {gameObject.name} has no glyph data assigned!");
            return;
        }

        // Find CodexController
        CodexController codex = FindAnyObjectByType<CodexController>();
        if (codex != null)
        {
            codex.AddGlyph(glyphData);
            Debug.Log($"[GlyphPickup] Collected {glyphData.glyphName}");

            hasBeenCollected = true;

            // Destroy the pickup object or disable it visually
            Destroy(gameObject);
        }
        else
        {
            Debug.LogError("[GlyphPickup] CodexController not found in scene!");
        }
    }

    /// <summary>
    /// Public method to forcefully collect this glyph (for testing)
    /// </summary>
    public void ForceCollect()
    {
        CollectGlyph();
    }
}