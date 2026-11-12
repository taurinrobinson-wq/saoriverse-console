using UnityEngine;

/// <summary>
/// Adds a dynamic shadow decal under a character/object in 2.5D games.
/// Optimized for XY plane side-scrolling views.
/// Attach to any character or glyph that needs a shadow.
/// </summary>
[ExecuteInEditMode]
public class ShadowDecal : MonoBehaviour
{
[Header("Shadow Settings")]
    [SerializeField] private float footOffset = 0.5f; // Distance from player root to feet
    [SerializeField] private float shadowScale = 1.0f; // Base size of shadow
    [SerializeField] private Vector2 shadowOffset = new Vector2(-0.7f, -0.1f); // Manual fallback offset
    [SerializeField] private float shadowSkew = 0.3f; // Skew/elongation for directional shadows
    [SerializeField] private Color shadowColor = new Color(0, 0, 0, 0.75f); // Increased base alpha
    [SerializeField] private float sortingOrderOffset = -1; // Render behind the player

    [Header("Lighting Sync")]
    [SerializeField] private bool syncWithMainLight = true;
    [SerializeField] private float lightOffsetMultiplier = 1.2f; 
    [SerializeField] private Color shadowTint = new Color(0.05f, 0.05f, 0.2f, 1f); // Darker tint

    [Header("Bones (Optional for Dynamics)")]
    [SerializeField] private Transform hipsBone;
    [SerializeField] private Transform leftFoot;
    [SerializeField] private Transform rightFoot;

    [Header("Dynamic Scaling")]
    [SerializeField] private float bounceSensitivity = 0.5f; // How much jump/bounce affects opacity
    [SerializeField] private float strideSensitivity = 1.2f; // How much leg spread affects shadow width
    [SerializeField] private float minAlpha = 0.2f;
    [SerializeField] private float maxAlpha = 0.5f;

    private GameObject shadowObj;
    private SpriteRenderer shadowRenderer;
    private float initialHipsY;
    private bool hasBones = false;
    private static Light mainLight;

    private void Start()
    {
        CreateShadowDecal();
        if (hipsBone != null && leftFoot != null && rightFoot != null)
        {
            initialHipsY = hipsBone.localPosition.y;
            hasBones = true;
        }

        if (mainLight == null) FindMainLight();
    }

    private static void FindMainLight()
    {
        // Find the most intense directional light
        Light[] lights = Object.FindObjectsByType<Light>(FindObjectsSortMode.None);
        float maxIntensity = -1f;
        foreach (var l in lights)
        {
            if (l.type == LightType.Directional && l.intensity > maxIntensity)
            {
                mainLight = l;
                maxIntensity = l.intensity;
            }
        }
    }

    private void OnDestroy()
    {
        if (shadowObj != null)
        {
            if (Application.isPlaying)
            {
                Destroy(shadowObj);
            }
            else
            {
                DestroyImmediate(shadowObj);
            }
        }
    }

    private void CreateShadowDecal()
    {
        shadowObj = new GameObject(gameObject.name + "_ShadowVisual");
        shadowObj.hideFlags = HideFlags.DontSave;
        // Do NOT parent to this object to avoid inherited rotation whiplash
        shadowObj.transform.position = transform.position;
        shadowObj.transform.rotation = Quaternion.identity;

        shadowRenderer = shadowObj.AddComponent<SpriteRenderer>();
        shadowRenderer.sprite = CreateShadowSprite();
        shadowRenderer.color = shadowColor;
        
        // Match player sorting
        SpriteRenderer playerSr = GetComponentInChildren<SpriteRenderer>();
        if (playerSr != null)
        {
            shadowRenderer.sortingLayerID = playerSr.sortingLayerID;
            shadowRenderer.sortingOrder = playerSr.sortingOrder + (int)sortingOrderOffset;
        }
        else
        {
            shadowRenderer.sortingOrder = -1;
        }
    }

