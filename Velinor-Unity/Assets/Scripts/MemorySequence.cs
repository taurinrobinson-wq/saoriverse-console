/*
 * ============================================================
 * PROPRIETARY & CONFIDENTIAL
 * 
 * © 2026 Tauri Robinson. All rights reserved.
 * This code is proprietary and may not be redistributed,
 * modified, or used without explicit written permission.
 * 
 * Unauthorized access, modification, or distribution is prohibited.
 * See LICENSE_COMMERCIAL.md and NDA_TEMPLATE.md for details.
 * ============================================================
 */

using UnityEngine;
using System.Collections;

/// <summary>
/// Triggers narrative camera sequences with fade effects.
/// Used for glyph visions, chamber moments, and emotional beats.
/// Freezes player movement during sequence.
/// </summary>
public class MemorySequence : MonoBehaviour
{
    [Header("Camera Settings")]
    [SerializeField] private Camera mainCamera;
    [SerializeField] private float zoomAmount = 2f;
    [SerializeField] private float zoomDuration = 1.5f;

    [Header("Fade Settings")]
    [SerializeField] private CanvasGroup fadeCanvas;
    [SerializeField] private float fadeDuration = 1f;

    [Header("Audio")]
    [SerializeField] private AudioSource memorySound;

    [Header("Sequence Control")]
    [SerializeField] private bool freezePlayer = true;

    private PlayerMovement playerMovement;
    private float originalCameraSize;

    private void Awake()
    {
        if (mainCamera == null)
            mainCamera = Camera.main;

        originalCameraSize = mainCamera.orthographicSize;
        playerMovement = FindAnyObjectByType<PlayerMovement>();
    }

    public void StartSequence()
    {
        StartCoroutine(SequenceRoutine());
    }

    private IEnumerator SequenceRoutine()
    {
        // Freeze player
        if (freezePlayer && playerMovement != null)
            playerMovement.enabled = false;

        // Play memory audio
        if (memorySound != null)
            memorySound.Play();

        // Camera zoom and fade
        yield return StartCoroutine(CameraZoom());
        yield return StartCoroutine(FadeToWhite());

        // Hold on white screen (narrative moment)
        yield return new WaitForSeconds(1f);

        // Return to normal
        yield return StartCoroutine(FadeFromWhite());
        yield return StartCoroutine(CameraReset());

        // Unfreeze player
        if (freezePlayer && playerMovement != null)
            playerMovement.enabled = true;

        Debug.Log("[MemorySequence] Sequence complete");
    }

    private IEnumerator CameraZoom()
    {
        float startSize = mainCamera.orthographicSize;
        float endSize = zoomAmount;
        float time = 0f;

        while (time < zoomDuration)
        {
            mainCamera.orthographicSize = Mathf.Lerp(startSize, endSize, time / zoomDuration);
            time += Time.deltaTime;
            yield return null;
        }

        mainCamera.orthographicSize = endSize;
    }

    private IEnumerator CameraReset()
    {
        float startSize = mainCamera.orthographicSize;
        float endSize = originalCameraSize;
        float time = 0f;

        while (time < zoomDuration)
        {
            mainCamera.orthographicSize = Mathf.Lerp(startSize, endSize, time / zoomDuration);
            time += Time.deltaTime;
            yield return null;
        }

        mainCamera.orthographicSize = endSize;
    }

    private IEnumerator FadeToWhite()
    {
        float time = 0f;

        while (time < fadeDuration)
        {
            fadeCanvas.alpha = Mathf.Lerp(0f, 1f, time / fadeDuration);
            time += Time.deltaTime;
            yield return null;
        }

        fadeCanvas.alpha = 1f;
    }

    private IEnumerator FadeFromWhite()
    {
        float time = 0f;

        while (time < fadeDuration)
        {
            fadeCanvas.alpha = Mathf.Lerp(1f, 0f, time / fadeDuration);
            time += Time.deltaTime;
            yield return null;
        }

        fadeCanvas.alpha = 0f;
    }
}
