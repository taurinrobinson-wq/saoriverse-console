using UnityEngine;

public class GlowPulseController : MonoBehaviour
{
    [Header("Visuals")]
    [SerializeField] private Renderer glowRenderer;
    [SerializeField] private Material activeMaterial;
    [SerializeField] private float baseIntensity = 0.3f;
    [SerializeField] private float reactiveIntensity = 0.8f;
    [SerializeField] private float pulseSpeed = 2f;

    [Header("Detection")]
    [SerializeField] private float detectionRadius = 3f;
    [SerializeField] private string requiredFlag = "kaelen_confessed";

    private bool isActive;
    private Material originalMaterial;

    private void Start()
    {
        if (glowRenderer != null)
            originalMaterial = glowRenderer.material;

        isActive = GameFlags.Get(requiredFlag);
        if (isActive)
            SetActiveVisual(true);
        else
            SetActiveVisual(false);
    }

    private void Update()
    {
        if (!isActive) return;

        var player = GameObject.FindGameObjectWithTag("Player");
        if (player == null) return;

        float distance = Vector3.Distance(transform.position, player.transform.position);
        float intensity = distance <= detectionRadius ? reactiveIntensity : baseIntensity;
        float pulse = 0.5f + Mathf.Sin(Time.time * pulseSpeed) * 0.5f;
        if (glowRenderer != null && activeMaterial != null)
        {
            glowRenderer.material.SetFloat("_Intensity", intensity * pulse);
        }
    }

    public void SetActiveVisual(bool active)
    {
        isActive = active;
        if (glowRenderer != null)
        {
            glowRenderer.enabled = active;
            if (activeMaterial != null && active)
                glowRenderer.material = activeMaterial;
            else if (originalMaterial != null)
                glowRenderer.material = originalMaterial;
        }
    }
}
