using UnityEngine;
using UnityEditor;

/// <summary>
/// Deprecated: UI controllers now find their panels automatically
/// Kept for reference/documentation purposes
/// </summary>
public class MachinesCaveUIWireup : MonoBehaviour
{
    [MenuItem("Tools/Wireup MachinesCave Existing UI")]
    public static void WireupExistingUI()
    {
        Debug.Log("ℹ UI controllers now auto-wire themselves:");
        Debug.Log("  - DialogueUIController finds DialoguePanel in Awake()");
        Debug.Log("  - DiaryController finds DiarySystem in prefab");
        Debug.Log("  - CodexController finds CodexPanel in Awake()");
        Debug.Log("✓ No manual wiring needed!");
    }
}