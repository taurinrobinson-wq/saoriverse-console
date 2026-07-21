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

/// <summary>
/// A single node in a machine network.
/// When powered, triggers all output machines in sequence.
/// Used for chain reactions, puzzle solutions, and chamber automation.
/// </summary>
public class MachineNode : MonoBehaviour
{
    [Header("Power State")]
    [SerializeField] private bool isPowered = false;
    [SerializeField] private MachineNode[] outputs;

    [Header("Visuals")]
    [SerializeField] private ParticleSystem powerParticles;
    [SerializeField] private Light glowLight;

    [Header("Audio")]
    [SerializeField] private AudioSource powerSound;

    public bool IsPowered => isPowered;

    public void PowerUp()
    {
        if (isPowered) return;

        isPowered = true;
        Debug.Log($"[MachineNode] {gameObject.name} powered up!");

        // Play VFX
        if (powerParticles != null)
            powerParticles.Play();

        if (glowLight != null)
            glowLight.enabled = true;

        // Play audio
        if (powerSound != null)
            powerSound.Play();

        // Cascade to outputs
        if (outputs != null && outputs.Length > 0)
        {
            foreach (var node in outputs)
            {
                if (node != null)
                    node.PowerUp();
            }
        }
    }

    public void PowerDown()
    {
        if (!isPowered) return;

        isPowered = false;

        if (glowLight != null)
            glowLight.enabled = false;

        Debug.Log($"[MachineNode] {gameObject.name} powered down");
    }
}
