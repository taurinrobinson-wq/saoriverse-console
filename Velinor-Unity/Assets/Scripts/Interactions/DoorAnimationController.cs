using UnityEngine;

/// <summary>
/// Animates the door cutout rising upward after glyphs are placed.
/// Reveals the darkened space (unsealed overlay) and allows player progression.
/// </summary>
public class DoorAnimationController : MonoBehaviour
{
    [SerializeField] private Transform doorCutout;
    [SerializeField] private float riseSpeed = 1.0f;
    [SerializeField] private float maxRiseDistance = 5.0f;
    [SerializeField] private ParticleSystem dustParticles;

    private bool opening = false;
    private float distanceTraveled = 0f;

    private void Update()
    {
        if (opening)
        {
            AnimateDoorOpening();
        }
    }

    public void OpenDoor()
    {
        opening = true;

        // Start dust particle effect if available
        if (dustParticles != null)
            dustParticles.Play();

        Debug.Log("Door opening animation started");
    }

    private void AnimateDoorOpening()
    {
        if (doorCutout == null)
        {
            Debug.LogWarning("DoorCutout not assigned!");
            opening = false;
            return;
        }

        float moveDistance = riseSpeed * Time.deltaTime;
        doorCutout.Translate(Vector3.up * moveDistance, Space.Self);
        distanceTraveled += moveDistance;

        if (distanceTraveled >= maxRiseDistance)
        {
            opening = false;
            distanceTraveled = 0f;
            Debug.Log("Door fully open");
        }
    }

    public void ResetDoor()
    {
        if (doorCutout == null)
            return;

        distanceTraveled = 0f;
        opening = false;
        // Reset position (implementation depends on your setup)
        // doorCutout.localPosition = Vector3.zero;
    }
}
