using UnityEngine;

/// <summary>
/// Creates 2D overlay effects for the cave machines.
/// Adds glowing quad overlays at machine positions with pulsing and shimmer effects.
/// </summary>
public class CaveMachineEffectsOverlay : MonoBehaviour
{
    [Header("Machine Positions (in world units)")]
    [SerializeField] private Vector2 leftMachinePos = new Vector2(-4f, 0f);
    [SerializeField] private Vector2 rightMachinePos = new Vector2(4f, -1f);

    [Header("Left Machine Transform")]
    [SerializeField] private Vector3 leftMachinePosition = new Vector3(-4.96f, 1.29f, -0.5f);
    [SerializeField] private Vector3 leftMachineRotation = new Vector3(8.977f, -32.615f, 12.729f);
    [SerializeField] private Vector3 leftMachineScale = new Vector3(2.710269f, 2.969019f, 0.95581f);

    [Header("Right Machine Transform")]
    [SerializeField] private Vector3 rightMachinePosition = new Vector3(-1.03f, 0.48f, -0.5f);
    [SerializeField] private Vector3 rightMachineRotation = new Vector3(17.717f, 46.692f, -17.234f);
    [SerializeField] private Vector3 rightMachineScale = new Vector3(0.614835f, 1.5f, 1f);

    [Header("Effect Settings")]
    [SerializeField] private Color glowColor = new Color(0, 1, 1, 1); // Cyan

    [ContextMenu("Setup Effect Overlays")]
    private void SetupEffectOverlays()
    {
        // Create left machine glow overlay with predefined transform
        GameObject leftGlow = CreateGlowOverlay("LeftMachineGlow");
        leftGlow.transform.localPosition = leftMachinePosition;
        leftGlow.transform.localEulerAngles = leftMachineRotation;
        leftGlow.transform.localScale = leftMachineScale;

        SpriteRenderer leftSprite = leftGlow.GetComponent<SpriteRenderer>();
        MachinePulseGlow2D leftPulse = leftGlow.AddComponent<MachinePulseGlow2D>();
        leftPulse.glowLight = null;
        leftPulse.spriteRenderer = leftSprite;

        MachineShimmer2D leftShimmer = leftGlow.AddComponent<MachineShimmer2D>();

        // Create right machine glow overlay with predefined transform
        GameObject rightGlow = CreateGlowOverlay("RightMachineGlow");
        rightGlow.transform.localPosition = rightMachinePosition;
        rightGlow.transform.localEulerAngles = rightMachineRotation;
        rightGlow.transform.localScale = rightMachineScale;

        SpriteRenderer rightSprite = rightGlow.GetComponent<SpriteRenderer>();
        MachinePulseGlow2D rightPulse = rightGlow.AddComponent<MachinePulseGlow2D>();
        rightPulse.glowLight = null;
        rightPulse.spriteRenderer = rightSprite;

        MachineShimmer2D rightShimmer = rightGlow.AddComponent<MachineShimmer2D>();

        Debug.Log("Cave machine effect overlays created at predefined positions!");
    }

    private GameObject CreateGlowOverlay(string name)
    {
        // Create sprite for the glow effect
        GameObject glowObj = new GameObject(name);
        glowObj.transform.SetParent(transform);
        glowObj.transform.localPosition = Vector3.zero;
        glowObj.transform.localScale = Vector3.one;

        // Add sprite renderer
        SpriteRenderer spriteRenderer = glowObj.AddComponent<SpriteRenderer>();
        spriteRenderer.sortingOrder = 0;

        // Create and assign the circle sprite
        spriteRenderer.sprite = CreateCircleSprite();
        spriteRenderer.color = glowColor;

        return glowObj;
    }

    private Sprite CreateCircleSprite()
    {
        // Create a simple circular texture for the glow
        Texture2D circleTexture = new Texture2D(64, 64, TextureFormat.RGBA32, false);
        Color[] pixels = circleTexture.GetPixels();

        Vector2 center = new Vector2(32, 32);
        float radius = 30f;

        for (int i = 0; i < pixels.Length; i++)
        {
            int x = i % 64;
            int y = i / 64;
            float distFromCenter = Vector2.Distance(new Vector2(x, y), center);

            // Create a radial gradient
            if (distFromCenter < radius)
            {
                float alpha = 1f - (distFromCenter / radius);
                pixels[i] = new Color(1, 1, 1, alpha * alpha); // Smooth falloff
            }
            else
            {
                pixels[i] = new Color(1, 1, 1, 0);
            }
        }

        circleTexture.SetPixels(pixels);
        circleTexture.Apply();

        return Sprite.Create(circleTexture, new Rect(0, 0, 64, 64), new Vector2(0.5f, 0.5f));
    }
}
