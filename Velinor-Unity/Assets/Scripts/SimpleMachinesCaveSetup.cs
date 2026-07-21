using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Rendering;

/// <summary>
/// Simple manual setup for machines cave scene.
/// Just drag this onto an empty GameObject and configure in Inspector.
/// </summary>
public class SimpleMachinesCaveSetup : MonoBehaviour
{
    [Header("Background Image")]
    [SerializeField] private Texture2D backgroundImage;

    [Header("Scene Setup")]
    [SerializeField] private bool setupOnStart = true;

    private void Start()
    {
        if (setupOnStart)
        {
            SetupScene();
        }
    }

    public void SetupScene()
    {
        // Set ambient lighting
        RenderSettings.ambientLight = new Color(0.2f, 0.3f, 0.35f) * 0.5f;
        RenderSettings.ambientMode = AmbientMode.Flat;

        // Position main camera correctly
        Camera mainCamera = Camera.main;
        if (mainCamera != null)
        {
            mainCamera.transform.position = new Vector3(0, 1.5f, -8f);
            mainCamera.fieldOfView = 60f;
        }

        // Create main light
        GameObject lightObj = new GameObject("MainLight");
        Light mainLight = lightObj.AddComponent<Light>();
        mainLight.type = LightType.Directional;
        mainLight.intensity = 0.4f;
        mainLight.color = Color.white;
        lightObj.transform.rotation = Quaternion.Euler(45f, -30f, 0f);

        // Create background quad if image assigned
        if (backgroundImage != null)
        {
            SetupBackground();
        }

        Debug.Log("Cave scene setup complete! Cylinders should be at (-3,0,0) and (3,0,0)");
    }

    private void SetupBackground()
    {
        // Create quad for background
        GameObject quadObj = new GameObject("BackgroundQuad");
        quadObj.transform.position = new Vector3(0, 0, 100);

        MeshFilter meshFilter = quadObj.AddComponent<MeshFilter>();
        MeshRenderer meshRenderer = quadObj.AddComponent<MeshRenderer>();

        // Create plane mesh
        Mesh mesh = new Mesh();
        float aspectRatio = (float)backgroundImage.width / backgroundImage.height;

        // Make background VERY large to fill viewport (50 units tall)
        Vector3[] vertices = new Vector3[]
        {
            new Vector3(-aspectRatio * 25, -25, 0),
            new Vector3(aspectRatio * 25, -25, 0),
            new Vector3(-aspectRatio * 25, 25, 0),
            new Vector3(aspectRatio * 25, 25, 0)
        };

        int[] triangles = new int[] { 0, 2, 1, 1, 2, 3 };
        Vector2[] uv = new Vector2[] { new Vector2(0, 0), new Vector2(1, 0), new Vector2(0, 1), new Vector2(1, 1) };

        mesh.vertices = vertices;
        mesh.triangles = triangles;
        mesh.uv = uv;
        mesh.RecalculateNormals();

        meshFilter.mesh = mesh;

        // Create material
        Material backgroundMat = new Material(Shader.Find("Standard"));
        backgroundMat.mainTexture = backgroundImage;
        backgroundMat.SetFloat("_Glossiness", 0);
        meshRenderer.material = backgroundMat;
    }
}
