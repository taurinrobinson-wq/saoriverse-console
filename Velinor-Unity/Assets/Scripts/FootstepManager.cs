using UnityEngine;
using System.Collections.Generic;

/// <summary>
/// Plays surface-specific footsteps when called by Animation Events.
/// Surface material is detected from invisible Collider2D zones placed
/// over the player's fictional walking area.
/// </summary>
public class FootstepManager : MonoBehaviour
{
    [System.Serializable]
    public class SurfaceAudioSet
    {
        public SurfaceType.Surface surface;

        [Tooltip("Several variations of the same type of footstep.")]
        public AudioClip[] footstepClips;

        [Range(0f, 1.5f)]
        public float volumeMultiplier = 1f;
    }

    [Header("Surface Audio")]
    [SerializeField]
    private SurfaceAudioSet[] surfaceAudioSets;

    [Header("Audio")]
    [SerializeField]
    private AudioSource footstepAudioSource;

    [Range(0f, 1f)]
    [SerializeField]
    private float masterFootstepVolume = 0.7f;

    [Tooltip("Small random volume variation prevents repeated steps from sounding identical.")]
    [Range(0f, 0.25f)]
    [SerializeField]
    private float volumeVariation = 0.08f;

    [Header("Surface Detection")]
    [Tooltip("Place this transform near the visual contact point between the feet and ground.")]
    [SerializeField]
    private Transform footProbe;

    [Tooltip("Radius used to find invisible surface-zone colliders.")]
    [SerializeField]
    private float surfaceCheckRadius = 0.15f;

    [Tooltip("Only colliders on these layers will be treated as footstep surfaces.")]
    [SerializeField]
    private LayerMask surfaceLayer;

    [Tooltip("Used when the foot probe is not touching a marked surface zone.")]
    [SerializeField]
    private SurfaceType.Surface defaultSurface = SurfaceType.Surface.Dirt;

    [Header("Movement Validation")]
    [Tooltip("Prevents transition frames from playing footsteps while the player is stationary.")]
    [SerializeField]
    private bool requireMovement = true;

    [Tooltip("Name of the Animator float parameter reporting player movement speed.")]
    [SerializeField]
    private string speedParameter = "Speed";

    [Tooltip("Minimum Animator speed required before a footstep can play.")]
    [SerializeField]
    private float minimumMovementSpeed = 0.05f;

    [Header("Debug")]
    [SerializeField]
    private bool showDebugMessages = false;

    private Animator animator;

    private Dictionary<SurfaceType.Surface, SurfaceAudioSet> surfaceAudioMap;
    private Dictionary<SurfaceType.Surface, int> lastClipBySurface;

    private bool surfaceOverrideActive;
    private SurfaceType.Surface overriddenSurface;

    private void Awake()
    {
        animator = GetComponent<Animator>();

        if (footstepAudioSource == null)
        {
            footstepAudioSource = GetComponent<AudioSource>();
        }

        if (footstepAudioSource == null)
        {
            footstepAudioSource = gameObject.AddComponent<AudioSource>();
            footstepAudioSource.spatialBlend = 0f;
            footstepAudioSource.playOnAwake = false;
            footstepAudioSource.priority = 128;
        }

        if (footProbe == null)
        {
            footProbe = transform;
            Debug.LogWarning(
                "[FootstepManager] No foot probe assigned. " +
                "Using the player's transform position."
            );
        }

        BuildSurfaceAudioMap();
    }

    private void BuildSurfaceAudioMap()
    {
        surfaceAudioMap =
            new Dictionary<SurfaceType.Surface, SurfaceAudioSet>();

        lastClipBySurface =
            new Dictionary<SurfaceType.Surface, int>();

        if (surfaceAudioSets == null)
        {
            return;
        }

        foreach (SurfaceAudioSet audioSet in surfaceAudioSets)
        {
            if (audioSet == null)
            {
                continue;
            }

            if (audioSet.footstepClips == null ||
                audioSet.footstepClips.Length == 0)
            {
                continue;
            }

            surfaceAudioMap[audioSet.surface] = audioSet;
            lastClipBySurface[audioSet.surface] = -1;
        }
    }

    /// <summary>
    /// Animation Event placed at the right-foot contact frame.
    /// </summary>
    public void PlayRightFootstep()
    {
        PlayFootstep("Right");
    }

    /// <summary>
    /// Animation Event placed at the left-foot contact frame.
    /// </summary>
    public void PlayLeftFootstep()
    {
        PlayFootstep("Left");
    }

