using UnityEngine;
using Velinor.Core;

/// <summary>
/// Represents a glyph collectible in the game world.
/// When the player touches it, the glyph is added to the codex.
/// Persists across scene loads via GameFlags.
/// </summary>
public class GlyphPickup : MonoBehaviour
{
    [SerializeField] private GlyphData glyphData;
    [SerializeField] private bool hasBeenCollected = false;
    private string glyphCollectionFlag = ""; // Set based on glyphData

    private void Start()
    {
        // Create flag name based on glyph data
        if (glyphData != null)
        {
            glyphCollectionFlag = $"glyph_collected_{glyphData.glyphName.ToLower()}";
        }
        else
        {
            glyphCollectionFlag = $"glyph_collected_{gameObject.name.ToLower()}";
        }

        // Check if already collected via persistent GameFlags
        if (GameFlags.Get(glyphCollectionFlag))
        {
            hasBeenCollected = true;
            Debug.Log($"[GlyphPickup] {gameObject.name} already collected, disabling.");
            // Disable visual and collider
            Transform visualContainer = transform.Find("Visuals");
            if (visualContainer != null) visualContainer.gameObject.SetActive(false);
            Collider col = GetComponent<Collider>();
            if (col != null) col.enabled = false;
            return;
        }

        // Ensure GlyphVisualEffect is attached to the Core mesh
        Transform coreTransform = transform.Find("Core");
        if (coreTransform != null && coreTransform.GetComponent<GlyphVisualEffect>() == null)
        {
            coreTransform.gameObject.AddComponent<GlyphVisualEffect>();
            Debug.Log($"[GlyphPickup] Added GlyphVisualEffect to {coreTransform.gameObject.name}");
        }
    }

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

    [SerializeField] private GameObject visualContainer;
    [SerializeField] private ParticleSystem collectionEffect;
    [SerializeField] private float destroyDelay = 1.0f;

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
            
            // PERSIST: Mark glyph as collected globally so it doesn't respawn
            GameFlags.Set(glyphCollectionFlag, true);
            Debug.Log($"[GlyphPickup] Flag set: {glyphCollectionFlag} = true");

            // Visual feedback
            if (visualContainer != null) visualContainer.SetActive(false);
            if (collectionEffect != null) collectionEffect.Play();
            
            // Disable collider so it doesn't trigger twice
            Collider col = GetComponent<Collider>();
            if (col != null) col.enabled = false;

            // CRITICAL: If this glyph has an associated NPC with secondary dialogue,
            // trigger it now. This enables multi-part encounters (e.g., Willy glyph).
            // The NPC should have secondaryDialogueJson assigned in the inspector.
            NPCDialogueDriver npcDriver = FindAnyObjectByType<NPCDialogueDriver>();
            if (npcDriver != null && glyphData.glyphName == "Sorrow")
            {
                // Check if Willy NPC has secondary dialogue
                if (npcDriver.gameObject.name.Contains("Willy") || npcDriver.gameObject.name.Contains("willy"))
                {
                    Debug.Log("[GlyphPickup] Triggering Willy secondary dialogue after glyph collection");
                    npcDriver.TriggerSecondaryDialogue();
                }
            }

            // Destroy after delay
            Destroy(gameObject, destroyDelay);
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