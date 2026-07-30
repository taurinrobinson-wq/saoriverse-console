using UnityEngine;
using UnityEngine.EventSystems;

namespace Velinor.UI
{
    public class UIButtonHover : MonoBehaviour, IPointerEnterHandler, IPointerExitHandler
    {
        [SerializeField] private float hoverScale = 1.05f;
        [SerializeField] private float transitionSpeed = 12f;
        
        private Vector3 originalScale;
        private Vector3 targetScale;
        
        private void Awake()
        {
            originalScale = transform.localScale;
            targetScale = originalScale;
        }
        
        private void Update()
        {
            transform.localScale = Vector3.Lerp(transform.localScale, targetScale, Time.deltaTime * transitionSpeed);
        }
        
        public void OnPointerEnter(PointerEventData eventData)
        {
            targetScale = originalScale * hoverScale;
        }
        
        public void OnPointerExit(PointerEventData eventData)
        {
            targetScale = originalScale;
        }
        
        private void OnDisable()
        {
            transform.localScale = originalScale;
            targetScale = originalScale;
        }
    }
}