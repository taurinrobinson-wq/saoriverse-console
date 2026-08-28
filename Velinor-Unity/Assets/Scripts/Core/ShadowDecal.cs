using UnityEngine;

/// <summary>
/// Adds a dynamic shadow decal under a character/object in 2.5D games.
/// The shadow fades based on height above the ground plane.
/// Attach to any character or glyph that needs a shadow.
/// </summary>
public class ShadowDecal : MonoBehaviour
{
    [Header("Shadow Settings")]
    [SerializeField] private float shadowHeight = 0.01f; // How far above ground the shadow is positioned
    [SerializeField] private float shadowScale = 1.5f; // Size of shadow quad
    [SerializeField] private float maxHeightForShadow = 3f; // Height at which shadow becomes invisible
    [SerializeField] private Color shadowColor = new Color(0, 0, 0, 0.6f); // Shadow color with alpha
    [SerializeField] private Texture2D shadowTexture; // Circular gradient shadow texture

    private GameObject shadowQuad;
    private MeshRenderer shadowRenderer;
    private Material shadowMaterial;
    private float baseY;

    private void Start()
    {
        CreateShadowDecal();
        baseY = transform.position.y;
    }

    private void CreateShadowDecal()
    {
        // Create a simple quad for the shadow
        shadowQuad = new GameObject("ShadowDecal");
        shadowQuad.transform.SetParent(transform);
        shadowQuad.transform.localPosition = new Vector3(0, -shadowHeight, 0.1f); // Slightly in front of character
        shadowQuad.transform.localRotation = Quaternion.Euler(90, 0, 0); // Rotate to lie flat on ground
        shadowQuad.transform.localScale = new Vector3(shadowScale, 1f, shadowScale);

        // Add mesh filter and renderer
        MeshFilter meshFilter = shadowQuad.AddComponent<MeshFilter>();
        shadowRenderer = shadowQuad.AddComponent<MeshRenderer>();

        // Create a simple quad mesh
        meshFilter.mesh = CreateQuadMesh();

        // Create shadow material
        if (shadowTexture == null)
        {
            // Create a simple white texture if none provided
            shadowTexture = new Texture2D(64, 64, TextureFormat.ARGB32, false);
            FillWithRadialGradient(shadowTexture);
        }

        // Use URP Unlit shader for transparency
        Shader unlitShader = Shader.Find("Universal Render Pipeline/Unlit");
        if (unlitShader == null)
            unlitShader = Shader.Find("Unlit/Transparent");

        shadowMaterial = new Material(unlitShader);
        shadowMaterial.name = "ShadowMaterial";
        shadowMaterial.SetTexture("_BaseMap", shadowTexture);
        shadowMaterial.SetColor("_BaseColor", shadowColor);
        shadowMaterial.SetFloat("_Surface", 1); // Transparent surface
        shadowMaterial.SetFloat("_Blend", 0); // Alpha blend
        shadowMaterial.SetInt("_SrcBlend", (int)UnityEngine.Rendering.BlendMode.SrcAlpha);
        shadowMaterial.SetInt("_DstBlend", (int)UnityEngine.Rendering.BlendMode.OneMinusSrcAlpha);
        shadowMaterial.SetInt("_ZWrite", 0);
        shadowMaterial.renderQueue = 3000;

        shadowRenderer.material = shadowMaterial;

        // Hide shadow in editor
        shadowQuad.hideFlags = HideFlags.HideInHierarchy;
    }

    private Mesh CreateQuadMesh()
    {
        Mesh mesh = new Mesh();
        mesh.name = "ShadowQuad";

        Vector3[] vertices = new Vector3[]
        {
            new Vector3(-0.5f, 0, -0.5f),
            new Vector3(0.5f, 0, -0.5f),
            new Vector3(0.5f, 0, 0.5f),
            new Vector3(-0.5f, 0, 0.5f)
        };

        int[] triangles = new int[] { 0, 2, 1, 0, 3, 2 };

        Vector2[] uv = new Vector2[]
        {
            new Vector2(0, 0),
            new Vector2(1, 0),
            new Vector2(1, 1),
            new Vector2(0, 1)
        };

        mesh.vertices = vertices;
        mesh.triangles = triangles;
        mesh.uv = uv;
        mesh.RecalculateNormals();
        return mesh;
    }

    private void FillWithRadialGradient(Texture2D texture)
    {
        Color[] pixels = new Color[texture.width * texture.height];
        Vector2 center = new Vector2(texture.width / 2f, texture.height / 2f);
        float maxDistance = Vector2.Distance(Vector2.zero, center);

        for (int y = 0; y < texture.height; y++)
        {
            for (int x = 0; x < texture.width; x++)
            {
                Vector2 pixelPos = new Vector2(x, y);
                float distance = Vector2.Distance(pixelPos, center);
                float alpha = 1f - (distance / maxDistance);
                alpha = Mathf.Clamp01(alpha);
                pixels[y * texture.width + x] = new Color(0, 0, 0, alpha);
            }
        }

        texture.SetPixels(pixels);
        texture.Apply();
    }

    private void Update()
    {
        if (shadowQuad == null)
            return;

        // Calculate height above base ground
        float heightAboveGround = transform.position.y - baseY;

        // Fade shadow based on height
        float shadowAlpha = Mathf.Clamp01(1f - (heightAboveGround / maxHeightForShadow));
        Color shadowColorWithAlpha = shadowColor;
        shadowColorWithAlpha.a = shadowColor.a * shadowAlpha;
        shadowMaterial.SetColor("_BaseColor", shadowColorWithAlpha);

        // Update shadow position (follow character horizontally)
        shadowQuad.transform.localPosition = new Vector3(0, -shadowHeight, 0.1f);
    }

    public void SetShadowColor(Color newColor)
    {
        shadowColor = newColor;
    }

    public void SetMaxHeight(float newMaxHeight)
    {
        maxHeightForShadow = newMaxHeight;
    }
}
