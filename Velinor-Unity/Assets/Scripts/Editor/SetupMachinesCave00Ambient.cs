using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;

/// <summary>
/// Editor script to quickly set up ambient audio for MachinesCave_00 scene with wind sounds
/// </summary>
public class SetupMachinesCave00Ambient
{
    [MenuItem("Velinor/Setup/MachinesCave_00 Ambient Audio")]
    public static void SetupAmbient()
    {
        // Find or create AmbientManager GameObject
        GameObject ambientManagerObj = GameObject.Find("AmbientManager");
        if (ambientManagerObj == null)
        {
            ambientManagerObj = new GameObject("AmbientManager");
            Debug.Log("[Setup] Created AmbientManager GameObject");
        }

        // Add AmbientLayerController if not present
        AmbientLayerController controller = ambientManagerObj.GetComponent<AmbientLayerController>();
        if (controller == null)
        {
            controller = ambientManagerObj.AddComponent<AmbientLayerController>();
            Debug.Log("[Setup] Added AmbientLayerController component");
        }

        // Create/get AudioSources for different wind layers
        AudioSource baseWind = FindOrCreateAudioSource(ambientManagerObj, "Wind_Base");
        AudioSource windGust = FindOrCreateAudioSource(ambientManagerObj, "Wind_Gust");
        AudioSource windWhistle = FindOrCreateAudioSource(ambientManagerObj, "Wind_Whistle");
        AudioSource mountainHum = FindOrCreateAudioSource(ambientManagerObj, "MountainHum");

        // Configure base wind (continuous loop)
        if (baseWind != null)
        {
            baseWind.loop = true;
            baseWind.volume = 0.3f; // Subtle base layer
            baseWind.playOnAwake = true;
            Debug.Log("[Setup] Configured Wind_Base AudioSource");
        }

        // Configure wind gust (occasional gusts)
        if (windGust != null)
        {
            windGust.loop = true;
            windGust.volume = 0f; // Starts faded out
            windGust.playOnAwake = false;
            Debug.Log("[Setup] Configured Wind_Gust AudioSource");
        }

        // Configure wind whistle (high frequency wind)
        if (windWhistle != null)
        {
            windWhistle.loop = true;
            windWhistle.volume = 0f; // Starts faded out
            windWhistle.playOnAwake = false;
            Debug.Log("[Setup] Configured Wind_Whistle AudioSource");
        }

        // Configure mountain hum (deep desert ambience)
        if (mountainHum != null)
        {
            mountainHum.loop = true;
            mountainHum.volume = 0.2f; // Subtle deep tone
            mountainHum.playOnAwake = false;
            Debug.Log("[Setup] Configured MountainHum AudioSource");
        }

        // Mark scene as dirty
        EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
        Debug.Log("[Setup] ✅ MachinesCave_00 ambient audio system ready!");
        Debug.Log("[Setup] NEXT STEP: Assign wind audio clips to the AudioSource components in the Inspector");
    }

    private static AudioSource FindOrCreateAudioSource(GameObject parent, string name)
    {
        // Look for child with this name
        Transform child = parent.transform.Find(name);
        if (child != null)
            return child.GetComponent<AudioSource>();

        // Create new child
        GameObject audioObj = new GameObject(name);
        audioObj.transform.SetParent(parent.transform);
        AudioSource audioSource = audioObj.AddComponent<AudioSource>();

        // Basic audio source setup
        audioSource.spatialBlend = 0f; // 2D audio
        audioSource.dopplerLevel = 0f;
        audioSource.rolloffMode = AudioRolloffMode.Logarithmic;

        return audioSource;
    }
}
