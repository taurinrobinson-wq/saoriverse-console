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
