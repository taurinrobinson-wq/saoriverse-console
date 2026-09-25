Shader "Custom/SpriteRimGlow"
{
    Properties
    {
        [MainTexture] _MainTex ("Sprite Texture", 2D) = "white" {}
        _EmissionColor ("Glow Color", Color) = (0,1,1,1)
        _GlowIntensity ("Glow Intensity", Range(0, 10)) = 2.0
        _OutlineWidth ("Outline Width", Range(0, 0.05)) = 0.01
    }

    SubShader
    {
        Tags
        {
            "Queue"="Transparent"
            "IgnoreProjector"="True"
            "RenderType"="Transparent"
            "PreviewType"="Plane"
            "CanUseSpriteAtlas"="True"
        }

        Cull Off
        Lighting Off
        ZWrite Off
        Blend One OneMinusSrcAlpha

        Pass
        {
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv : TEXCOORD0;
                float4 color : COLOR;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float4 color : COLOR;
            };

            sampler2D _MainTex;
            float4 _MainTex_ST;
            float4 _EmissionColor;
            float _GlowIntensity;
            float _OutlineWidth;

            Varyings vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.uv = TRANSFORM_TEX(input.uv, _MainTex);
                output.color = input.color;
                return output;
            }

            half4 frag(Varyings input) : SV_Target
            {
                // Sample the sprite to get the shape
                float alpha = tex2D(_MainTex, input.uv).a;
                
                // Sample multiple points to create a thicker outline
                float outline = 0;
                float dist = _OutlineWidth;
                
                outline += tex2D(_MainTex, input.uv + float2(dist, 0)).a;
                outline += tex2D(_MainTex, input.uv + float2(-dist, 0)).a;
                outline += tex2D(_MainTex, input.uv + float2(0, dist)).a;
                outline += tex2D(_MainTex, input.uv + float2(0, -dist)).a;
                outline += tex2D(_MainTex, input.uv + float2(dist * 0.7, dist * 0.7)).a;
                outline += tex2D(_MainTex, input.uv + float2(-dist * 0.7, dist * 0.7)).a;
                outline += tex2D(_MainTex, input.uv + float2(dist * 0.7, -dist * 0.7)).a;
                outline += tex2D(_MainTex, input.uv + float2(-dist * 0.7, -dist * 0.7)).a;
                
                outline = saturate(outline / 8.0);
                
                // Only show glow outside the original shape (or at least prioritize it)
                float glowMask = saturate(outline - alpha);
                
                half4 color = _EmissionColor * _GlowIntensity * glowMask;
                color.rgb *= color.a; // Premultiplied alpha for URP
                
                return color;
            }
            ENDHLSL
        }
    }
}
