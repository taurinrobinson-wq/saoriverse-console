using UnityEngine;

namespace Velinor.Utils
{
    [ExecuteInEditMode]
    public class PlayerBodyCustomizer : MonoBehaviour
    {
        [Header("Colors")]
        public Color skinColor = new Color(0.85f, 0.67f, 0.55f);
        public Color torsoColor = new Color(0.15f, 0.15f, 0.2f);
        
        [Header("Tuning")]
        [Range(0, 2)] public float headHeightThreshold = 1.55f;
        [Range(0, 1)] public float smoothness = 0.3f;

        private SkinnedMeshRenderer smr;
        private MaterialPropertyBlock propBlock;

        private void OnEnable()
        {
            smr = GetComponentInChildren<SkinnedMeshRenderer>();
            propBlock = new MaterialPropertyBlock();
            Apply();
        }

        private void OnValidate()
        {
            Apply();
        }

        public void Apply()
        {
            if (smr == null) smr = GetComponentInChildren<SkinnedMeshRenderer>();
            if (smr == null) return;

            if (propBlock == null) propBlock = new MaterialPropertyBlock();

            // We use the custom shader for Slot 0 (Body)
            // And standard skin for Slots 1 & 2
            
            // Note: To make this work seamlessly in editor without creating many assets,
            // we'll ensure the materials assigned to the slots have the right shader.
            
            if (smr.sharedMaterials.Length > 0)
            {
                smr.GetPropertyBlock(propBlock, 0);
                propBlock.SetColor("_SkinColor", skinColor);
                propBlock.SetColor("_ClothColor", torsoColor);
                propBlock.SetFloat("_HeadThreshold", headHeightThreshold);
                propBlock.SetFloat("_Smoothness", smoothness);
                smr.SetPropertyBlock(propBlock, 0);
            }

            // Slots 1 and 2 (Arms/Legs) - if they use the same shader we can just set color
            if (smr.sharedMaterials.Length > 1)
            {
                smr.GetPropertyBlock(propBlock, 1);
                propBlock.SetColor("_SkinColor", skinColor);
                propBlock.SetColor("_ClothColor", skinColor); // Make it all skin
                propBlock.SetFloat("_HeadThreshold", -1f); // Force all skin
                smr.SetPropertyBlock(propBlock, 1);
            }

            if (smr.sharedMaterials.Length > 2)
            {
                smr.GetPropertyBlock(propBlock, 2);
                propBlock.SetColor("_SkinColor", skinColor);
                propBlock.SetColor("_ClothColor", skinColor);
                propBlock.SetFloat("_HeadThreshold", -1f);
                smr.SetPropertyBlock(propBlock, 2);
            }
        }
}
}
