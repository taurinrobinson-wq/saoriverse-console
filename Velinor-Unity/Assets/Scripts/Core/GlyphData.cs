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
        [SerializeField] public string glyphName;
        [SerializeField] public Sprite icon;
        [SerializeField] public string description;

        public void OnValidate()
        {
            if (string.IsNullOrEmpty(glyphName))
                glyphName = this.name;
        }
    }
}
