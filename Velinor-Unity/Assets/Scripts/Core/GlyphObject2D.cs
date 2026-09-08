using UnityEngine;

namespace Velinor.Core
{
    /// <summary>
    /// 2D version of GlyphObject - flat sprite glyph that player can collect.
    /// Rotates in Z-axis and adds glyph to codex on player collision.
    /// Uses 2D collider for visual consistency with 2D background.
    /// </summary>
    public class GlyphObject2D : MonoBehaviour
    {
        [SerializeField] private float rotationSpeed = 45f;  // Degrees per second
        [SerializeField] private GlyphData glyphData;

        private bool hasBeenCollected = false;

        private void Start()
        {
            // Verify SphereCollider is set as trigger
            SphereCollider collider = GetComponent<SphereCollider>();
            if (collider != null && !collider.isTrigger)
            {
                collider.isTrigger = true;
            }
        }

        private void Update()
        {
            // Rotate around Y-axis (coin flip motion - like rotating between fingers)
            transform.Rotate(0, rotationSpeed * Time.deltaTime, 0);

            // Create coin-flip illusion by scaling Y based on Y rotation
            // At 0°/180°: full height; at 90°/270°: edge-on (nearly invisible)
            float rotationY = transform.eulerAngles.y;
            float rotationRadians = rotationY * Mathf.Deg2Rad;
            float yScale = Mathf.Abs(Mathf.Cos(rotationRadians));

            Vector3 currentScale = transform.localScale;
            currentScale.y = yScale;
            transform.localScale = currentScale;
        }

        private void OnTriggerEnter(Collider collision)
        {
            Debug.Log($"[GlyphObject2D] 3D collision detected with: {collision.gameObject.name}, Tag: {collision.tag}");

            // Check if the object that entered has a tag or component indicating it's the player
            if (collision.CompareTag("Player") || collision.GetComponent<PlayerController>() != null)
            {
                Debug.Log("[GlyphObject2D] Player detected! Collecting...");
                CollectGlyph();
            }
            else
            {
                Debug.Log($"[GlyphObject2D] Collision with {collision.gameObject.name} but not player");
            }
        }

        private void CollectGlyph()
        {
            if (hasBeenCollected)
            {
                Debug.Log($"[GlyphObject2D] {gameObject.name} already collected.");
                return;
            }

            if (glyphData == null)
            {
                Debug.LogError($"[GlyphObject2D] {gameObject.name} has NO glyph data assigned! Check prefab inspector.");
                return;
            }

            // Find CodexController
            CodexController codex = Object.FindAnyObjectByType<CodexController>();
            if (codex != null)
            {
                Debug.Log($"[GlyphObject2D] CodexController found. Adding glyph: {glyphData.glyphName}");
                codex.AddGlyph(glyphData);
                Debug.Log($"[GlyphObject2D] Successfully added {glyphData.glyphName} to codex");

                hasBeenCollected = true;

                // Destroy the glyph object after collection
                Destroy(gameObject);
            }
            else
            {
                Debug.LogError("[GlyphObject2D] CodexController NOT FOUND in scene! Make sure it exists.");
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
