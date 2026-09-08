using UnityEngine;

namespace Velinor.Core
{
    /// <summary>
    /// Utility for creating 3D sphere glyphs from 2D artwork.
    /// Uses Unity's built-in sphere primitive for simplicity and proper 3D appearance.
    /// </summary>
    public class Glyph3DGenerator
    {
        /// <summary>
        /// Gets Unity's built-in sphere mesh.
        /// </summary>
        public static Mesh CreateCubeMesh()
        {
            // Use Unity's built-in sphere primitive
            GameObject tempSphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            Mesh sphereMesh = tempSphere.GetComponent<MeshFilter>().sharedMesh;

            // Destroy the temp object but keep the mesh reference
            Object.DestroyImmediate(tempSphere);

            return sphereMesh;
        }

        /// <summary>
        /// Creates a material with the specified texture.
        /// Uses URP-compatible shader for proper rendering.
        /// </summary>
        public static Material CreateGlyphMaterial(Texture2D texture, string materialName = "GlyphMaterial")
        {
            // Try URP shader first (for Universal Render Pipeline)
            Shader shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null)
            {
                // Fallback to built-in Standard if URP not available
                shader = Shader.Find("Standard");
            }
            if (shader == null)
            {
                // Last resort: use unlit/texture shader
                shader = Shader.Find("Unlit/Texture");
            }

            Material material = new Material(shader);
            material.name = materialName;

            if (texture != null)
            {
                material.SetTexture("_BaseMap", texture);  // URP parameter
                material.SetTexture("_MainTex", texture);  // Built-in fallback
            }

            material.SetColor("_BaseColor", Color.white);  // URP
            material.SetColor("_Color", Color.white);      // Built-in fallback

            // Enable alpha blending for transparency
            material.SetFloat("_Surface", 1);  // Transparent mode in URP
            material.SetFloat("_Blend", 0);    // Alpha blend
            material.SetInt("_SrcBlend", (int)UnityEngine.Rendering.BlendMode.SrcAlpha);
            material.SetInt("_DstBlend", (int)UnityEngine.Rendering.BlendMode.OneMinusSrcAlpha);
            material.SetInt("_ZWrite", 0);

            // Ensure alpha transparency works
            material.SetFloat("_AlphaClip", 0);
            material.renderQueue = 3000;

            // Set keywords for URP
            material.DisableKeyword("_RECEIVE_SHADOWS_OFF");
            material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
            material.EnableKeyword("_ALPHAPREMULTIPLY_ON");

            return material;
        }
    }
}
