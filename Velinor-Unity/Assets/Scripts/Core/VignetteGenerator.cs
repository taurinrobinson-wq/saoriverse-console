using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(Image))]
public class VignetteGenerator : MonoBehaviour
{
    [Range(0f, 1f)]
    public float intensity = 0.75f;   // how dark the edges are
    public Color vignetteColor = new Color(0.09f, 0.09f, 0.09f, 0.85f); // #181818 with alpha ~218/255

    private Image img;

    void Awake()
    {
        img = GetComponent<Image>();
        img.material = new Material(Shader.Find("UI/Default"));
        img.sprite = GenerateVignetteSprite(512, 512);
        img.type = Image.Type.Simple;
        img.preserveAspect = false;
    }

    Sprite GenerateVignetteSprite(int width, int height)
    {
        Texture2D tex = new Texture2D(width, height, TextureFormat.RGBA32, false);
        tex.wrapMode = TextureWrapMode.Clamp;

        Vector2 center = new Vector2(width / 2f, height / 2f);
        float maxDist = Vector2.Distance(Vector2.zero, center);

        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                float dist = Vector2.Distance(new Vector2(x, y), center);
                float t = Mathf.Clamp01(dist / maxDist);
                float alpha = Mathf.Lerp(0f, vignetteColor.a, Mathf.Pow(t, intensity * 2f));

                tex.SetPixel(x, y, new Color(vignetteColor.r, vignetteColor.g, vignetteColor.b, alpha));
            }
        }

        tex.Apply();
        return Sprite.Create(tex, new Rect(0, 0, width, height), new Vector2(0.5f, 0.5f));
    }
}
