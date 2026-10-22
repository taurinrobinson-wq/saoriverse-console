using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Displays the Triglyph Monster projection floating within the projector beam.
/// Shows the assigned texture with a subtle floating animation and projector color tinting.
/// </summary>
public class TriglyphMonsterProjector : MonoBehaviour
{
    [Header("Projection Display")]
    [SerializeField] private RawImage projectionDisplay;
    
    [Header("Stage Texture (Swap per variant)")]
    [SerializeField] private Texture stageTexture;
    
    [Header("Animation")]
    [SerializeField, Range(0f, 1f)] private float floatingAmount = 0.1f;
    [SerializeField] private float floatingSpeed = 1f;

    [Header("Lighting Integration")]
    [SerializeField] private ProjectorEffectController projectorController;
    [SerializeField] private bool tintWithProjectorColor = true;

    private CanvasGroup canvasGroup;
    private Vector3 basePosition;

    private void Awake()
    {
        InitializeProjection();
    }

    private void InitializeProjection()
    {
        if (projectionDisplay == null)
            projectionDisplay = GetComponent<RawImage>();

        canvasGroup = gameObject.GetComponent<CanvasGroup>();
        if (canvasGroup == null)
            canvasGroup = gameObject.AddComponent<CanvasGroup>();

        if (projectorController == null)
            projectorController = FindObjectOfType<ProjectorEffectController>();

        basePosition = transform.position;

        // Set initial texture
        if (stageTexture != null && projectionDisplay != null)
            projectionDisplay.texture = stageTexture;
    }

    private void OnEnable()
    {
        if (projectionDisplay != null)
            projectionDisplay.enabled = true;
    }

    private void OnDisable()
    {
        if (projectionDisplay != null)
            projectionDisplay.enabled = false;
    }

    private void Update()
    {
        UpdateFloatingAnimation();
        if (tintWithProjectorColor && projectorController != null)
            UpdateProjectorColorTint();
    }

    private void UpdateFloatingAnimation()
    {
        if (basePosition == Vector3.zero)
            basePosition = transform.position;

        float floatOffset = Mathf.Sin(Time.time * floatingSpeed) * floatingAmount;
        Vector3 newPosition = basePosition + Vector3.up * floatOffset;
        transform.position = newPosition;
    }

    private void UpdateProjectorColorTint()
    {
        if (projectionDisplay == null || projectorController == null)
            return;

        Color projectorColor = projectorController.GetCurrentColor();
        projectionDisplay.color = Color.Lerp(Color.white, projectorColor, 0.3f);
    }
}
