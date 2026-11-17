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
        
        [Header("Shadow Transform (Scene-Specific)")]
        [SerializeField] private bool useCustomTransform = false;
        [SerializeField] private Vector3 shadowLocalPosition = Vector3.zero;
        [SerializeField] private Vector3 shadowLocalScale = Vector3.one;

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
                    
                    // Apply custom transform only on creation
                    if (useCustomTransform)
                    {
                        shadowObject.transform.localPosition = shadowLocalPosition;
                        shadowObject.transform.localScale = shadowLocalScale;
                    }
                    else
                    {
                        // Default shadow positioning
                        shadowObject.transform.localPosition = Vector3.zero;
                        shadowObject.transform.localScale = Vector3.one;
                    }
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
            // Check if shadow object is still valid; reinitialize if lost
            if (shadowObject == null || sourceRenderer == null || shadowRenderer == null)
            {
                Initialize();
                return;
            }

            UpdateShadow();
        }

        private void UpdateShadow()
        {
            if (shadowRenderer == null || sourceRenderer == null) return;

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

            // 4. PRESERVE custom transform if enabled - do NOT reset it every frame
            if (useCustomTransform)
            {
                // Only update transform if inspector values changed
                if (shadowObject.transform.localPosition != shadowLocalPosition || 
                    shadowObject.transform.localScale != shadowLocalScale)
                {
                    shadowObject.transform.localPosition = shadowLocalPosition;
                    shadowObject.transform.localScale = shadowLocalScale;
                }
            }
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
