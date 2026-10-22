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
using System.Collections.Generic;

/// <summary>
/// Creates a sparkling/glitter effect with random bright twinkles.
/// Generates small sparkle overlays that randomly flash and fade around the main glow or along wires.
/// </summary>
public class MachineShimmer2D : MonoBehaviour
{
    public enum SpawnDistribution
    {
        Circular,
        Box,
        WirePoints
    }

    [Header("Sparkle Settings")]
    [SerializeField] private int sparkleCount = 5;
    [SerializeField] private float sparkleSpeed = 0.3f; // How fast sparkles flash
    [SerializeField] private float sparkleAppearChance = 0.02f; // Chance per frame to spawn new sparkle
    [SerializeField] private Color sparkleColor = new Color(1, 1, 1, 1); // White sparkles
    [SerializeField] private float sparkleScale = 0.3f;

    [Header("Spawn Distribution")]
    [SerializeField] private SpawnDistribution distribution = SpawnDistribution.Circular;
    [Tooltip("Min and max radius for Circular distribution")]
    [SerializeField] private float minRadius = 0.2f;
    [SerializeField] private float maxRadius = 0.8f;
    [Tooltip("Width and height for Box distribution")]
    [SerializeField] private Vector2 areaSize = new Vector2(1f, 1f);
    [Tooltip("Specific local positions along wires for WirePoints distribution")]
    [SerializeField] private Vector2[] wirePoints;
    [SerializeField] private float wireJitter = 0.05f;

    [Header("3D Lighting")]
    [SerializeField] private Light flickerLight;
    [SerializeField] private float minFlickerIntensity = 0f;
    [SerializeField] private float maxFlickerIntensity = 1f;

    private List<GameObject> sparkles = new List<GameObject>();
    private List<float> sparkleTimers = new List<float>();

    private void Start()
    {
        if (flickerLight == null)
            flickerLight = GetComponent<Light>();

        // Create sparkle objects
        for (int i = 0; i < sparkleCount; i++)
        {
            CreateSparkle();
            sparkleTimers.Add(0f);
        }
    }

    private void OnDestroy()
    {
        for (int i = 0; i < sparkles.Count; i++)
        {
            if (sparkles[i] != null)
                Destroy(sparkles[i]);
        }
        sparkles.Clear();
        sparkleTimers.Clear();
    }

    private void Update()
    {
        int activeSparkles = 0;

        // Update each sparkle
        for (int i = 0; i < sparkles.Count; i++)
        {
            if (sparkles[i] == null)
                continue;

            sparkleTimers[i] -= Time.deltaTime;

            // Sparkle has finished, hide it
            if (sparkleTimers[i] <= 0f)
            {
                sparkles[i].SetActive(false);

                // Randomly spawn new sparkles
                if (Random.value < sparkleAppearChance)
                {
                    sparkleTimers[i] = sparkleSpeed;
                    sparkles[i].SetActive(true);
                    RandomizeSparklePosition(sparkles[i]);
                }
            }
            else
            {
                activeSparkles++;
                // Fade sparkle in/out
                float normalizedTime = 1f - (sparkleTimers[i] / sparkleSpeed);
                float alpha = Mathf.Sin(normalizedTime * Mathf.PI) * 0.8f; // Peak at middle, fade at edges

                SpriteRenderer sr = sparkles[i].GetComponent<SpriteRenderer>();
                Color color = sparkleColor;
                color.a = alpha;
                sr.color = color;
            }
        }

        // Update flicker light based on active sparkle count
        if (flickerLight != null)
        {
            float intensityTarget = Mathf.Lerp(minFlickerIntensity, maxFlickerIntensity, (float)activeSparkles / sparkleCount);
            // Add some high-frequency noise for "sparking" feel
            intensityTarget *= Random.Range(0.8f, 1.2f);
            flickerLight.intensity = Mathf.MoveTowards(flickerLight.intensity, intensityTarget, Time.deltaTime * 5f);
        }
    }

    private void CreateSparkle()
    {
        GameObject sparkle = new GameObject($"Sparkle_{sparkles.Count}");
        sparkle.transform.SetParent(transform);
        sparkle.transform.localPosition = Vector3.zero;
        sparkle.transform.localScale = new Vector3(sparkleScale, sparkleScale, 1f);

        SpriteRenderer sr = sparkle.AddComponent<SpriteRenderer>();
        sr.sprite = CreateSmallSparkleSprite();
        sr.sortingOrder = 1; // Above the main glow
        sr.color = new Color(1, 1, 1, 0);

        sparkle.SetActive(false);
        sparkles.Add(sparkle);
    }

