using UnityEngine;
using System.Collections;

/// <summary>
/// Triggers machine overload sequences with danger states.
/// Creates sparks, smoke, flickering lights, and chain reactions.
/// Links machines for cascade failures.
/// </summary>
public class MachineOverload : MonoBehaviour
{
    [Header("Machine Components")]
    [SerializeField] private Light machineLight;
    [SerializeField] private ParticleSystem sparks;
    [SerializeField] private ParticleSystem smoke;
    [SerializeField] private AudioSource overloadSound;
    [SerializeField] private AudioSource shutdownSound;

    [Header("Overload Settings")]
    [SerializeField] private float flickerSpeed = 0.1f;
    [SerializeField] private float overloadDuration = 2f;

    [Header("Chain Reaction")]
    [SerializeField] private MachineOverload[] linkedMachines;

    private bool isOverloading = false;

    public void TriggerOverload()
    {
        if (isOverloading) return;
        isOverloading = true;

        StartCoroutine(OverloadRoutine());
    }

    private IEnumerator OverloadRoutine()
    {
        Debug.Log($"[MachineOverload] {gameObject.name} overloading!");

        // Play overload sound
        if (overloadSound != null)
            overloadSound.Play();

        float time = 0f;

        // Flicker and spark phase
        while (time < overloadDuration)
        {
            if (machineLight != null)
                machineLight.enabled = !machineLight.enabled;

            if (sparks != null)
                sparks.Play();

            // Trigger camera shake
            if (CameraShake.Instance != null)
                CameraShake.Instance.Shake(0.2f, 0.15f);

            time += flickerSpeed;
            yield return new WaitForSeconds(flickerSpeed);
        }

        // Shutdown
        ShutdownMachine();
    }

    private void ShutdownMachine()
    {
        isOverloading = false;

        if (machineLight != null)
            machineLight.enabled = false;

        if (smoke != null)
            smoke.Play();

        if (shutdownSound != null)
            shutdownSound.Play();

        Debug.Log($"[MachineOverload] {gameObject.name} shutdown!");

        // Cascade to linked machines
        if (linkedMachines != null && linkedMachines.Length > 0)
        {
            foreach (var m in linkedMachines)
            {
                if (m != null)
                    m.TriggerOverload();
            }
        }
    }
}
