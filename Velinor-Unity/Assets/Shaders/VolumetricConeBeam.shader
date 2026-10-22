Shader "Custom/VolumetricConeBeam"
{
    Properties
    {
        [HDR] _BaseColor ("Beam Color", Color) = (1, 1, 1, 0.22)
        _NearBrightness ("Near Source Brightness", Range(1, 5)) = 2.5
        _DistanceFade ("Distance Fade Power", Range(0.5, 4)) = 1.4
        _EdgeSoftness ("Edge Softness", Range(0.1, 4)) = 1.0
        _CoreGlow ("Core Glow", Range(0, 1)) = 0.4
    }

    SubShader
    {
        Tags
        {
            "Queue" = "Transparent+10"
            "RenderType" = "Transparent"
            "RenderPipeline" = "UniversalPipeline"
            "IgnoreProjector" = "True"
        }

        Cull Off
        ZWrite Off
        Blend SrcAlpha One // Additive light blending

        Pass
        {
            Name "VolumetricBeamPass"
            Tags { "LightMode" = "SRPDefaultUnlit" }

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_fog

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes
            {
                float4 positionOS   : POSITION;
                float3 normalOS     : NORMAL;
                float2 uv           : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionCS   : SV_POSITION;
                float2 uv           : TEXCOORD0;
                float3 normalWS     : TEXCOORD1;
                float3 viewDirWS    : TEXCOORD3;
                float  fogCoord     : TEXCOORD4;
            };

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseColor;
                float  _NearBrightness;
                float  _DistanceFade;
                float  _EdgeSoftness;
                float  _CoreGlow;
            CBUFFER_END

            Varyings vert(Attributes input)
            {
                Varyings output = (Varyings)0;

                VertexPositionInputs vertexInput = GetVertexPositionInputs(input.positionOS.xyz);
                VertexNormalInputs normalInput = GetVertexNormalInputs(input.normalOS);

                output.positionCS = vertexInput.positionCS;
                output.uv = input.uv;
                output.normalWS = normalInput.normalWS;
                output.viewDirWS = GetWorldSpaceNormalizeViewDir(vertexInput.positionWS);
                output.fogCoord = ComputeFogFactor(vertexInput.positionCS.z);

                return output;
            }

            half4 frag(Varyings input) : SV_Target
            {
                // uv.y = 0 at base (emitter), 1 at top (fades to 0)
                float height = saturate(input.uv.y);
                float distFade = pow(saturate(1.0 - height), _DistanceFade);
                float nearBoost = lerp(1.0, _NearBrightness, pow(saturate(1.0 - height), 2.5));

                // Soft view-aligned grazing rim so the cone shell looks like filled volumetric smoke
                float3 normalWS = normalize(input.normalWS);
                float3 viewDirWS = normalize(input.viewDirWS);
                float rim = abs(dot(normalWS, viewDirWS));
                float edgeFactor = lerp(_CoreGlow, 1.0, pow(saturate(rim), _EdgeSoftness));

                float alpha = _BaseColor.a * distFade * edgeFactor;
                half3 color = _BaseColor.rgb * nearBoost;

                #if defined(FOG_LINEAR) || defined(FOG_EXP) || defined(FOG_EXP2)
                color = MixFogColor(color, half3(0, 0, 0), input.fogCoord);
                #endif

                return half4(color, alpha);
            }
            ENDHLSL
        }
    }
    FallBack Off
}

