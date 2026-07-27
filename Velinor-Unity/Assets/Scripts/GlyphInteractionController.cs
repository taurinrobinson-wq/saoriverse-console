using UnityEngine;

public class GlyphInteractionController : MonoBehaviour
{
    [Header("Interaction")]
    [SerializeField] private GlowPulseController glowPulseController;
    [SerializeField] private string requiredFlag = "kaelen_confessed";
    [SerializeField] private string successFlag = "obtained_remembrance";

    [Header("Visuals")]
    [SerializeField] private GameObject memoryFlashCanvas;
    [SerializeField] private float flashDuration = 1.2f;

    private bool hasCollected;

    private void Start()
    {
        if (glowPulseController != null && !GameFlags.Get(requiredFlag))
            glowPulseController.SetActiveVisual(false);
    }

    private void Update()
    {
        if (hasCollected || !GameFlags.Get(requiredFlag)) return;
        if (Input.GetKeyDown(KeyCode.E))
        {
            CollectGlyph();
        }
    }

    private void CollectGlyph()
    {
        if (hasCollected) return;
        hasCollected = true;

        if (memoryFlashCanvas != null)
            memoryFlashCanvas.SetActive(true);

        GameFlags.Set(successFlag, true);

        if (glowPulseController != null)
            glowPulseController.SetActiveVisual(false);

        Debug.Log("[GlyphInteractionController] Remembrance collected.");
    }
}
