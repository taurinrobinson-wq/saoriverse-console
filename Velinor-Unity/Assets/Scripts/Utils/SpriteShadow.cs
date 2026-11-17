using UnityEngine;

namespace Velinor.Utils
{
    /// <summary>
    /// Creates a grounded silhouette shadow based on a SpriteRenderer's current sprite.
    /// Values are driven via the inspector to allow for scene-specific light angle adjustments.
    /// 
    /// IMPORTANT: This script disables itself at runtime to preserve manually-set shadow transforms.
    /// All setup happens in the editor only.
    /// </summary>
    [ExecuteAlways]
    public class SpriteShadow : MonoBehaviour
    {
        [Header("Appearance")]
        [SerializeField] private Color shadowColor = new Color(0, 0, 0, 0.4f);
        [SerializeField] private string sortingLayerName = "";
        [SerializeField] private int sortingOrderOffset = -1;

        private SpriteRenderer sourceRenderer;
        private SpriteRenderer shadowRenderer;
        private GameObject shadowObject;
        private Material shadowMaterial;

        private void Awake()
        {
            // Disable this script immediately in play mode - we don't want it running at runtime
            if (Application.isPlaying)
            {
                this.enabled = false;
                return;
            }
        }

        private void OnEnable()
        {
            // Safety check: if we somehow got enabled in play mode, disable immediately
            if (Application.isPlaying)
            {
                this.enabled = false;
                return;
            }

            Initialize();
        }

        private void Initialize()
        {
            sourceRenderer = GetComponent<SpriteRenderer>();
            if (sourceRenderer == null) sourceRenderer = GetComponentInChildren<SpriteRenderer>();
            
            if (sourceRenderer == null) return;

            // Find or create shadow object
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

            shadowObject.hideFlags = HideFlags.None;

            // Set up renderer component
            shadowRenderer = shadowObject.GetComponent<SpriteRenderer>();
            if (shadowRenderer == null) 
            {
                shadowRenderer = shadowObject.AddComponent<SpriteRenderer>();
            }

            // Set up material
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

            if (shadowMaterial != null) 
            {
                shadowRenderer.sharedMaterial = shadowMaterial;
            }
            
            UpdateShadow();
        }

        private void LateUpdate()
        {
            // Safety: if running and not disabled yet, disable now
            if (Application.isPlaying)
            {
                this.enabled = false;
                return;
            }

            // Reinitialize only if components are missing
            if (shadowObject == null || sourceRenderer == null || shadowRenderer == null)
            {
                Initialize();
                return;
            }

            UpdateShadow();
        }

        private void UpdateShadow()
        {
            if (shadowRenderer == null || sourceRenderer == null) 
                return;

            // Sync sprite and flip
            shadowRenderer.sprite = sourceRenderer.sprite;
            shadowRenderer.flipX = sourceRenderer.flipX;
            shadowRenderer.flipY = sourceRenderer.flipY;

            if (shadowRenderer.sprite == null) 
                return;

            // Sync sorting
            shadowRenderer.sortingLayerName = string.IsNullOrEmpty(sortingLayerName) 
                ? sourceRenderer.sortingLayerName 
                : sortingLayerName;
            shadowRenderer.sortingOrder = sourceRenderer.sortingOrder + sortingOrderOffset;

            // Sync material color
            MaterialPropertyBlock mpb = new MaterialPropertyBlock();
            shadowRenderer.GetPropertyBlock(mpb);
            mpb.SetColor("_BaseColor", shadowColor);
            shadowRenderer.SetPropertyBlock(mpb);
        }

        private void OnDisable()
        {
            // Don't destroy shadow - let Unity manage scene hierarchy
        }

        private void OnDestroy()
        {
            if (shadowMaterial != null)
            {
                if (Application.isPlaying) 
                    Destroy(shadowMaterial);
                else 
                    DestroyImmediate(shadowMaterial);
            }
        }
    }
}
