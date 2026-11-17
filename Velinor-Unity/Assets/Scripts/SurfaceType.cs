using UnityEngine;

/// <summary>
/// Identifies the fictional ground material represented by a 2D surface zone.
/// Attach this component to an invisible Collider2D covering a walkable area.
/// </summary>
[RequireComponent(typeof(Collider2D))]
public class SurfaceType : MonoBehaviour
{
    public enum Surface
    {
        Dirt,
        Grass,
        Mud,
        ShallowWater,
        Stone,
        Metal,
        Wood,
        Snow,
        Gravel
    }

    [Header("Surface")]
    [Tooltip("The footstep material represented by this collider.")]
    public Surface surfaceType = Surface.Dirt;

    [Tooltip("If multiple surface zones overlap, the zone with the highest priority wins.")]
    public int priority = 0;

    private void Reset()
    {
        Collider2D surfaceCollider = GetComponent<Collider2D>();

        if (surfaceCollider != null)
        {
            surfaceCollider.isTrigger = true;
        }
    }
}