    private Sprite CreateShadowSprite()
    {
        int res = 64;
        Texture2D tex = new Texture2D(res, res, TextureFormat.RGBA32, false);
        Color[] pixels = new Color[res * res];
        Vector2 center = new Vector2(res / 2f, res / 2f);
        float radius = res / 2f;

        for (int y = 0; y < res; y++)
        {
            for (int x = 0; x < res; x++)
            {
                float dist = Vector2.Distance(new Vector2(x, y), center);
                float alpha = Mathf.Clamp01(1f - (dist / radius));
                alpha = Mathf.Pow(alpha, 1.5f); 
                pixels[y * res + x] = new Color(1, 1, 1, alpha);
            }
        }

        tex.SetPixels(pixels);
        tex.Apply();
        return Sprite.Create(tex, new Rect(0, 0, res, res), new Vector2(0.5f, 0.5f));
    }

    private void LateUpdate()
    {
        if (shadowObj == null) return;
        
        // Ensure visibility matches parent
        if (shadowRenderer.enabled != gameObject.activeInHierarchy)
            shadowRenderer.enabled = gameObject.activeInHierarchy;

        // 1. Calculate Shadow Parameters from Light
        Vector2 currentOffset = shadowOffset;
        Color currentShadowColor = shadowColor;

        if (syncWithMainLight && mainLight != null)
        {
            // Project light direction onto the XY plane
            Vector3 lightDir = mainLight.transform.forward;
            
            // If the light is from the 'right', cast shadow 'left'
            currentOffset.x += -lightDir.x * lightOffsetMultiplier;
            currentOffset.y += -lightDir.y * 0.2f; // Add light offset to the manual placement

            // Dynamic Tinting: Blend base shadow with a cool tint for ambient depth
            // Warm lights (red/orange) create cool shadows (blue/purple)
            float intensityFactor = Mathf.Clamp01(mainLight.intensity / 2f);
            currentShadowColor = Color.Lerp(new Color(0,0,0,0.5f), shadowTint, 0.3f);
            currentShadowColor.a = shadowColor.a * intensityFactor;
        }

        // 2. Position handling (World Space)
        // Fixed offset in world space ensures shadow direction is independent of character facing
        Vector3 playerPos = transform.position;
        Vector3 shadowWorldPos = new Vector3(
            playerPos.x + currentOffset.x,
            playerPos.y - footOffset + currentOffset.y,
            playerPos.z - 0.05f // Move slightly closer to camera to stay in front of ground
        );
shadowObj.transform.position = shadowWorldPos;
        shadowObj.transform.rotation = Quaternion.identity; 

        // 3. Biomechanical Dynamics
        float currentStrideWidth = 1f;
        float currentAlpha = currentShadowColor.a;

        if (hasBones)
        {
            // Stride: Distance between feet on local X axis
            float footDistX = Mathf.Abs(leftFoot.localPosition.x - rightFoot.localPosition.x);
            currentStrideWidth = 1f + (footDistX * strideSensitivity);

            // Bounce: Vertical hips offset relative to character root
            float hipsOffset = hipsBone.localPosition.y - initialHipsY;
            if (hipsOffset > 0)
            {
                float bounceFactor = Mathf.Clamp01(hipsOffset * bounceSensitivity);
                currentStrideWidth *= (1f - bounceFactor * 0.2f);
                currentAlpha = Mathf.Lerp(currentAlpha, minAlpha, bounceFactor);
            }
        }

        // 4. Apply visual updates
        shadowRenderer.color = new Color(currentShadowColor.r, currentShadowColor.g, currentShadowColor.b, currentAlpha);
        
        // Scale includes the parent's scale for depth perception, but remains world-aligned
        float worldScale = Mathf.Abs(transform.lossyScale.x);
        shadowObj.transform.localScale = new Vector3(
            worldScale * shadowScale * (1f + shadowSkew) * currentStrideWidth,
            worldScale * shadowScale * 0.3f, 
            1f
        );
    }

    public void SetShadowColor(Color color)
    {
        shadowColor = color;
        if (shadowRenderer != null) shadowRenderer.color = color;
    }

    public void SetFootOffset(float offset)
    {
        footOffset = offset;
    }

    public void SetShadowOffset(Vector2 offset)
    {
        shadowOffset = offset;
    }

    public void SetShadowSkew(float skew)
    {
        shadowSkew = skew;
    }
}

