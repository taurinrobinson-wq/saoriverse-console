using UnityEngine;

public class TorusRollingAnimation : MonoBehaviour
{
    [Header("Rolling Animation")]
    public float rollSpeed = 2f;           // Speed of rotation
    public float tubeHeight = 10f;         // Length of the tube
    public float scrollSpeed = 1f;         // Speed along the tube (positive = upward)

    private float currentOffset = 0f;

    void Update()
    {
        // Rotate the torus to simulate rolling
        transform.Rotate(rollSpeed * Time.deltaTime, 0, 0);

        // Move along the tube (in Y direction)
        currentOffset += scrollSpeed * Time.deltaTime;

        // Loop back to start if it goes too far
        if (currentOffset > tubeHeight)
        {
            currentOffset = -tubeHeight;
        }

        transform.position = new Vector3(transform.position.x, currentOffset, transform.position.z);
    }

    public void SetRollSpeed(float speed)
    {
        rollSpeed = speed;
    }

    public void SetScrollSpeed(float speed)
    {
        scrollSpeed = speed;
    }
}
