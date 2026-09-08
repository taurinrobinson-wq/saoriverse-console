using UnityEngine;

namespace Velinor.Core
{
    /// <summary>
    /// 3D version of GlyphObject - spinning hexahedron glyph that player can collect.
    /// Rotates continuously around Y-axis and adds glyph to codex on player collision.
    /// </summary>
    public class GlyphObject3D : MonoBehaviour
    {
        [SerializeField] private float rotationSpeed = 45f;  // Degrees per second
        [SerializeField] private GlyphData glyphData;

        private bool hasBeenCollected = false;

        private void Start()
        {
            // Mesh and collider should already be set up in the prefab
            // Just verify the collider is set as trigger
            MeshCollider meshCollider = GetComponent<MeshCollider>();
            if (meshCollider != null && !meshCollider.isTrigger)
            {
                meshCollider.isTrigger = true;
            }
        }

        private void Update()
        {
            // Rotate continuously around Y-axis
            transform.Rotate(0, rotationSpeed * Time.deltaTime, 0);
        }

        private void OnTriggerEnter(Collider other)
        {
            Debug.Log($"[GlyphObject3D] Collision detected with: {other.gameObject.name}, Tag: {other.tag}");

            // Check if the object that entered has a tag or component indicating it's the player
            if (other.CompareTag("Player") || other.GetComponent<PlayerController>() != null)
            {
                Debug.Log("[GlyphObject3D] Player detected! Collecting...");
                CollectGlyph();
            }
            else
            {
                Debug.Log($"[GlyphObject3D] Collision with {other.gameObject.name} but not player");
            }
        }

        private void CollectGlyph()
        {
            if (hasBeenCollected)
            {
                return;
            }

            if (glyphData == null)
            {
                Debug.LogError($"[GlyphObject3D] {gameObject.name} has no glyph data assigned!");
                return;
            }

            // Find CodexController
            CodexController codex = Object.FindAnyObjectByType<CodexController>();
            if (codex != null)
            {
                codex.AddGlyph(glyphData);
                Debug.Log($"[GlyphObject3D] Collected {glyphData.glyphName}");

                hasBeenCollected = true;

                // Destroy the glyph object after collection
                Destroy(gameObject);
            }
            else
            {
                Debug.LogError("[GlyphObject3D] CodexController not found in scene!");
            }
        }

        private void OnDrawGizmosSelected()
        {
            // Visualize collection range
            Gizmos.color = Color.yellow;
            Gizmos.DrawWireSphere(transform.position, 0.5f);
        }
    }
}
