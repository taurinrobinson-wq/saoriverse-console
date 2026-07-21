using UnityEngine;
using System.Collections.Generic;

/// <summary>
/// Creates a sparkling/glitter effect with random bright twinkles.
/// Generates small sparkle overlays that randomly flash and fade around the main glow.
/// </summary>
public class MachineShimmer2D : MonoBehaviour
{
    [Header("Sparkle Settings")]
    [SerializeField] private int sparkleCount = 5;
    [SerializeField] private float sparkleSpeed = 0.3f; // How fast sparkles flash
    [SerializeField] private float sparkleAppearChance = 0.02f; // Chance per frame to spawn new sparkle
    [SerializeField] private Color sparkleColor = new Color(1, 1, 1, 1); // White sparkles

    private List<GameObject> sparkles = new List<GameObject>();
    private List<float> sparkleTimers = new List<float>();

    private void Start()
    {
        // Create sparkle objects
        for (int i = 0; i < sparkleCount; i++)
        {
            CreateSparkle();
            sparkleTimers.Add(0f);
        }
    }

    private void Update()
    {
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
                // Fade sparkle in/out
                float normalizedTime = 1f - (sparkleTimers[i] / sparkleSpeed);
                float alpha = Mathf.Sin(normalizedTime * Mathf.PI) * 0.8f; // Peak at middle, fade at edges

                SpriteRenderer sr = sparkles[i].GetComponent<SpriteRenderer>();
                Color color = sparkleColor;
                color.a = alpha;
                sr.color = color;
            }
        }
    }

    private void CreateSparkle()
    {
        GameObject sparkle = new GameObject($"Sparkle_{sparkles.Count}");
        sparkle.transform.SetParent(transform);
        sparkle.transform.localPosition = Vector3.zero;
        sparkle.transform.localScale = new Vector3(0.3f, 0.3f, 1f);

        SpriteRenderer sr = sparkle.AddComponent<SpriteRenderer>();
        sr.sprite = CreateSmallSparkleSprite();
        sr.sortingOrder = 1; // Above the main glow
        sr.color = new Color(1, 1, 1, 0);

        sparkle.SetActive(false);
        sparkles.Add(sparkle);
    }

    private void RandomizeSparklePosition(GameObject sparkle)
    {
        // Random position around the glow (circular distribution)
        float angle = Random.Range(0f, 360f) * Mathf.Deg2Rad;
        float distance = Random.Range(0.2f, 0.8f); // Within glow radius

        sparkle.transform.localPosition = new Vector3(
            Mathf.Cos(angle) * distance,
            Mathf.Sin(angle) * distance,
            -0.1f
        );
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
