using UnityEngine;

namespace Velinor.Utils
{
    /// <summary>
    /// Creates a grounded silhouette shadow based on a SpriteRenderer's current sprite.
    /// Values are driven via the inspector to allow for scene-specific light angle adjustments.
    /// </summary>
    [ExecuteAlways]
    public class SpriteShadow : MonoBehaviour
    {
        [Header("Appearance")]
        [SerializeField] private Color shadowColor = new Color(0, 0, 0, 0.4f);
        [SerializeField] private string sortingLayerName = "";
        [SerializeField] private int sortingOrderOffset = -1;

        [Header("Transform (Drives the Shadow Visual)")]
        [Tooltip("Local offset from character root. Use Z to stay behind character.")]
        [SerializeField] private Vector3 shadowOffset = new Vector3(-0.3f, 0f, 0.05f);
        
        [Tooltip("Skew multiplier relative to character scale. Y usually small for 'flat' look.")]
        [SerializeField] private Vector3 shadowScale = new Vector3(2.5f, 0.5f, 1f);
        
        [Tooltip("Rotation for sun angle skewing.")]
        [SerializeField] private Vector3 shadowRotation = new Vector3(0, 0, -45f);

        private SpriteRenderer sourceRenderer;
        private SpriteRenderer shadowRenderer;
        private GameObject shadowObject;
        private Material shadowMaterial;

        private void OnEnable()
        {
            Initialize();
        }

        private void Initialize()
        {
            sourceRenderer = GetComponent<SpriteRenderer>();
            if (sourceRenderer == null) sourceRenderer = GetComponentInChildren<SpriteRenderer>();
            
            if (sourceRenderer == null) return;

            // Manage shadow object without constant destruction
            if (shadowObject == null)
            {
                Transform existing = transform.Find("SpriteShadow_Visual");
                if (existing != null)
                {
                    shadowObject = existing.gameObject;
                }
                else
                {
                    shadowObject = new GameObject("SpriteShadow_Visual");
                    shadowObject.transform.SetParent(transform);
                }
            }

            // Keep it visible in hierarchy for now to confirm existence
            shadowObject.hideFlags = HideFlags.None; 

            shadowRenderer = shadowObject.GetComponent<SpriteRenderer>();
            if (shadowRenderer == null) shadowRenderer = shadowObject.AddComponent<SpriteRenderer>();

            if (shadowMaterial == null)
            {
                Shader silhouetteShader = Shader.Find("Custom/SpriteSilhouette");
                if (silhouetteShader != null)
                {
                    shadowMaterial = new Material(silhouetteShader);
                    shadowMaterial.name = "SpriteShadow_Material_Instance";
                    shadowMaterial.hideFlags = HideFlags.HideAndDontSave;
                }
            }

            if (shadowMaterial != null) shadowRenderer.sharedMaterial = shadowMaterial;
            
            UpdateShadow();
        }

        private void LateUpdate()
        {
            if (sourceRenderer == null || shadowRenderer == null || shadowObject == null)
            {
                Initialize();
                return;
            }

            UpdateShadow();
        }

        private void UpdateShadow()
        {
            // 1. Sync Visuals
            shadowRenderer.sprite = sourceRenderer.sprite;
            shadowRenderer.flipX = sourceRenderer.flipX;
            shadowRenderer.flipY = sourceRenderer.flipY;

            if (shadowRenderer.sprite == null) return;

            // 2. Sync Sorting
            shadowRenderer.sortingLayerName = string.IsNullOrEmpty(sortingLayerName) ? sourceRenderer.sortingLayerName : sortingLayerName;
            shadowRenderer.sortingOrder = sourceRenderer.sortingOrder + sortingOrderOffset;

            // 3. Sync Properties via MaterialPropertyBlock (no leaks)
            MaterialPropertyBlock mpb = new MaterialPropertyBlock();
            shadowRenderer.GetPropertyBlock(mpb);
            mpb.SetColor("_BaseColor", shadowColor);
            shadowRenderer.SetPropertyBlock(mpb);

            // 4. Sync Transform
            // We use the inspector fields as the source of truth for the child object.
            // This 'locks' the child object's transform to whatever you type in the inspector,
            // which prevents prefab/scene drift while giving you full control.
            
            Vector3 characterScale = sourceRenderer.transform.localScale;
            shadowObject.transform.localScale = new Vector3(
                characterScale.x * shadowScale.x,
                characterScale.y * shadowScale.y,
                1f
            );

            shadowObject.transform.localPosition = new Vector3(
                sourceRenderer.transform.localPosition.x + shadowOffset.x,
                shadowOffset.y,
                shadowOffset.z
            );

            shadowObject.transform.localRotation = Quaternion.Euler(shadowRotation);
        }

        private void OnDisable()
        {
            // Do NOT destroy the shadowObject here - let Unity manage it in the scene/prefab.
            // This prevents the 'MissingReference' and 'SerializedObject' errors in the inspector.
        }

        private void OnDestroy()
        {
            if (shadowMaterial != null)
            {
                if (Application.isPlaying) Destroy(shadowMaterial);
                else DestroyImmediate(shadowMaterial);
            }
        }
    }
}
