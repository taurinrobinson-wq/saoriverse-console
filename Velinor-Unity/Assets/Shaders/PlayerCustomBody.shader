// I will use a simple code-based shader since I can't generate a binary shadergraph file easily, 
// but I can create a standard Shader file that works with URP.
Shader "Custom/PlayerBodyHeightMask"
{
    Properties
    {
        _SkinColor("Skin Color", Color) = (0.8, 0.6, 0.5, 1)
        _ClothColor("Cloth Color", Color) = (0.2, 0.2, 0.2, 1)
        _HeadThreshold("Head Height Threshold", Float) = 1.5
        _Smoothness("Smoothness", Range(0,1)) = 0.5
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" }
        LOD 100

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode"="UniversalForward" }

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS : TEXCOORD1;
            };

            CBUFFER_START(UnityPerMaterial)
                float4 _SkinColor;
                float4 _ClothColor;
                float _HeadThreshold;
                float _Smoothness;
            CBUFFER_END

            Varyings vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.positionWS = TransformObjectToWorld(input.positionOS.xyz);
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                return output;
            }

            float4 frag(Varyings input) : SV_Target
            {
                // Determine if we are in the head or torso based on LOCAL Y position
                // Note: Armature_Mesh local space Y is roughly 0 (feet) to 1.8 (head)
                // We need the local position. Let's pass it from vert.
                
                // Re-calculating local Y by transforming back or passing it.
                float3 posOS = TransformWorldToObject(input.positionWS);
                float mask = saturate((posOS.y - _HeadThreshold) * 100.0); // Sharp transition
                
                float3 albedo = lerp(_ClothColor.rgb, _SkinColor.rgb, mask);
                
                // Simple lighting
                float3 lightDir = _MainLightPosition.xyz;
                float diffuse = saturate(dot(normalize(input.normalWS), lightDir));
                float3 finalColor = albedo * (diffuse * _MainLightColor.rgb + 0.2); // + ambient
                
                return float4(finalColor, 1.0);
            }
            ENDHLSL
        }
    }
}