    /// <summary>
    /// Generic method retained in case an animation only needs one event name.
    /// </summary>
    public void PlayFootstepEvent()
    {
        PlayFootstep("Foot");
    }

    private void PlayFootstep(string footName)
    {
        if (footstepAudioSource == null)
        {
            return;
        }

        if (requireMovement &&
            animator != null &&
            !string.IsNullOrEmpty(speedParameter))
        {
            float speed = animator.GetFloat(speedParameter);

            if (speed <= minimumMovementSpeed)
            {
                return;
            }
        }

        SurfaceType.Surface currentSurface = DetectCurrentSurface();

        if (!surfaceAudioMap.TryGetValue(
                currentSurface,
                out SurfaceAudioSet audioSet))
        {
            if (showDebugMessages)
            {
                Debug.LogWarning(
                    "[FootstepManager] No clips configured for surface: " +
                    currentSurface
                );
            }

            return;
        }

        if (audioSet.footstepClips == null ||
            audioSet.footstepClips.Length == 0)
        {
            return;
        }

        int clipIndex = ChooseClipIndex(
            currentSurface,
            audioSet.footstepClips.Length
        );

        AudioClip selectedClip = audioSet.footstepClips[clipIndex];

        if (selectedClip == null)
        {
            return;
        }

        float randomVolume = Random.Range(
            1f - volumeVariation,
            1f + volumeVariation
        );

        float finalVolume =
            masterFootstepVolume *
            audioSet.volumeMultiplier *
            randomVolume;

        footstepAudioSource.PlayOneShot(selectedClip, finalVolume);

        if (showDebugMessages)
        {
            Debug.Log(
                "[FootstepManager] " +
                footName +
                " foot on " +
                currentSurface +
                " using " +
                selectedClip.name
            );
        }
    }

    private int ChooseClipIndex(
        SurfaceType.Surface surface,
        int clipCount)
    {
        if (clipCount <= 1)
        {
            lastClipBySurface[surface] = 0;
            return 0;
        }

        int lastIndex = -1;

        if (lastClipBySurface.TryGetValue(surface, out int storedIndex))
        {
            lastIndex = storedIndex;
        }

        int newIndex = Random.Range(0, clipCount);

        while (newIndex == lastIndex)
        {
            newIndex = Random.Range(0, clipCount);
        }

        lastClipBySurface[surface] = newIndex;
        return newIndex;
    }

    private SurfaceType.Surface DetectCurrentSurface()
    {
        if (surfaceOverrideActive)
        {
            return overriddenSurface;
        }

        Vector2 probePosition =
            footProbe != null
                ? footProbe.position
                : transform.position;

        Collider2D[] detectedColliders =
            Physics2D.OverlapCircleAll(
                probePosition,
                surfaceCheckRadius,
                surfaceLayer
            );

        SurfaceType bestSurface = null;
        int highestPriority = int.MinValue;

        foreach (Collider2D detectedCollider in detectedColliders)
        {
            if (detectedCollider == null)
            {
                continue;
            }

            SurfaceType surface =
                detectedCollider.GetComponent<SurfaceType>();

            if (surface == null)
            {
                surface =
                    detectedCollider.GetComponentInParent<SurfaceType>();
            }

            if (surface == null)
            {
                continue;
            }

            if (bestSurface == null ||
                surface.priority > highestPriority)
            {
                bestSurface = surface;
                highestPriority = surface.priority;
            }
        }

        if (bestSurface != null)
        {
            return bestSurface.surfaceType;
        }

        return defaultSurface;
    }

    /// <summary>
    /// Forces a particular surface until ClearSurfaceOverride is called.
    /// Useful for scripted sequences or unusual areas.
    /// </summary>
    public void SetSurfaceOverride(SurfaceType.Surface surface)
    {
        overriddenSurface = surface;
        surfaceOverrideActive = true;
    }

    /// <summary>
    /// Returns control to automatic surface-zone detection.
    /// </summary>
    public void ClearSurfaceOverride()
    {
        surfaceOverrideActive = false;
    }

    public SurfaceType.Surface GetCurrentSurface()
    {
        return DetectCurrentSurface();
    }

    private void OnDrawGizmosSelected()
    {
        Vector3 probePosition =
            footProbe != null
                ? footProbe.position
                : transform.position;

        Gizmos.color = Color.cyan;
        Gizmos.DrawWireSphere(probePosition, surfaceCheckRadius);
    }
}
