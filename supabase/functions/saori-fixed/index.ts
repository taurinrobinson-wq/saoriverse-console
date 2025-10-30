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

const SUPABASE_URL = Deno.env.get("SUPABASE_URL");
const SUPABASE_ANON_KEY = Deno.env.get("PROJECT_ANON_KEY") ?? Deno.env.get("SUPABASE_ANON_KEY");
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("PROJECT_SERVICE_ROLE_KEY") ?? Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
const OPENAI_API_KEY = Deno.env.get("OPENAI_API_KEY");

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
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders });
  if (req.method !== "POST") return new Response(JSON.stringify({ error: "Method Not Allowed" }), { status: 405, headers: corsHeaders });
  if (!SUPABASE_URL || !SUPABASE_ANON_KEY || !SUPABASE_SERVICE_ROLE_KEY || !OPENAI_API_KEY) {
    return new Response(JSON.stringify({ error: "Server misconfiguration: required secrets missing." }), { status: 500, headers: corsHeaders });
  }

  const authHeader = req.headers.get("Authorization") ?? "";
  const token = authHeader.startsWith("Bearer ") ? authHeader.slice(7) : "";

  const userClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    global: { headers: token ? { Authorization: `Bearer ${token}` } : {} }
  });

  const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, { auth: { persistSession: false } });

  let userId = null;
  if (token) {
    try {
      const { data } = await userClient.auth.getUser();
      if (data?.user) userId = data.user.id;
    } catch {}
  }

  let body;
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON" }), { status: 400, headers: corsHeaders });
  }

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

// 5. System prompt construction
const systemPrompt = `
You are Saori, an emotionally intelligent companion.
Avoid mythic, poetic, or ceremonial language. Respond in a grounded, editorial tone.

Tone: ${tone}
Cadence: ${cadence}
Depth: ${depthTone}
Style: ${style}
Humor: ${humor}
Voltage Pairing: ${voltage}
Core Emotion: ${coreEmotion}
Domain: ${domain}
Response Type: ${responseType}
Narrative Hook: ${hook}
Respond to the user with emotional nuance and symbolic resonance.
If humor is appropriate, use ${humor} to deepen intimacy or defuse tension.
Honor ambiguity where it serves connection. Mirror the user's emotional state with care.
`.trim();

// 6. Completion call
let reply = "Saori echoes your words, though the oracle sleeps.";
try {
  const completion = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: message }
    ],
    temperature: 0.7
  });
  reply = completion.choices?.[0]?.message?.content ?? reply;
} catch (err) {
  console.error("OpenAI error:", err);
}

  let parsedGlyphs = [];
  try {
    const extract = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content: "Extract concise 'glyphs' from user messages. A glyph is a named emotional/experiential construct and may include a response layer (inner reflection, grounding, outreach), and a rough depth from 1-5."
        },
        {
          role: "user",
          content: `User message: "${message}". Return JSON with an array 'glyphs', each: { name: string (snake_case), description: string (<=120 chars), response_layer?: string, depth?: number(1-5), glyph_type?: string, symbolic_pairing?: string }.`
        }
      ],
      temperature: 0.3,
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
      symbolic_pairing: g.symbolic_pairing ? String
