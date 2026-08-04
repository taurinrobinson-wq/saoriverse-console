using UnityEngine;

namespace Velinor.Utils
{
    public class Billboard : MonoBehaviour
    {
        private Transform _cam;

        void Start()
        {
            if (Camera.main != null)
                _cam = Camera.main.transform;
        }

        void LateUpdate()
        {
            if (_cam == null)
            {
                if (Camera.main != null)
                    _cam = Camera.main.transform;
                else
                    return;
            }

            // Face the camera, but only rotate around Y axis if desired
            // For a flat sprite, we usually want full billboard or just Y
            Vector3 lookPos = transform.position + _cam.forward;
            transform.LookAt(lookPos);
        }
    }
}
