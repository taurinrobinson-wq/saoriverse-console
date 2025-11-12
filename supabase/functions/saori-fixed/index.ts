import { createClient } from "npm:@supabase/supabase-js@2.45.4";
import OpenAI from "npm:openai@4.56.0";

const ALLOWED_ORIGINS = [
  "https://taurinrobinson-wq.github.io",
  "https://console.saonyx.com"
];

function getCorsHeaders(req) {
  const origin = req.headers.get("Origin");
  const isStreamlitApp = origin && origin.includes(".streamlit.app");
  const isLocalhost = origin && (origin.includes("localhost") || origin.includes("127.0.0.1"));
  let allowOrigin = ALLOWED_ORIGINS.includes(origin) || isStreamlitApp || isLocalhost ? origin : ALLOWED_ORIGINS[0];
  return {
    "Access-Control-Allow-Origin": allowOrigin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Content-Type": "application/json"
  };
}

// User Authentication Functions
async function validateUserSession(authHeader: string, adminClient: any): Promise<{ valid: boolean, userId?: string }> {
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return { valid: false };
  }

  try {
    const token = authHeader.replace("Bearer ", "");

    // Parse custom token format: base64payload.signature
    const parts = token.split('.');
    if (parts.length !== 2) {
      return { valid: false };
    }

    const [payloadB64, signature] = parts;
    const payload = JSON.parse(atob(payloadB64));

    // Validate token structure
    if (!payload.user_id || !payload.issued_at || !payload.expires_at) {
      return { valid: false };
    }

    // Check expiration
    if (Date.now() > payload.expires_at) {
      return { valid: false };
    }

    // Validate signature (simple check)
    const expectedSignature = btoa(payload.user_id + '_' + payload.issued_at);
    if (signature !== expectedSignature) {
      return { valid: false };
    }

    // Verify user exists in database
    const { data: user, error } = await adminClient
      .from('users')
      .select('id, username')
      .eq('id', payload.user_id)
      .single();

    if (error || !user) {
      return { valid: false };
    }

    return { valid: true, userId: user.id };
  } catch (err) {
    console.error("Session validation error:", err);
    return { valid: false };
  }
}

(function assertEnv() {
  const missing = [];
  if (!SUPABASE_URL) missing.push("SUPABASE_URL");
  if (!SUPABASE_ANON_KEY) missing.push("PROJECT_ANON_KEY|SUPABASE_ANON_KEY");
  if (!SUPABASE_SERVICE_ROLE_KEY) missing.push("PROJECT_SERVICE_ROLE_KEY|SUPABASE_SERVICE_ROLE_KEY");
  if (!OPENAI_API_KEY) missing.push("OPENAI_API_KEY");
  if (missing.length) console.error(`saori-fixed missing env: ${missing.join(", ")}`);
})();