    private void RandomizeSparklePosition(GameObject sparkle)
    {
        Vector2 pos = Vector2.zero;

        switch (distribution)
        {
            case SpawnDistribution.Box:
                pos = new Vector2(
                    Random.Range(-areaSize.x * 0.5f, areaSize.x * 0.5f),
                    Random.Range(-areaSize.y * 0.5f, areaSize.y * 0.5f)
                );
                break;

            case SpawnDistribution.WirePoints:
                if (wirePoints != null && wirePoints.Length > 0)
                {
                    if (wirePoints.Length == 1)
                    {
                        pos = wirePoints[0];
                    }
                    else
                    {
                        int segmentIndex = Random.Range(0, wirePoints.Length - 1);
                        float t = Random.value;
                        pos = Vector2.Lerp(wirePoints[segmentIndex], wirePoints[segmentIndex + 1], t);
                    }
                    pos += Random.insideUnitCircle * wireJitter;
                }
                else
                {
                    float angle = Random.Range(0f, 360f) * Mathf.Deg2Rad;
                    float distance = Random.Range(minRadius, maxRadius);
                    pos = new Vector2(Mathf.Cos(angle) * distance, Mathf.Sin(angle) * distance);
                }
                break;

            case SpawnDistribution.Circular:
            default:
                float a = Random.Range(0f, 360f) * Mathf.Deg2Rad;
                float d = Random.Range(minRadius, maxRadius);
                pos = new Vector2(Mathf.Cos(a) * d, Mathf.Sin(a) * d);
                break;
        }

        sparkle.transform.localPosition = new Vector3(pos.x, pos.y, -0.1f);
    }

    private void OnDrawGizmosSelected()
    {
        Gizmos.color = new Color(0.2f, 0.9f, 1f, 0.75f);
        Matrix4x4 oldMatrix = Gizmos.matrix;
        Gizmos.matrix = transform.localToWorldMatrix;

        switch (distribution)
        {
            case SpawnDistribution.Box:
                Gizmos.DrawWireCube(Vector3.zero, new Vector3(areaSize.x, areaSize.y, 0.05f));
                break;

            case SpawnDistribution.Circular:
                int segments = 24;
                Vector3 prevMax = Vector3.zero;
                Vector3 prevMin = Vector3.zero;
                for (int i = 0; i <= segments; i++)
                {
                    float angle = (i % segments) * Mathf.PI * 2f / segments;
                    Vector3 ptMax = new Vector3(Mathf.Cos(angle) * maxRadius, Mathf.Sin(angle) * maxRadius, 0);
                    Vector3 ptMin = new Vector3(Mathf.Cos(angle) * minRadius, Mathf.Sin(angle) * minRadius, 0);
                    if (i > 0)
                    {
                        Gizmos.DrawLine(prevMax, ptMax);
                        Gizmos.DrawLine(prevMin, ptMin);
                    }
                    prevMax = ptMax;
                    prevMin = ptMin;
                }
                break;

            case SpawnDistribution.WirePoints:
                if (wirePoints != null && wirePoints.Length > 0)
                {
                    for (int i = 0; i < wirePoints.Length; i++)
                    {
                        Gizmos.DrawWireSphere(new Vector3(wirePoints[i].x, wirePoints[i].y, 0), wireJitter > 0 ? wireJitter : 0.05f);
                        if (i < wirePoints.Length - 1)
                        {
                            Gizmos.DrawLine(new Vector3(wirePoints[i].x, wirePoints[i].y, 0),
                                            new Vector3(wirePoints[i + 1].x, wirePoints[i + 1].y, 0));
                        }
                    }
                }
                break;
        }

        Gizmos.matrix = oldMatrix;
    }

    private Sprite CreateSmallSparkleSprite()
    {
        // Create a small, bright star-like sparkle
        Texture2D sparkleTexture = new Texture2D(16, 16, TextureFormat.RGBA32, false);
        Color[] pixels = sparkleTexture.GetPixels();

        Vector2 center = new Vector2(8, 8);

        for (int i = 0; i < pixels.Length; i++)
        {
            int x = i % 16;
            int y = i / 16;
            float distFromCenter = Vector2.Distance(new Vector2(x, y), center);

            // Bright center, fade edges
            if (distFromCenter < 4f)
            {
                float alpha = 1f - (distFromCenter / 4f);
                pixels[i] = new Color(1, 1, 1, alpha * alpha);
            }
            else
            {
                pixels[i] = new Color(1, 1, 1, 0);
            }
        }

        sparkleTexture.SetPixels(pixels);
        sparkleTexture.Apply();

        return Sprite.Create(sparkleTexture, new Rect(0, 0, 16, 16), new Vector2(0.5f, 0.5f));
    }
}
