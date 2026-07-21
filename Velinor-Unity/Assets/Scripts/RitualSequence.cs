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
/// Multi-step ritual logic for chamber puzzles.
/// Enforces ordered steps: PlaceGlyph → ActivateMachine → PowerConduit → ResonateChamber
/// Unlocks inner sanctum/door when all steps complete.
/// </summary>
public class RitualSequence : MonoBehaviour
{
    [Header("Ritual Steps")]
    [SerializeField]
    private string[] steps = new string[]
    {
        "PlaceGlyph",
        "ActivateMachine",
        "PowerConduit",
        "ResonateChamber"
    };
    private int currentStep = 0;

    [Header("Linked Systems")]
    [SerializeField] private MachineNode machineNode;
    [SerializeField] private MachineOverload overloadSystem;
    [SerializeField] private DoorController innerDoor;
    [SerializeField] private AmbientLayerController ambientController;

    [Header("Ritual Settings")]
    [SerializeField] private bool requireSequence = true;

    public int CurrentStep => currentStep;
    public int TotalSteps => steps.Length;

    private void Awake()
    {
        Debug.Log($"[RitualSequence] Initialized with {steps.Length} steps");
    }

    /// <summary>
    /// Perform a ritual step. Must be in correct sequence if requireSequence is true.
    /// </summary>
    public void PerformStep(string stepID)
    {
        // Check if step is correct (if sequences required)
        if (requireSequence && stepID != steps[currentStep])
        {
            Debug.LogWarning($"[RitualSequence] Wrong step! Expected {steps[currentStep]}, got {stepID}");
            ResetRitual();
            return;
        }

        Debug.Log($"[RitualSequence] Step {currentStep + 1}/{steps.Length}: {stepID}");

        // Execute step logic
        ExecuteStep(stepID);

        currentStep++;

        // Check if ritual complete
        if (currentStep >= steps.Length)
            CompleteRitual();
    }

    private void ExecuteStep(string stepID)
    {
        switch (stepID)
        {
            case "PlaceGlyph":
                OnPlaceGlyph();
                break;

            case "ActivateMachine":
                OnActivateMachine();
                break;

            case "PowerConduit":
                OnPowerConduit();
                break;

            case "ResonateChamber":
                OnResonateChamber();
                break;

            default:
                Debug.LogWarning($"[RitualSequence] Unknown step: {stepID}");
                break;
        }
    }

    private void OnPlaceGlyph()
    {
        if (machineNode != null)
            machineNode.PowerUp();

        if (ambientController != null)
            ambientController.SetLayer("Glyph", true);
    }

    private void OnActivateMachine()
    {
        Debug.Log("[RitualSequence] Machine activated!");
        if (ambientController != null)
            ambientController.SetLayer("Machine", true);
    }

    private void OnPowerConduit()
    {
        if (CameraShake.Instance != null)
            CameraShake.Instance.Shake(0.4f, 0.2f);

        if (ambientController != null)
            ambientController.SetLayer("Chamber", true);
    }

    private void OnResonateChamber()
    {
        if (overloadSystem != null)
            overloadSystem.TriggerOverload();

        if (CameraShake.Instance != null)
            CameraShake.Instance.Shake(0.8f, 0.4f);
    }

    private void CompleteRitual()
    {
        Debug.Log("[RitualSequence] RITUAL COMPLETE!");

        if (innerDoor != null)
            innerDoor.OpenDoor();

        if (CameraShake.Instance != null)
            CameraShake.Instance.Shake(0.3f, 0.25f);
    }

    public void ResetRitual()
    {
        currentStep = 0;
        Debug.Log("[RitualSequence] Ritual reset");
    }
}
