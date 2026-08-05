using Unity.Entities;
using Unity.Entities.UI;
using Unity.Rendering;
using UnityEditor;
using UnityEditor.UIElements;
using UnityEngine;
using UnityEngine.UIElements;

namespace TimeGhost
{
    class RenderMeshArrayInspector : PropertyInspector<RenderMeshArray>
    {
        public override VisualElement Build()
        {
            var baseElement = base.Build();

            // Create a main container for all your fields
            var renderMeshArray = Target;

            var foldout = new Foldout();
            foldout.text = "Material & Mesh References";
            baseElement.Add(foldout);
            
            {
                var materials = renderMeshArray.MaterialReferences;
                for(int i = 0; i < materials.Length; ++i)
                {
                    var objectField = new ObjectField();
                    objectField.objectType = typeof(Material);
                    objectField.value = materials[i];
                    foldout.Add(objectField);
                }
            }
            
            {
                var meshes = renderMeshArray.MeshReferences;
                for(int i = 0; i < meshes.Length; ++i)
                {
                    var objectField = new ObjectField();
                    objectField.objectType = typeof(Mesh);
                    objectField.value = meshes[i];
                    foldout.Add(objectField);
                }
            }
            

            return baseElement;
        }
    }
}