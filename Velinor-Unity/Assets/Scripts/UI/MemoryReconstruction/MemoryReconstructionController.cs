using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using System.Collections;
using System.Collections.Generic;
using Velinor.Management;
using Velinor.Core;
using TMPro;

namespace Velinor.UI.MemoryPuzzle
{
    public class MemoryReconstructionController : MonoBehaviour
    {
        [Header("UI Panels")]
        public RectTransform anchorPanel;
        public RectTransform slotLeft;
        public RectTransform slotRight;
        public MemoryReconstructionCandidate candidateA;
        public MemoryReconstructionCandidate candidateB;
        public CanvasGroup buttonGroup;
        public Button lockInButton;
        public Button tryOrderButton;
        public CanvasGroup resultOverlay;
        public TextMeshProUGUI resultText;
        public Button retryButton;

        [Header("Sequence Visualization")]
        public GameObject[] reconstructionSequenceBoxes;
        private CanvasGroup _anchorCanvasGroup;

        [Header("Animation Settings")]
        public float revealDuration = 0.4f;
        public float buttonFadeDuration = 0.4f;
        public float sequenceStepDelay = 0.8f;

        [Header("Sequence Logic")]
        [TextArea] public string anchorText = "Ophina approaches the unstable wall.";
        [TextArea] public string correctMindLog = "Ravi and Nima never mentioned anyone from the market trying to intervene...";
        
        private Canvas _canvas;
        private Coroutine _buttonFadeCoroutine;
        private bool _isRevealed = false;
        
        public float CanvasScaleFactor => _canvas != null ? _canvas.scaleFactor : 1f;

        private void Awake()
        {
            _canvas = GetComponentInParent<Canvas>();
            _anchorCanvasGroup = anchorPanel.GetComponent<CanvasGroup>();
            if (_anchorCanvasGroup == null) _anchorCanvasGroup = anchorPanel.gameObject.AddComponent<CanvasGroup>();
            
            lockInButton.onClick.AddListener(OnLockIn);
            tryOrderButton.onClick.AddListener(OnTryDifferentOrder);
            retryButton.onClick.AddListener(ResetPuzzle);

            AddHoverEffect(lockInButton);
            AddHoverEffect(tryOrderButton);

            Button anchorBtn = anchorPanel.GetComponent<Button>();
            if (anchorBtn == null) anchorBtn = anchorPanel.gameObject.AddComponent<Button>();
            anchorBtn.onClick.RemoveAllListeners();
            anchorBtn.onClick.AddListener(() => StartCoroutine(RevealSequence()));
            
            buttonGroup.alpha = 0;
            buttonGroup.interactable = false;
            buttonGroup.blocksRaycasts = false;

            if (resultOverlay != null)
            {
                resultOverlay.alpha = 0;
                resultOverlay.blocksRaycasts = false;
                resultOverlay.interactable = false;
            }
            
            // Do NOT auto-hide pieces here anymore to allow user setup to show
            SetupSlotVisuals();
        }

        private void OnEnable()
        {
            SetupSlotVisuals();
            
            // Ensure fragments are visible for the user to interact
            if (slotLeft != null) slotLeft.gameObject.SetActive(true);
            if (slotRight != null) slotRight.gameObject.SetActive(true);
            if (candidateA != null) candidateA.gameObject.SetActive(true);
            if (candidateB != null) candidateB.gameObject.SetActive(true);

            if (buttonGroup != null && (candidateA.CurrentSlot == null || candidateB.CurrentSlot == null))
            {
                buttonGroup.alpha = 0;
                buttonGroup.interactable = false;
            }
        }

        private void SetupSlotVisuals()
        {
            SetSlotStyle(slotLeft);
            SetSlotStyle(slotRight);
        }

        private void SetSlotStyle(RectTransform slot)
        {
            if (slot == null) return;
            var img = slot.GetComponent<UnityEngine.UI.Image>();
            if (img != null) img.color = new Color(0, 1, 1, 0.05f); // Mostly transparent

            Transform border = slot.Find("Border");
            if (border != null)
            {
                var bImg = border.GetComponent<UnityEngine.UI.Image>();
                if (bImg != null)
                {
                    bImg.color = new Color(0, 1, 1, 1f); // Solid border
                    bImg.enabled = true;
                }
            }
        }

