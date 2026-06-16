using UnityEngine;
using Velinor.Core;

public class CodexManagerInitializer : MonoBehaviour
{
    private void Awake()
    {
        if (FindAnyObjectByType<CodexManager>() == null)
        {
            gameObject.AddComponent<CodexManager>();
        }
    }
}