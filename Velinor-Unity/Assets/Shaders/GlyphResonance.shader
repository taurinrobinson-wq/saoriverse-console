Shader "Velinor/GlyphResonance"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" {}
        _GlowColor ("Glow Color", Color) = (0, 1, 1, 1)
        _GlowStrength ("Glow Strength", Range(0, 2)) = 0.5
        _PulseSpeed ("Pulse Speed", Range(0, 10)) = 3
    }

    SubShader
    {
        Tags { "RenderType"="Transparent" "Queue"="Transparent" }
        Blend SrcAlpha OneMinusSrcAlpha
        ZWrite Off

        Pass
        {
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            sampler2D _MainTex;
            float4 _MainTex_ST;
            float4 _GlowColor;
            float _GlowStrength;
            float _PulseSpeed;

            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
                float4 color : COLOR;
            };

            struct v2f
            {
                float2 uv : TEXCOORD0;
                float4 vertex : SV_POSITION;
                float4 color : COLOR;
            };

            v2f vert (appdata v)
            {
                v2f o;
                o.vertex = TransformObjectToHClip(v.vertex.xyz);
                o.uv = TRANSFORM_TEX(v.uv, _MainTex);
                o.color = v.color;
                return o;
            }

            float4 frag (v2f i) : SV_Target
            {
                float4 col = tex2D(_MainTex, i.uv);
                col *= i.color;

                // Pulsing glow
                float pulse = (sin(_Time.y * _PulseSpeed) + 1.0) * 0.5;
                float4 glow = _GlowColor * pulse * _GlowStrength;

                return col + glow;
            }
            ENDHLSL
        }
    }
}