        private void HideAllPuzzlePieces()
        {
            if (slotLeft != null) slotLeft.gameObject.SetActive(false);
            if (slotRight != null) slotRight.gameObject.SetActive(false);
            if (candidateA != null) candidateA.gameObject.SetActive(false);
            if (candidateB != null) candidateB.gameObject.SetActive(false);

            if (reconstructionSequenceBoxes != null)
            {
                foreach (var box in reconstructionSequenceBoxes)
                {
                    if (box != null) box.SetActive(false);
                }
            }
        }

        private void AddHoverEffect(Button btn)
        {
            EventTrigger trigger = btn.gameObject.GetComponent<EventTrigger>();
            if (trigger == null) trigger = btn.gameObject.AddComponent<EventTrigger>();

            EventTrigger.Entry enter = new EventTrigger.Entry { eventID = EventTriggerType.PointerEnter };
            enter.callback.AddListener((data) => { StartCoroutine(ScaleButton(btn.transform, 1.1f)); });
            trigger.triggers.Add(enter);

            EventTrigger.Entry exit = new EventTrigger.Entry { eventID = EventTriggerType.PointerExit };
            exit.callback.AddListener((data) => { StartCoroutine(ScaleButton(btn.transform, 1.0f)); });
            trigger.triggers.Add(exit);
        }

        private IEnumerator ScaleButton(Transform t, float targetScale)
        {
            float elapsed = 0;
            float duration = 0.15f;
            Vector3 startScale = t.localScale;
            Vector3 endScale = new Vector3(targetScale, targetScale, 1f);

            while (elapsed < duration)
            {
                t.localScale = Vector3.Lerp(startScale, endScale, elapsed / duration);
                elapsed += Time.deltaTime;
                yield return null;
            }
            t.localScale = endScale;
        }

        private IEnumerator RevealSequence()
        {
            if (_isRevealed) yield break;
            _isRevealed = true;

            anchorPanel.GetComponent<Button>().interactable = false;
            
            slotLeft.gameObject.SetActive(true);
            slotRight.gameObject.SetActive(true);
            candidateA.gameObject.SetActive(true);
            candidateB.gameObject.SetActive(true);

            candidateA.ReturnToOriginalPosition(true);
            candidateB.ReturnToOriginalPosition(true);
            
            float elapsed = 0;
            Vector2 startPosA = anchorPanel.anchoredPosition;
            Vector2 startPosB = anchorPanel.anchoredPosition;
            Vector2 endPosA = new Vector2(-230, 38);
            Vector2 endPosB = new Vector2(20, 38);

            while (elapsed < revealDuration)
            {
                float t = elapsed / revealDuration;
                t = 1f - Mathf.Pow(1f - t, 3f);
                
                candidateA.Rect.anchoredPosition = Vector2.Lerp(startPosA, endPosA, t);
                candidateB.Rect.anchoredPosition = Vector2.Lerp(startPosB, endPosB, t);
                
                elapsed += Time.deltaTime;
                yield return null;
            }

            candidateA.Rect.anchoredPosition = endPosA;
            candidateB.Rect.anchoredPosition = endPosB;
            candidateA.SetOriginalPosition(endPosA);
            candidateB.SetOriginalPosition(endPosB);
        }

        public void CheckCompletion()
        {
            if (candidateA.CurrentSlot != null && candidateB.CurrentSlot != null)
            {
                if (_buttonFadeCoroutine != null) StopCoroutine(_buttonFadeCoroutine);
                _buttonFadeCoroutine = StartCoroutine(FadeInButtonGroup());
            }
            else
            {
                if (_buttonFadeCoroutine != null) StopCoroutine(_buttonFadeCoroutine);
                _buttonFadeCoroutine = StartCoroutine(FadeCanvasGroup(buttonGroup, 0f, 0.1f));
            }
        }

        private IEnumerator FadeInButtonGroup()
        {
            RectTransform rt = buttonGroup.GetComponent<RectTransform>();
            Vector2 endPos = new Vector2(0, -200);
            Vector2 startPos = endPos + new Vector2(0, -50);
            
            float elapsed = 0;
            while (elapsed < buttonFadeDuration)
            {
                float t = elapsed / buttonFadeDuration;
                buttonGroup.alpha = t;
                rt.anchoredPosition = Vector2.Lerp(startPos, endPos, t);
                elapsed += Time.deltaTime;
                yield return null;
            }
            buttonGroup.alpha = 1f;
            rt.anchoredPosition = endPos;
            buttonGroup.interactable = true;
            buttonGroup.blocksRaycasts = true;
        }

