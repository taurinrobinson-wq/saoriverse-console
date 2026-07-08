using UnityEngine;

[RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
public class TorusGenerator : MonoBehaviour
{
    public float R = 2f;       // Major radius (distance from center to middle of the tube)
    public float r = 0.5f;     // Minor radius (radius of the tube)
    public int segments = 32;  // Segments around the main ring
    public int tubes = 16;     // Segments around the tubular cross-section

    void Start()
    {
        GenerateTorus();
    }

    void GenerateTorus()
    {
        Mesh mesh = new Mesh();
        mesh.name = "GeneratedTorus";

        int vertexCount = (segments + 1) * (tubes + 1);
        Vector3[] vertices = new Vector3[vertexCount];
        Vector2[] uv = new Vector2[vertexCount];
        int[] triangles = new int[segments * tubes * 6];

        int vIndex = 0;
        int tIndex = 0;

        // Calculate Vertices and UV Mapping
        for (int s = 0; s <= segments; s++)
        {
            float theta = (float)s / segments * 2f * Mathf.PI;
            float cosTheta = Mathf.Cos(theta);
            float sinTheta = Mathf.Sin(theta);

            for (int t = 0; t <= tubes; t++)
            {
                float phi = (float)t / tubes * 2f * Mathf.PI;
                float cosPhi = Mathf.Cos(phi);
                float sinPhi = Mathf.Sin(phi);

                // Parametric torus math
                float x = cosTheta * (R + r * cosPhi);
                float z = sinTheta * (R + r * cosPhi);
                float y = r * sinPhi;

                vertices[vIndex] = new Vector3(x, y, z);
                uv[vIndex] = new Vector2((float)s / segments, (float)t / tubes);
                vIndex++;
            }
        }

        // Build Triangles
        for (int s = 0; s < segments; s++)
        {
            for (int t = 0; t < tubes; t++)
            {
                int current = s * (tubes + 1) + t;
                int next = current + tubes + 1;

                // Triangle 1
                triangles[tIndex++] = current;
                triangles[tIndex++] = current + 1;
                triangles[tIndex++] = next;

                // Triangle 2
                triangles[tIndex++] = next;
                triangles[tIndex++] = current + 1;
                triangles[tIndex++] = next + 1;
            }
        }

        // Assign to mesh
        mesh.vertices = vertices;
        mesh.triangles = triangles;
        mesh.uv = uv;

        // Automatically fix lighting normals and boundaries
        mesh.RecalculateNormals();
        mesh.RecalculateBounds();

        // Apply to GameObject
        GetComponent<MeshFilter>().mesh = mesh;
    }
}
