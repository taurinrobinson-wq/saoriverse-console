using UnityEngine;

namespace Velinor.UI.MemoryPuzzle
{
    public class MemoryReconstructionSlot : MonoBehaviour
    {
        public MemoryReconstructionCandidate OccupyingCandidate { get; private set; }

        public bool IsOccupied => OccupyingCandidate != null;

        public void AssignCandidate(MemoryReconstructionCandidate candidate)
        {
            OccupyingCandidate = candidate;
            UpdateVisuals();
        }

        public void ClearSlot()
        {
            OccupyingCandidate = null;
            UpdateVisuals();
        }

        private void UpdateVisuals()
        {
            var img = GetComponent<UnityEngine.UI.Image>();
            if (img != null)
            {
                // Increase alpha when occupied to show it's 'populated'
                img.color = IsOccupied ? new Color(0, 1, 1, 0.15f) : new Color(0, 1, 1, 0.05f);
            }

            Transform border = transform.Find("Border");
            if (border != null)
            {
                var bImg = border.GetComponent<UnityEngine.UI.Image>();
                if (bImg != null)
                {
                    // Thicker/Brighter border when occupied? Or just keep it solid.
                    bImg.color = IsOccupied ? Color.white : new Color(0, 1, 1, 1f);
                }
            }
        }
    }
}
