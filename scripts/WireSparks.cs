using UnityEngine;

/// <summary>
/// Creates sporadic sparking effects along wires connected to machines.
/// Instantiates spark particles at random positions and intervals.
/// </summary>
public class WireSparks : MonoBehaviour
{
    [Header("Spark Settings")]
    [SerializeField] private LineRenderer wireLineRenderer;
    [SerializeField] private ParticleSystem sparkParticlePrefab;
    [SerializeField] private int sparkCount = 2;
    [SerializeField] private float sparkInterval = 0.5f;
    [SerializeField] private float sparkIntervalRandomness = 0.3f;
    
    [Header("Spark Positioning")]
    [SerializeField] private float minPositionOnWire = 0.1f;
    [SerializeField] private float maxPositionOnWire = 0.9f;
    [SerializeField] private float positionRandomness = 0.1f;
    
    [Header("Particle Settings")]
    [SerializeField] private float sparkLifetime = 0.5f;
    [SerializeField] private float sparkEmissionRate = 20f;
    
    private ParticleSystem[] activeSparks;
    private float nextSparkTime = 0f;
    private float currentSparkInterval;
    
    private void Start()
    {
        if (wireLineRenderer == null)
        {
            wireLineRenderer = GetComponent<LineRenderer>();
        }
        
        // Initialize active spark particles
        activeSparks = new ParticleSystem[sparkCount];
        for (int i = 0; i < sparkCount; i++)
        {
            activeSparks[i] = Instantiate(sparkParticlePrefab, transform);
            activeSparks[i].Stop();
        }
        
        SetNextSparkTime();
    }
    
    private void Update()
    {
        // Check if it's time to trigger sparks
        if (Time.time >= nextSparkTime)
        {
            TriggerSpark();
            SetNextSparkTime();
        }
    }
    
    private void TriggerSpark()
    {
        if (wireLineRenderer == null || wireLineRenderer.positionCount < 2)
            return;
        
        // Get a random particle system that isn't currently active
        ParticleSystem sparkSystem = activeSparks[Random.Range(0, sparkCount)];
        
        // Calculate random position along the wire
        float t = Random.Range(minPositionOnWire, maxPositionOnWire);
        t += Random.Range(-positionRandomness, positionRandomness);
        t = Mathf.Clamp01(t);
        
        // Interpolate position along the line renderer
        Vector3 sparkPosition = GetPositionOnWire(t);
        
        // Set particle system position
        sparkSystem.transform.position = sparkPosition;
        
        // Burst emission for visual impact
        sparkSystem.Play();
        var emission = sparkSystem.emission;
        emission.rateOverTime = sparkEmissionRate;
        
        // Add slight velocity variation for more organic look
        var velocity = sparkSystem.velocityOverLifetime;
        velocity.enabled = true;
        Vector3 randomVelocity = Random.onUnitSphere * Random.Range(0.5f, 2f);
        velocity.x = new ParticleSystem.MinMaxCurve(randomVelocity.x);
        velocity.y = new ParticleSystem.MinMaxCurve(randomVelocity.y);
        velocity.z = new ParticleSystem.MinMaxCurve(randomVelocity.z);
    }
    
    private Vector3 GetPositionOnWire(float t)
    {
        int positionCount = wireLineRenderer.positionCount;
        int segmentCount = positionCount - 1;
        
        // Find which segment of the wire
        float segmentT = t * segmentCount;
        int segment = Mathf.FloorToInt(segmentT);
        segment = Mathf.Clamp(segment, 0, segmentCount - 1);
        
        // Local position within segment
        float localT = segmentT - segment;
        
        // Get start and end positions of segment
        Vector3 startPos = wireLineRenderer.GetPosition(segment);
        Vector3 endPos = wireLineRenderer.GetPosition(segment + 1);
        
        // Interpolate
        return Vector3.Lerp(startPos, endPos, localT);
    }
    
    private void SetNextSparkTime()
    {
        float randomness = sparkInterval * sparkIntervalRandomness;
        currentSparkInterval = sparkInterval + Random.Range(-randomness, randomness);
        nextSparkTime = Time.time + currentSparkInterval;
    }
    
    /// <summary>
    /// Adjust spark frequency at runtime
    /// </summary>
    public void SetSparkFrequency(float frequency)
    {
        sparkInterval = frequency;
    }
    
    /// <summary>
    /// Enable/disable sparking
    /// </summary>
    public void SetSparkingActive(bool active)
    {
        enabled = active;
    }
}
