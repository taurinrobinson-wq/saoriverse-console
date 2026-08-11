using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections;

public class DiaryController : MonoBehaviour
{
    [Header("Page Layers")]
    public Image leftPage;
    public Image rightPage;

    [Header("Text Layers")]
    public TextMeshProUGUI textLeft;
    public TextMeshProUGUI textRight;

    [Header("Animation Settings")]
    public float turnDuration = 0.35f;
    public float swingDuration = 0.5f;

    private bool diaryOpen = false;
    private bool isAnimating = false;
    private CanvasGroup cg;
    private RectTransform rectTransform;
    private Vector2 openPosition;
    private Vector2 closedPosition;

    void Start()
    {
        cg = GetComponent<CanvasGroup>();
        rectTransform = GetComponent<RectTransform>();
        
        // Store open position (center of screen)
        openPosition = Vector2.zero;
        
        // Store closed position (off-screen at bottom)
        closedPosition = new Vector2(0, -rectTransform.rect.height - 100f);
        
        // Start off-screen
        rectTransform.anchoredPosition = closedPosition;
        cg.interactable = false;
        cg.blocksRaycasts = false;

        leftPage.rectTransform.localRotation = Quaternion.identity;
        rightPage.rectTransform.localRotation = Quaternion.identity;
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.N) && !isAnimating)
        {
            if (!diaryOpen) StartCoroutine(OpenDiary());
            else StartCoroutine(CloseDiary());
        }

        if (diaryOpen && Input.GetKeyDown(KeyCode.RightArrow))
        {
            StartCoroutine(TurnPage());
        }
    }

    public IEnumerator OpenDiary()
    {
        isAnimating = true;
        diaryOpen = true;
        cg.interactable = true;
        cg.blocksRaycasts = true;

        float t = 0f;
        while (t < swingDuration)
        {
            t += Time.deltaTime;
            float normalized = t / swingDuration;
            
            // Swing animation: ease out curve for natural swing motion
            float eased = 1f - Mathf.Pow(1f - normalized, 3f);
            
            rectTransform.anchoredPosition = Vector2.Lerp(closedPosition, openPosition, eased);
            yield return null;
        }

        rectTransform.anchoredPosition = openPosition;
        isAnimating = false;
    }

    public IEnumerator CloseDiary()
    {
        isAnimating = true;
        diaryOpen = false;
        cg.interactable = false;
        cg.blocksRaycasts = false;

        float t = 0f;
        while (t < swingDuration)
        {
            t += Time.deltaTime;
            float normalized = t / swingDuration;
            
            // Swing down animation: ease in curve
            float eased = Mathf.Pow(normalized, 3f);
            
            rectTransform.anchoredPosition = Vector2.Lerp(openPosition, closedPosition, eased);
            yield return null;
        }

        rectTransform.anchoredPosition = closedPosition;
        isAnimating = false;
    }

    IEnumerator TurnPage()
    {
        float t = 0f;

        while (t < turnDuration)
        {
            t += Time.deltaTime;
            float normalized = t / turnDuration;

            float angle = Mathf.Lerp(0f, -90f, normalized);
            leftPage.rectTransform.localRotation = Quaternion.Euler(0, angle, 0);

            yield return null;
        }

        textLeft.text = textRight.text;
        textRight.text = "New diary entry...";

        leftPage.rectTransform.localRotation = Quaternion.identity;
    }
}
