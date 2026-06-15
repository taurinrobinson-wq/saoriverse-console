using UnityEngine;
using UnityEngine.SceneManagement;

public class MainMenu : MonoBehaviour
{
    public void PlayGame()
    {
        // Loads the next scene in your build sequence
        SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex + 1);
        
        // Alternatively, load by exact scene name string:
        // SceneManager.LoadScene("GameplayScene"); 
    }
}
