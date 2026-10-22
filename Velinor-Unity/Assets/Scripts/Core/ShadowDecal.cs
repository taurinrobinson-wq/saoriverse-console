using UnityEngine;

/// <summary>
/// Adds a dynamic shadow decal under a character/object in 2.5D games.
/// Optimized for XY plane side-scrolling views.
/// Attach to any character or glyph that needs a shadow.
/// </summary>
public class ShadowDecal : MonoBehaviour
{
    [Header("Shadow Settings")]
    [SerializeField] private float footOffset = 0.5f; // Distance from player root to feet
    [SerializeField] private float shadowScale = 1.0f; // Base size of shadow
    [SerializeField] private Color shadowColor = new Color(0, 0, 0, 0.5f); // Shadow color with alpha
    [SerializeField] private float sortingOrderOffset = -1; // Render behind the player

    private GameObject shadowObj;
    private SpriteRenderer shadowRenderer;

    private void Start()
    {
        CreateShadowDecal();
    }

    private void CreateShadowDecal()
    {
        shadowObj = new GameObject("ShadowVisual");
        shadowObj.transform.SetParent(transform);
        shadowObj.transform.localPosition = new Vector3(0, -footOffset, 0.05f); // Slightly behind player on Z
        shadowObj.transform.localRotation = Quaternion.identity;
        shadowObj.transform.localScale = new Vector3(shadowScale, shadowScale * 0.3f, 1f); // Ellipse shape

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

        // Hide shadow in hierarchy to keep it clean
        shadowObj.hideFlags = HideFlags.HideInHierarchy;
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
                alpha = Mathf.Pow(alpha, 2); // Sharper falloff
                pixels[y * res + x] = new Color(1, 1, 1, alpha);
            }
        }

        tex.SetPixels(pixels);
        tex.Apply();
        return Sprite.Create(tex, new Rect(0, 0, res, res), new Vector2(0.5f, 0.5f));
    }

    private void Update()
    {
        if (shadowObj == null) return;
        
        // Keep shadow at feet even if parent rotates
        shadowObj.transform.localPosition = new Vector3(0, -footOffset, 0.05f);
        shadowObj.transform.rotation = Quaternion.identity; 
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
}

