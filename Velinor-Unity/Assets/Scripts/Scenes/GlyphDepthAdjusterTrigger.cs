using UnityEngine;
using System.Collections.Generic;

/// <summary>
/// GlyphDepthAdjusterTrigger: Extension to DialogueTransitionFade.
/// 
/// Automatically finds all GlyphDepthAdjuster components in the scene
/// and notifies them when fade transitions occur.
/// 
/// This allows glyphs to dynamically adjust their Z-position during
/// transitions without explicit scene scripting.
/// 
/// Attach this to the same GameObject as DialogueTransitionFade.
/// </summary>
public class GlyphDepthAdjusterTrigger : MonoBehaviour
{
    private DialogueTransitionFade fadeController;
    private List<GlyphDepthAdjuster> glyphAdjusters = new List<GlyphDepthAdjuster>();
    private bool hasInitialized = false;

    private void OnEnable()
    {
        if (!hasInitialized)
        {
            InitializeAdjusters();
            hasInitialized = true;
        }
    }

    /// <summary>
    /// Find all GlyphDepthAdjuster components in the scene
    /// </summary>
    private void InitializeAdjusters()
    {
        glyphAdjusters.Clear();
        glyphAdjusters.AddRange(FindObjectsByType<GlyphDepthAdjuster>());
        
        Debug.Log($"[GlyphDepthAdjusterTrigger] Found {glyphAdjusters.Count} GlyphDepthAdjuster components");
        
        foreach (var adjuster in glyphAdjusters)
        {
            Debug.Log($"  - {adjuster.gameObject.name}");
        }
    }

    /// <summary>
    /// Call this when a fade transition starts (screen goes black)
    /// </summary>
    public void OnTransitionStarted()
    {
        foreach (var adjuster in glyphAdjusters)
        {
            adjuster.OnTransitionStart();
        }
    }

    /// <summary>
    /// Call this when a fade transition completes (screen fades back in)
    /// </summary>
    public void OnTransitionCompleted()
    {
        foreach (var adjuster in glyphAdjusters)
        {
            adjuster.OnTransitionComplete();
        }
    }

    /// <summary>
    /// Move all glyphs to background depth
    /// </summary>
    public void MoveAllToBackground()
    {
        foreach (var adjuster in glyphAdjusters)
        {
            adjuster.MoveToBackground();
        }
    }

    /// <summary>
    /// Move all glyphs to interaction depth
    /// </summary>
    public void MoveAllToInteraction()
    {
        foreach (var adjuster in glyphAdjusters)
        {
            adjuster.MoveToInteraction();
        }
    }

    /// <summary>
    /// Move specific glyph to interaction depth by name
    /// </summary>
    public void MoveGlyphToInteraction(string glyphName)
    {
        foreach (var adjuster in glyphAdjusters)
        {
            if (adjuster.gameObject.name.Contains(glyphName))
            {
                adjuster.MoveToInteraction();
                Debug.Log($"[GlyphDepthAdjusterTrigger] Moved {glyphName} to interaction depth");
                return;
            }
        }
        
        Debug.LogWarning($"[GlyphDepthAdjusterTrigger] Glyph {glyphName} not found");
    }

    /// <summary>
    /// Move specific glyph to background depth by name
    /// </summary>
    public void MoveGlyphToBackground(string glyphName)
    {
        foreach (var adjuster in glyphAdjusters)
        {
            if (adjuster.gameObject.name.Contains(glyphName))
            {
                adjuster.MoveToBackground();
                Debug.Log($"[GlyphDepthAdjusterTrigger] Moved {glyphName} to background depth");
                return;
            }
        }
        
        Debug.LogWarning($"[GlyphDepthAdjusterTrigger] Glyph {glyphName} not found");
    }
}
