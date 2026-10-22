using UnityEngine;

/// <summary>
/// Makes the 3D player respond dynamically to environmental lights in the 2.5D cave:
/// 1. Projector: intense spectral rim/emissive, ONLY when inside the beam radius/cone.
/// 2. Wall Lights (Square & Tube): soft cyan rim/emissive increasing with proximity.
/// 3. Blue Fill Light (Right Side): cool blue rim/emissive increasing towards the right.
/// </summary>
public class PlayerReactiveLighting : MonoBehaviour
{
    [Header("Player Material Target")]
    [SerializeField] private Renderer playerRenderer;
    [SerializeField] private Color baseAmbientRim = new Color(0.02f, 0.04f, 0.06f, 1f);
    [SerializeField] private float maxTotalEmission = 3.0f;

    [Header("Tracked Light Sources")]
    [SerializeField] private ProjectorEffectController projector;
    [SerializeField] private Transform squareWallLight;
    [SerializeField] private Transform tubeWallLight;
    [SerializeField] private Transform blueFillLight;

    [Header("Range Parameters")]
    [SerializeField] private float squareWallRange = 9.5f;
    [SerializeField] private float tubeWallRange = 8.0f;
    [SerializeField] private float blueFillRange = 12.0f;

    private Material playerMat;
    private static readonly int EmissionColorId = Shader.PropertyToID("_EmissionColor");
    private static readonly int MetallicId = Shader.PropertyToID("_Metallic");
    private static readonly int SmoothnessId = Shader.PropertyToID("_Smoothness");

    private void Start()
    {
        if (playerRenderer == null)
            playerRenderer = GetComponentInChildren<SkinnedMeshRenderer>();
        if (playerRenderer == null)
            playerRenderer = GetComponentInChildren<Renderer>();

        if (playerRenderer != null)
        {
            playerMat = playerRenderer.material;
            playerMat.EnableKeyword("_EMISSION");
        }

        FindLightSourcesIfNull();
    }

    private void FindLightSourcesIfNull()
    {
        if (projector == null)
            projector = Object.FindAnyObjectByType<ProjectorEffectController>();

        if (squareWallLight == null)
        {
            var go = GameObject.Find("WallLight_SquarePanel");
            if (go != null) squareWallLight = go.transform;
        }

        if (tubeWallLight == null)
        {
            var go = GameObject.Find("WallLight_HorizontalTube");
            if (go != null) tubeWallLight = go.transform;
        }

        if (blueFillLight == null)
        {
            var go = GameObject.Find("RightSide_BlueFill");
            if (go != null) blueFillLight = go.transform;
        }
    }

    private void Update()
    {
        if (playerMat == null) return;

        Vector3 playerPos = transform.position;

        // 1. Projector Beam Response (Strict radius check)
        Color projContrib = Color.black;
        float projFactor = 0f;
        if (projector != null && projector.CheckPlayerInsideBeam(playerPos, out float beamFactor, out Color projColor))
        {
            projFactor = beamFactor;
            // Intense spectral rim when inside the light cone
            projContrib = projColor * (beamFactor * 2.5f);
        }

        // 2. Square Wall Light Response (Upper Left)
        Color sqContrib = Color.black;
        float sqFactor = 0f;
        if (squareWallLight != null)
        {
            float dist = Vector3.Distance(playerPos, squareWallLight.position);
            sqFactor = Mathf.Clamp01(1f - (dist / squareWallRange));
            sqFactor = sqFactor * sqFactor; // Smooth falloff curve
            Color sqColor = new Color(0.2f, 0.95f, 1.0f);
            sqContrib = sqColor * (sqFactor * 1.1f);
        }

        // 3. Horizontal Tube Light Response (Lower Mid-Left)
        Color tubeContrib = Color.black;
        float tubeFactor = 0f;
        if (tubeWallLight != null)
        {
            float dist = Vector3.Distance(playerPos, tubeWallLight.position);
            tubeFactor = Mathf.Clamp01(1f - (dist / tubeWallRange));
            tubeFactor = tubeFactor * tubeFactor;
            Color tubeColor = new Color(0.12f, 0.9f, 1.0f);
            tubeContrib = tubeColor * (tubeFactor * 0.95f);
        }

        // 4. Blue Fill Light Response (Right Side)
        Color blueContrib = Color.black;
        float blueFactor = 0f;
        if (blueFillLight != null)
        {
            float dist = Vector3.Distance(playerPos, blueFillLight.position);
            blueFactor = Mathf.Clamp01(1f - (dist / blueFillRange));
            blueFactor = blueFactor * blueFactor;
            Color blueColor = new Color(0.15f, 0.45f, 0.95f);
            blueContrib = blueColor * (blueFactor * 1.3f);
        }

        // 5. Combine Environmental Lighting Responses
        Color totalEmission = baseAmbientRim + projContrib + sqContrib + tubeContrib + blueContrib;
        // Clamp to prevent blowout
        totalEmission.r = Mathf.Min(totalEmission.r, maxTotalEmission);
        totalEmission.g = Mathf.Min(totalEmission.g, maxTotalEmission);
        totalEmission.b = Mathf.Min(totalEmission.b, maxTotalEmission);

        Color currentEmission = playerMat.GetColor(EmissionColorId);
        playerMat.SetColor(EmissionColorId, Color.Lerp(currentEmission, totalEmission, Time.deltaTime * 8f));

        // Adjust specular response based on proximity to active lights
        float maxLightFactor = Mathf.Max(projFactor, Mathf.Max(sqFactor, Mathf.Max(tubeFactor, blueFactor)));
        float targetMetallic = Mathf.Lerp(0.70f, 0.95f, maxLightFactor);
        float targetSmoothness = Mathf.Lerp(0.65f, 0.88f, maxLightFactor);

        playerMat.SetFloat(MetallicId, Mathf.Lerp(playerMat.GetFloat(MetallicId), targetMetallic, Time.deltaTime * 5f));
        playerMat.SetFloat(SmoothnessId, Mathf.Lerp(playerMat.GetFloat(SmoothnessId), targetSmoothness, Time.deltaTime * 5f));
    }
}