Deno.serve(async (req) => {
  const corsHeaders = getCorsHeaders(req);
  try {
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders });
    if (req.method !== "POST") return new Response(JSON.stringify({ error: "Method Not Allowed" }), { status: 405, headers: corsHeaders });
    if (!SUPABASE_URL || !SUPABASE_ANON_KEY || !SUPABASE_SERVICE_ROLE_KEY || !OPENAI_API_KEY) {
      return new Response(JSON.stringify({ error: "Server misconfiguration: required secrets missing." }), { status: 500, headers: corsHeaders });
    }

    const authHeader = req.headers.get("Authorization") ?? "";
    const token = authHeader.startsWith("Bearer ") ? authHeader.slice(7) : "";

    const userClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

    const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, { auth: { persistSession: false } });

    let userId = null;
    if (token) {
      const sessionValidation = await validateUserSession(`Bearer ${token}`, admin);
      if (sessionValidation.valid) {
        userId = sessionValidation.userId;
      }
    }

    let body;
    try {
      body = await req.json();
    } catch {
      return new Response(JSON.stringify({ error: "Invalid JSON" }), { status: 400, headers: corsHeaders });
    }

    // Timestamp for simple processing_time logs
    const startTime = Date.now();

    const message = body?.message?.toString?.().trim();
    const mode = body?.mode?.toString?.() || "quick";
    const requestUserId = body?.user_id?.toString?.();
    if (requestUserId) userId = requestUserId;
    if (!message) return new Response(JSON.stringify({ error: "Missing 'message'" }), { status: 400, headers: corsHeaders });

    // 1. Mode-based tone map
    const toneMap = {
      hybrid: "editorial and private",
      local: "plain and conversational",
      ai_preferred: "emotionally attuned and responsive",
      quick: "regular and grounded"
    };

    // 2. Extract override tone from mode
    const overrideTone = toneMap[mode] ?? null;

    const openai = new OpenAI({ apiKey: OPENAI_API_KEY });

    const input = message.toLowerCase();
    const wantsPlain = /plain|simple|normal|talk normal|conversational|less mythic/.test(input);
    const wantsFunny = /make me laugh|be funny|roast me|joke|silly|playful/.test(input);

    // 3. Emotional tag matching
    let matchedTag = null;
    try {
      const tagQuery = wantsPlain
        ? admin.from("emotional_tags").select("*").eq("tag_name", "plain").single()
        : wantsFunny
          ? admin.from("emotional_tags").select("*").eq("tag_name", "playful").single()
          : userClient.from("emotional_tags").select("*").ilike("tag_name", `%${input}%`);
      const { data } = await tagQuery;
      matchedTag = data ?? null;
    } catch (e) {
      console.error("Tag lookup failed:", e);
    }

    // 4. Editorial switchboard with mode override taking priority
    const tone = overrideTone ?? matchedTag?.tone_profile ?? "regular and grounded";
    const cadence = matchedTag?.cadence ?? "poetic and flowing";
    const depthTone = matchedTag?.depth_level ?? "emotional excavation";
    const style = matchedTag?.style_variant ?? "oracle";
    const humor = matchedTag?.humor_style ?? "none";
    const voltage = matchedTag?.glyph ?? "γ × γ";
    const domain = matchedTag?.domain ?? "Unspecified";
    const coreEmotion = matchedTag?.core_emotion ?? "Ambiguity";
    const responseType = matchedTag?.response_type ?? "Reflect";
    const hook = matchedTag?.narrative_hook ?? "Saori listens in silence.";

    // 5. System prompt construction - direct and specific
    const systemPrompt = `You are Saori, a compassionate friend who helps people with their emotional challenges. You listen carefully and respond with genuine empathy and understanding.

IMPORTANT: Respond naturally and conversationally, like a caring friend would. Acknowledge their feelings, validate their experiences, and offer supportive insights when appropriate. Never give generic technical responses.

For example, if someone shares about family difficulties, respond with something like: "That sounds really tough. Divorce and custody issues can be so complicated, especially when kids are involved. It makes sense that you're worried about having the right space for him."

Keep your response focused on emotional support and understanding. Be warm, genuine, and human.`.trim();

    // 6.a Optional limbic cues supplied by a trusted client. If present, summarize them for the generator.
    let fullSystemPrompt = systemPrompt;
    try {
      const limbic = body?.limbic;
      if (limbic && typeof limbic === 'object') {
        const limbicEmotion = String(limbic.emotion ?? 'unknown');
        const ritualSeq = Array.isArray(limbic.ritual_sequence) ? limbic.ritual_sequence.join(', ') : '';
        let signalsSummary = '';
        try {
          const keys = Object.keys(limbic.system_signals || {}).slice(0, 5);
          signalsSummary = keys.map(k => `${k}:${(limbic.system_signals[k]?.signal ?? '').slice(0, 60)}`).join('; ');
        } catch (e) {
          signalsSummary = '';
        }

        const limbicNote = `Limbic cues: emotion=${limbicEmotion}; rituals=${ritualSeq}; signals=${signalsSummary}. Use these cues to adapt tone and include a brief empathic opener that references the mapped emotion when appropriate.`;
        fullSystemPrompt = systemPrompt + "\n\n" + limbicNote;
      }
    } catch (e) {
      // Non-fatal - continue with base prompt
    }

    // 6. Completion call
    let reply = "Saori echoes your words, though the oracle sleeps.";
    try {
      console.log("Making OpenAI call with system prompt:", fullSystemPrompt.substring(0, 200) + "...");
      const completion = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: fullSystemPrompt },
          { role: "user", content: message }
        ],
        temperature: 0.8
      });
      reply = completion.choices?.[0]?.message?.content ?? reply;
      console.log("OpenAI response received:", reply.substring(0, 100) + "...");
    } catch (err) {
      console.error("OpenAI error:", err);
    }

    let parsedGlyphs = [];
    try {
      // Stronger, stricter extraction instructions to force a valid JSON-only response.
      const extract = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          {
            role: "system",
            content: "You are a JSON-only extractor. Given a user's message, you MUST return ONLY a valid JSON object (no surrounding explanation, no markdown) with a single key 'glyphs'. The value of 'glyphs' MUST be an array (possibly empty). Each array element must be an object with keys: name (snake_case string), description (string, <=120 chars), optional response_layer (string), optional depth (integer 1-5), optional glyph_type (string), optional symbolic_pairing (string). If there are no glyphs, return {\"glyphs\": []}."
          },
          {
            role: "user",
            content: `User message: "${message}"\n\nReturn exactly one JSON object: {"glyphs": [ ... ]}. Example: {"glyphs":[{"name":"chest_tightening","description":"A physical sensation...","response_layer":"inner_reflection","depth":4}]}\nDo NOT include any additional text.`
          }
        ],
        // Use very low temperature for deterministic extraction
        temperature: 0.0,
        response_format: { type: "json_object" }
      });
      const raw = extract.choices?.[0]?.message?.content ?? "{}";
      const parsed = JSON.parse(raw);
      const glyphs = Array.isArray(parsed?.glyphs) ? parsed.glyphs : [];
      parsedGlyphs = glyphs.filter((g) => g?.name && typeof g.name === "string").map((g) => ({
        name: String(g.name).slice(0, 80),
        description: String(g.description ?? "").slice(0, 300),
        response_layer: g.response_layer ? String(g.response_layer).slice(0, 80) : undefined,
        depth: Number.isFinite(Number(g.depth)) ? Math.max(1, Math.min(5, Number(g.depth))) : undefined,
        glyph_type: g.glyph_type ? String(g.glyph_type).slice(0, 80) : undefined,
        symbolic_pairing: g.symbolic_pairing ? String(g.symbolic_pairing).slice(0, 80) : undefined
      }));
    } catch (err) {
      console.error("Glyph extraction failed:", err);
      parsedGlyphs = [];
    }

    // Build response object
    const processingTime = `${Date.now() - startTime}ms`;
    const response = {
      reply,
      glyph: matchedTag,
      parsed_glyphs: parsedGlyphs,
      upserted_glyphs: [],
      log: {
        processing_time: processingTime,
        method: "optimized_with_extraction",
        emotions_detected: [],
        user_id: userId || null,
        learning_active: false,
        cache_used: false,
        privacy_mode: "anonymous"
      }
    };

    return new Response(JSON.stringify(response), { status: 200, headers: corsHeaders });
  } catch (err) {
    console.error("Unexpected processing error:", err);
    return new Response(JSON.stringify({ error: "Internal server error" }), { status: 500, headers: corsHeaders });
  }
});