        private IEnumerator FadeCanvasGroup(CanvasGroup cg, float targetAlpha, float duration)
        {
            if (cg == null) yield break;
            float startAlpha = cg.alpha;
            float elapsed = 0;
            while (elapsed < duration)
            {
                cg.alpha = Mathf.Lerp(startAlpha, targetAlpha, elapsed / duration);
                elapsed += Time.deltaTime;
                yield return null;
            }
            cg.alpha = targetAlpha;
            cg.interactable = targetAlpha > 0.5f;
            cg.blocksRaycasts = targetAlpha > 0.5f;
        }

        private void OnLockIn()
        {
            // Correct Sequence: Left = Marketplace Citizens (Candidate A), Right = Ravi and Nima (Candidate B)
            // Use gameObject comparison because CurrentSlot is a component and slotLeft/Right are RectTransforms
            bool correct = (candidateA.CurrentSlot != null && candidateA.CurrentSlot.gameObject == slotLeft.gameObject &&
                            candidateB.CurrentSlot != null && candidateB.CurrentSlot.gameObject == slotRight.gameObject);
            
            StartCoroutine(PlayReconstruction(correct));
        }

        private IEnumerator PlayReconstruction(bool correct)
        {
            candidateA.enabled = false;
            candidateB.enabled = false;
            lockInButton.interactable = false;
            tryOrderButton.interactable = false;

            // Fade out Anchor Panel
            yield return StartCoroutine(FadeCanvasGroup(_anchorCanvasGroup, 0f, 0.5f));
            anchorPanel.gameObject.SetActive(false);

            // Display sequence boxes one by one
            if (reconstructionSequenceBoxes != null)
            {
                for (int i = 0; i < reconstructionSequenceBoxes.Length; i++)
                {
                    if (reconstructionSequenceBoxes[i] != null)
                    {
                        reconstructionSequenceBoxes[i].SetActive(true);
                        yield return new WaitForSeconds(sequenceStepDelay);
                    }
                }
            }

            if (resultOverlay != null)
            {
                resultOverlay.alpha = 1;
                resultOverlay.blocksRaycasts = true;
                resultOverlay.interactable = true;
                
                if (correct)
                {
                    resultText.text = "Memory Reconstruction Complete\n\n" + correctMindLog;
                    retryButton.gameObject.SetActive(false);
                    
                    var manager = MindLogManager.GetOrCreate();
                    if (manager != null)
                    {
                        MindLogEntry entry = new MindLogEntry("reconstructed_memory_ophina", null, "Memory Reconstruction", correctMindLog);
                        manager.AddLog(entry);
                    }
                }
                else
                {
                    resultText.text = "Reconstruction unstable.\nCausal contradiction detected.\n\nThe dialogue no longer has a clear trigger.";
                    retryButton.gameObject.SetActive(true);
                }
            }
        }

        private void OnTryDifferentOrder()
        {
            ResetPuzzle();
        }

        public void ResetPuzzle()
        {
            if (resultOverlay != null)
            {
                resultOverlay.alpha = 0;
                resultOverlay.blocksRaycasts = false;
                resultOverlay.interactable = false;
            }

            if (reconstructionSequenceBoxes != null)
            {
                foreach (var box in reconstructionSequenceBoxes)
                {
                    if (box != null) box.SetActive(false);
                }
            }
            anchorPanel.gameObject.SetActive(true);
            _anchorCanvasGroup.alpha = 1f;
            anchorPanel.GetComponent<Button>().interactable = true;

            StartCoroutine(FadeCanvasGroup(buttonGroup, 0f, 0.1f));
            
            candidateA.enabled = true;
            candidateB.enabled = true;
            lockInButton.interactable = true;
            tryOrderButton.interactable = true;
            
            candidateA.ReturnToOriginalPosition();
            candidateB.ReturnToOriginalPosition();
            
            if (slotLeft != null) slotLeft.GetComponent<MemoryReconstructionSlot>().ClearSlot();
            if (slotRight != null) slotRight.GetComponent<MemoryReconstructionSlot>().ClearSlot();
        }
    }
}
