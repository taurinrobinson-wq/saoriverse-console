using UnityEngine;

public class TorusCargoBoxGenerator : MonoBehaviour
{
    [Header("Torus Parameters")]
    public float torusR = 2f;           // Major radius (same as TorusGenerator.R)
    public float torusR_minor = 0.5f;   // Minor radius (same as TorusGenerator.r)
    public int boxCount = 24;           // Number of boxes around the torus

    [Header("Box Parameters")]
    public Vector3 boxSize = new Vector3(0.3f, 0.2f, 0.3f);
    public Material boxMaterial;

    [Header("Box Positioning")]
    public float distanceFromTorusCenter = 0.7f; // How far boxes extend from torus center

    void Start()
    {
        GenerateCargoBoxes();
    }

    void GenerateCargoBoxes()
    {
        // Create a parent container for all boxes
        GameObject boxContainer = new GameObject("CargoBoxes");
        boxContainer.transform.parent = transform;
        boxContainer.transform.localPosition = Vector3.zero;

        for (int i = 0; i < boxCount; i++)
        {
            // Calculate angle around the torus
            float angle = (float)i / boxCount * 2f * Mathf.PI;

            // Position on the outer edge of the torus
            float posX = Mathf.Cos(angle) * distanceFromTorusCenter;
            float posZ = Mathf.Sin(angle) * distanceFromTorusCenter;
            float posY = 0f; // Boxes positioned at the outer equator of the torus

            // Create box
            GameObject box = GameObject.CreatePrimitive(PrimitiveType.Cube);
            box.name = $"CargoBox_{i}";
            box.transform.parent = boxContainer.transform;
            box.transform.localPosition = new Vector3(posX, posY, posZ);
            box.transform.localScale = boxSize;

            // Remove the default collider (we'll add a transparent one if needed)
            Collider collider = box.GetComponent<Collider>();
            if (collider != null)
            {
                DestroyImmediate(collider);
            }

            // Assign material
            if (boxMaterial != null)
            {
                Renderer renderer = box.GetComponent<Renderer>();
                renderer.material = boxMaterial;
            }

            // Optional: Add a slight rotation to make it look more dynamic
            box.transform.localRotation = Quaternion.Euler(Random.Range(-15f, 15f), angle * Mathf.Rad2Deg, Random.Range(-15f, 15f));
        }
    }
}
