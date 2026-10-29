using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using System.Collections;

namespace Velinor.UI.MemoryPuzzle
{
    public class MemoryReconstructionCandidate : MonoBehaviour, IBeginDragHandler, IDragHandler, IEndDragHandler
    {
        [SerializeField] private string candidateID;
        public string CandidateID => candidateID;

        public RectTransform Rect => _rectTransform;
        public MemoryReconstructionSlot CurrentSlot { get; private set; }

        private RectTransform _rectTransform;
        private CanvasGroup _canvasGroup;
        private MemoryReconstructionController _controller;
        
        private Vector2 _originalPosition;
        private Vector2 _startDragPos;
        private Vector2 _dragScale = new Vector2(300, 300);
        private Vector2 _normalScale = new Vector2(180, 180);
        
        private Coroutine _scaleCoroutine;

        private void Awake()
        {
            _rectTransform = GetComponent<RectTransform>();
            _canvasGroup = GetComponent<CanvasGroup>();
            if (_canvasGroup == null) _canvasGroup = gameObject.AddComponent<CanvasGroup>();
            
            _controller = GetComponentInParent<MemoryReconstructionController>();
            _originalPosition = _rectTransform.anchoredPosition;
        }

        public void OnBeginDrag(PointerEventData eventData)
        {
            if (CurrentSlot != null)
            {
                CurrentSlot.ClearSlot();
                CurrentSlot = null;
            }

            transform.SetAsLastSibling(); // Bring to front
            _canvasGroup.blocksRaycasts = false;
            
            if (_scaleCoroutine != null) StopCoroutine(_scaleCoroutine);
            _scaleCoroutine = StartCoroutine(ScaleTo(_dragScale, 0.2f));
            
            _controller.CheckCompletion();
        }

        public void OnDrag(PointerEventData eventData)
        {
            _rectTransform.anchoredPosition += eventData.delta / _controller.CanvasScaleFactor;
        }

        public void OnEndDrag(PointerEventData eventData)
        {
            _canvasGroup.blocksRaycasts = true;

            // Simple proximity check for slots
            MemoryReconstructionSlot nearest = FindNearestAvailableSlot();
            if (nearest != null)
            {
                SnapToSlot(nearest);
            }
            else
            {
                ReturnToOriginalPosition();
            }
            
            _controller.CheckCompletion();
        }

        private MemoryReconstructionSlot FindNearestAvailableSlot()
        {
            MemoryReconstructionSlot left = _controller.slotLeft.GetComponent<MemoryReconstructionSlot>();
            MemoryReconstructionSlot right = _controller.slotRight.GetComponent<MemoryReconstructionSlot>();
            
            float distLeft = Vector3.Distance(transform.position, _controller.slotLeft.position);
            float distRight = Vector3.Distance(transform.position, _controller.slotRight.position);
            
            // Proximity threshold in pixel space (Screen Space Overlay)
            float threshold = 150f; 
            
            if (distLeft < distRight && distLeft < threshold && !left.IsOccupied) return left;
            if (distRight < distLeft && distRight < threshold && !right.IsOccupied) return right;
            
            return null;
        }

        public void SnapToSlot(MemoryReconstructionSlot slot)
        {
            CurrentSlot = slot;
            slot.AssignCandidate(this);
            
            // Snap world position to slot center
            transform.position = slot.transform.position;
            
            if (_scaleCoroutine != null) StopCoroutine(_scaleCoroutine);
            _rectTransform.sizeDelta = _dragScale; 
        }

        public void ReturnToOriginalPosition(bool immediate = false)
        {
            if (CurrentSlot != null) CurrentSlot.ClearSlot();
            CurrentSlot = null;
            
            _rectTransform.anchoredPosition = _originalPosition;
            
            if (immediate)
            {
                _rectTransform.sizeDelta = _normalScale;
            }
            else
            {
                if (_scaleCoroutine != null) StopCoroutine(_scaleCoroutine);
                _scaleCoroutine = StartCoroutine(ScaleTo(_normalScale, 0.2f));
            }
        }

        public void SetOriginalPosition(Vector2 pos)
        {
            _originalPosition = pos;
        }

        private IEnumerator ScaleTo(Vector2 targetSize, float duration)
        {
            Vector2 startSize = _rectTransform.sizeDelta;
            float elapsed = 0;
            while (elapsed < duration)
            {
                _rectTransform.sizeDelta = Vector2.Lerp(startSize, targetSize, elapsed / duration);
                elapsed += Time.deltaTime;
                yield return null;
            }
            _rectTransform.sizeDelta = targetSize;
        }
    }
}
