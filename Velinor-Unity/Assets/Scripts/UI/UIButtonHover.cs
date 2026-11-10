using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

namespace Velinor.UI
{
    public class UIButtonHover : MonoBehaviour, IPointerEnterHandler, IPointerExitHandler, IPointerDownHandler, IPointerUpHandler
    {
        [Header("Scale Settings")]
        [SerializeField] private float hoverScale = 1.05f;
        [SerializeField] private float clickScale = 0.95f;
        [SerializeField] private float transitionSpeed = 15f;
        
        [Header("Color Settings")]
        [SerializeField] private bool useColorTransition = true;
        [SerializeField] private Color hoverColor = Color.white;
        [SerializeField] private Color clickColor = Color.gray;
        [SerializeField] private Graphic targetGraphic;

        private Vector3 originalScale;
        private Vector3 targetScale;
        private Color originalColor;
        private Color targetColor;
        
        private bool isPointerDown = false;
        private bool isHovering = false;
        
        private void Awake()
        {
            originalScale = transform.localScale;
            targetScale = originalScale;
            
            if (targetGraphic == null)
            {
                targetGraphic = GetComponent<Graphic>();
                if (targetGraphic == null) targetGraphic = GetComponentInChildren<Graphic>();
            }
            
            if (targetGraphic != null)
            {
                originalColor = targetGraphic.color;
                targetColor = originalColor;
            }
        }
        
        private void Update()
        {
            transform.localScale = Vector3.Lerp(transform.localScale, targetScale, Time.deltaTime * transitionSpeed);
            
            if (useColorTransition && targetGraphic != null)
            {
                targetGraphic.color = Color.Lerp(targetGraphic.color, targetColor, Time.deltaTime * transitionSpeed);
            }
        }
        
        public void OnPointerEnter(PointerEventData eventData)
        {
            isHovering = true;
            UpdateVisualState();
        }
        
        public void OnPointerExit(PointerEventData eventData)
        {
            isHovering = false;
            UpdateVisualState();
        }
        
        public void OnPointerDown(PointerEventData eventData)
        {
            isPointerDown = true;
            UpdateVisualState();
        }
        
        public void OnPointerUp(PointerEventData eventData)
        {
            isPointerDown = false;
            UpdateVisualState();
        }
        
        private void UpdateVisualState()
        {
            if (isPointerDown)
            {
                targetScale = originalScale * clickScale;
                targetColor = clickColor;
            }
            else if (isHovering)
            {
                targetScale = originalScale * hoverScale;
                targetColor = hoverColor;
            }
            else
            {
                targetScale = originalScale;
                targetColor = originalColor;
            }
        }
        
        private void OnDisable()
        {
            transform.localScale = originalScale;
            targetScale = originalScale;
            if (targetGraphic != null)
            {
                targetGraphic.color = originalColor;
                targetColor = originalColor;
            }
            isPointerDown = false;
            isHovering = false;
        }
    }
}