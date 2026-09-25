using UnityEngine;

public class PulsingGlow : MonoBehaviour
{
    [SerializeField] private float minIntensity = 0.5f;
    [SerializeField] private float maxIntensity = 1.5f;
    [SerializeField] private float pulseSpeed = 2.0f;
    
    private Renderer targetRenderer;
    private static readonly int EmissionColor = Shader.PropertyToID("_EmissionColor");
    private Color baseColor;

    private void Awake()
    {
        targetRenderer = GetComponent<Renderer>();
        if (targetRenderer != null)
        {
            baseColor = targetRenderer.material.GetColor(EmissionColor);
        }
    }

    private void Update()
    {
        if (targetRenderer == null) return;
        
        float t = Mathf.PingPong(Time.time * pulseSpeed, 1.0f);
        float intensity = Mathf.Lerp(minIntensity, maxIntensity, t);
        targetRenderer.material.SetColor(EmissionColor, baseColor * intensity);
    }
}
