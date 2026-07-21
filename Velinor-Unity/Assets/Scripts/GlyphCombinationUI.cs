/*
 * ============================================================
 * PROPRIETARY & CONFIDENTIAL
 * 
 * © 2026 Tauri Robinson. All rights reserved.
 * This code is proprietary and may not be redistributed,
 * modified, or used without explicit written permission.
 * 
 * Unauthorized access, modification, or distribution is prohibited.
 * See LICENSE_COMMERCIAL.md and NDA_TEMPLATE.md for details.
 * ============================================================
 */

using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// UI overlay for multi-glyph puzzle combinations.
/// Shows player progress through glyph sequences with visual feedback.
/// Displays correct/incorrect glyph slots.
/// </summary>
public class GlyphCombinationUI : MonoBehaviour
{
    [Header("UI Elements")]
    [SerializeField] private Image[] glyphSlots;        // UI slots for glyphs
    [SerializeField] private Sprite emptySlotSprite;
    [SerializeField] private Sprite correctGlyphSprite;
    [SerializeField] private Sprite wrongGlyphSprite;

    [Header("Visual Feedback")]
    [SerializeField] private Color correctColor = Color.green;
    [SerializeField] private Color wrongColor = Color.red;
    [SerializeField] private Color neutralColor = Color.white;

    [Header("Animation")]
    [SerializeField] private float feedbackDuration = 0.5f;

    public void UpdateGlyphSlot(int index, bool correct)
    {
        if (index < 0 || index >= glyphSlots.Length)
        {
            Debug.LogWarning($"[GlyphCombinationUI] Invalid slot index: {index}");
            return;
        }

        Image slot = glyphSlots[index];
        slot.sprite = correct ? correctGlyphSprite : wrongGlyphSprite;
        slot.color = correct ? correctColor : wrongColor;

        Debug.Log($"[GlyphCombinationUI] Slot {index}: {(correct ? "CORRECT" : "WRONG")}");
    }

    public void ResetUI()
    {
        foreach (var slot in glyphSlots)
        {
            slot.sprite = emptySlotSprite;
            slot.color = neutralColor;
        }

        Debug.Log("[GlyphCombinationUI] UI reset");
    }

    public void SetSlotActive(int index, bool active)
    {
        if (index < 0 || index >= glyphSlots.Length) return;

        glyphSlots[index].enabled = active;
    }

    public void SetAllSlotsActive(bool active)
    {
        foreach (var slot in glyphSlots)
            slot.enabled = active;
    }
}
