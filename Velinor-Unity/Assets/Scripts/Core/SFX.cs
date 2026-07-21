using UnityEngine;

public class LoopingSFX : MonoBehaviour
{
    public AudioClip soundEffect;   // Assign your audio clip in the Inspector
    public float volume = 1.0f;     // Adjust volume if needed

    private AudioSource audioSource;

    void Awake()
    {
        audioSource = gameObject.AddComponent<AudioSource>();
        audioSource.clip = soundEffect;
        audioSource.loop = true;        // Enable looping
        audioSource.playOnAwake = false;
        audioSource.volume = volume;
    }

    void Start()
    {
        audioSource.Play();             // Start the loop when the scene loads
    }
}
