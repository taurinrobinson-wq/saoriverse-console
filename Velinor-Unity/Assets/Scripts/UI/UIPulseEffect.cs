using UnityEngine;
using UnityEngine.UI;

namespace Velinor.UI
{
    public class UIPulseEffect : MonoBehaviour
    {
        [Header("Pulse Settings")]
        [SerializeField] private float pulseSpeed = 1f;
        [SerializeField] private float minAlpha = 0.4f;
        [SerializeField] private float maxAlpha = 1f;
        [SerializeField] private float minScale = 0.95f;
        [SerializeField] private float maxScale = 1.05f;
        
        [Header("Components")]
        [SerializeField] private Image targetImage;
        
        private RectTransform rectTransform;
        
        private void Awake()
        {
            if (targetImage == null) targetImage = GetComponent<Image>();
            rectTransform = GetComponent<RectTransform>();
        }
        
        private void Update()
        {
            float t = (Mathf.Sin(Time.time * pulseSpeed) + 1f) / 2f;
            
            // Pulse Alpha
            if (targetImage != null)
            {
                Color c = targetImage.color;
                c.a = Mathf.Lerp(minAlpha, maxAlpha, t);
                targetImage.color = c;
            }
            
            // Pulse Scale
            if (rectTransform != null)
            {
                float s = Mathf.Lerp(minScale, maxScale, t);
                rectTransform.localScale = new Vector3(s, s, s);
            }
        }
    }
}
