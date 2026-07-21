using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Rendering;

/// <summary>
/// Automatically sets up the machines cave scene with background image and visual effects.
/// Attach to an empty GameObject in the scene to initialize on Start.
/// </summary>
public class MachinesCaveSceneSetup : MonoBehaviour
{
    [Header("Background Settings")]
    [SerializeField] private Texture2D backgroundImage;
    [SerializeField] private float backgroundDistance = 100f;
    [SerializeField] private bool useCanvasBackground = false;

    [Header("Lighting")]
    [SerializeField] private Color ambientLightColor = new Color(0.2f, 0.3f, 0.35f);
    [SerializeField] private float ambientIntensity = 0.5f;

    [Header("Machine Left Setup")]
    [SerializeField] private GameObject machineLeftPrefab;
    [SerializeField] private Vector3 machineLeftPosition = new Vector3(-3f, 0f, 0f);

    [Header("Machine Right Setup")]
    [SerializeField] private GameObject machineRightPrefab;
    [SerializeField] private Vector3 machineRightPosition = new Vector3(3f, 0f, 0f);

    [Header("Wires Setup")]
    [SerializeField] private bool createWires = true;
    [SerializeField] private Material wireMaterial;
    [SerializeField] private float wireWidth = 0.1f;

    private void Start()
    {
        SetupScene();
    }

    public void SetupScene()
    {
        // Set up ambient lighting
        SetupLighting();

        // Set up background
        if (useCanvasBackground)
        {
            SetupCanvasBackground();
        }
        else
        {
            SetupQuadBackground();
        }

        // Set up machines
        SetupMachines();

        // Set up wires connecting machines
        if (createWires)
        {
            SetupWires();
        }
    }

    private void SetupLighting()
    {
        RenderSettings.ambientLight = ambientLightColor * ambientIntensity;
        RenderSettings.ambientMode = AmbientMode.Flat;

        // Create main directional light from the cave opening
        GameObject lightObj = new GameObject("MainLight");
        Light mainLight = lightObj.AddComponent<Light>();
        mainLight.type = LightType.Directional;
        mainLight.intensity = 0.4f;
        mainLight.color = Color.white;
        lightObj.transform.rotation = Quaternion.Euler(45f, -30f, 0f);
    }

    private void SetupCanvasBackground()
    {
        // Create Canvas for UI-based background
        GameObject canvasObj = new GameObject("BackgroundCanvas");
        Canvas canvas = canvasObj.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceCamera;

        // Attach to main camera
        Camera mainCamera = Camera.main;
        if (mainCamera != null)
        {
            canvas.worldCamera = mainCamera;
        }

        // Create Image component for background
        GameObject imageObj = new GameObject("BackgroundImage");
        imageObj.transform.SetParent(canvasObj.transform);

        Image image = imageObj.AddComponent<Image>();
        image.sprite = Sprite.Create(backgroundImage,
            new Rect(0, 0, backgroundImage.width, backgroundImage.height),
            new Vector2(0.5f, 0.5f));

        // Scale to fill screen
        RectTransform rectTransform = imageObj.GetComponent<RectTransform>();
        rectTransform.offsetMin = Vector2.zero;
        rectTransform.offsetMax = Vector2.zero;

        // Set to back
        imageObj.transform.SetAsFirstSibling();
    }

    private void SetupQuadBackground()
    {
        // Create a quad for 3D background
        GameObject quadObj = new GameObject("BackgroundQuad");
        MeshFilter meshFilter = quadObj.AddComponent<MeshFilter>();
        MeshRenderer meshRenderer = quadObj.AddComponent<MeshRenderer>();

        // Create plane mesh
        Mesh mesh = new Mesh();
        float aspectRatio = (float)backgroundImage.width / backgroundImage.height;

        Vector3[] vertices = new Vector3[]
        {
            new Vector3(-aspectRatio * 5, -5, backgroundDistance),
            new Vector3(aspectRatio * 5, -5, backgroundDistance),
            new Vector3(-aspectRatio * 5, 5, backgroundDistance),
            new Vector3(aspectRatio * 5, 5, backgroundDistance)
        };

        int[] triangles = new int[] { 0, 2, 1, 1, 2, 3 };
        Vector2[] uv = new Vector2[] { new Vector2(0, 0), new Vector2(1, 0), new Vector2(0, 1), new Vector2(1, 1) };

        mesh.vertices = vertices;
        mesh.triangles = triangles;
        mesh.uv = uv;
        mesh.RecalculateNormals();

        meshFilter.mesh = mesh;

        // Create material for background
        Material backgroundMat = new Material(Shader.Find("Standard"));
        backgroundMat.mainTexture = backgroundImage;
        backgroundMat.SetFloat("_Glossiness", 0);

        meshRenderer.material = backgroundMat;
    }

    private void SetupMachines()
    {
        if (machineLeftPrefab != null)
        {
            GameObject machineLeft = Instantiate(machineLeftPrefab);
            machineLeft.name = "Machine_Left";
            machineLeft.transform.position = machineLeftPosition;
        }

        if (machineRightPrefab != null)
        {
            GameObject machineRight = Instantiate(machineRightPrefab);
            machineRight.name = "Machine_Right";
            machineRight.transform.position = machineRightPosition;
        }
    }

    private void SetupWires()
    {
        GameObject wiresObj = new GameObject("Wires");
        LineRenderer lineRenderer = wiresObj.AddComponent<LineRenderer>();

        // Set up line renderer
        lineRenderer.material = wireMaterial ?? new Material(Shader.Find("Standard"));
        lineRenderer.startWidth = wireWidth;
        lineRenderer.endWidth = wireWidth;
        lineRenderer.positionCount = 4;

        // Create wire path from left machine to right machine
        lineRenderer.SetPosition(0, machineLeftPosition + Vector3.up * 2f);
        lineRenderer.SetPosition(1, machineLeftPosition + Vector3.forward * 3f + Vector3.up * 3f);
        lineRenderer.SetPosition(2, machineRightPosition + Vector3.forward * 3f + Vector3.up * 3f);
        lineRenderer.SetPosition(3, machineRightPosition + Vector3.up * 2f);

        // Add WireSparks script
        WireSparks wireSparks = wiresObj.AddComponent<WireSparks>();
        wireSparks.GetComponent<LineRenderer>(); // Will be assigned in WireSparks.Start()
    }
}
