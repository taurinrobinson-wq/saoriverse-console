using UnityEngine;

namespace Velinor.Core
{
    /// <summary>
    /// ScriptableObject that defines a single glyph's properties.
    /// Used by CodexController to populate glyph UI and manage glyph data.
    /// </summary>
    [CreateAssetMenu(fileName = "New Glyph", menuName = "Velinor/Glyph Data", order = 1)]
    public class GlyphData : ScriptableObject
    {
        [SerializeField]
        [Tooltip("Display name of the glyph in the codex")]
        public string glyphName;

        [SerializeField]
        [Tooltip("Icon sprite displayed in the codex UI")]
        public Sprite icon;

        [SerializeField]
        [TextArea(3, 5)]
        [Tooltip("Poetic or descriptive text about this glyph")]
        public string description;

        public void OnValidate()
        {
            if (string.IsNullOrEmpty(glyphName))
                glyphName = this.name;
        }
    }
}
