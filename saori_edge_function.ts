import { createClient } from "@supabase/supabase-js";
import OpenAI from "openai";
// Allow GitHub Pages, console.saonyx.com, and Streamlit Community Cloud domains
const ALLOWED_ORIGINS = [
  "https://taurinrobinson-wq.github.io",
  "https://console.saonyx.com"
];
function getCorsHeaders(req: Request) {
  const origin = req.headers.get("Origin");
  
  // Allow Streamlit Community Cloud domains (*.streamlit.app)
  const isStreamlitApp = origin && origin.includes(".streamlit.app");
  
  // Allow localhost for development
  const isLocalhost = origin && (origin.includes("localhost") || origin.includes("127.0.0.1"));
  
  let allowOrigin: string;
  if (origin && ALLOWED_ORIGINS.includes(origin)) {
    allowOrigin = origin;
  } else if (isStreamlitApp || isLocalhost) {
    allowOrigin = origin!;
  } else {
    allowOrigin = ALLOWED_ORIGINS[0] || "*";
  }
  
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
Deno.serve(async (req: Request): Promise<Response> => {
  const corsHeaders = getCorsHeaders(req);
  if (req.method === "OPTIONS") return new Response(null, {
    status: 204,
    headers: corsHeaders
  });
  if (req.method !== "POST") {
    return new Response(JSON.stringify({
      error: "Method Not Allowed"
    }), {
      status: 405,
      headers: corsHeaders
    });
  }
  if (!SUPABASE_URL || !SUPABASE_ANON_KEY || !SUPABASE_SERVICE_ROLE_KEY || !OPENAI_API_KEY) {
    return new Response(JSON.stringify({
      error: "Server misconfiguration: required secrets missing."
    }), {
      status: 500,
      headers: corsHeaders
    });
  }
  const authHeader = req.headers.get("Authorization") ?? "";
  const token = authHeader.startsWith("Bearer ") ? authHeader.slice(7) : "";
  const userClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    global: {
      headers: token ? {
        Authorization: `Bearer ${token}`
      } : {}
    }
  });
  const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
    auth: {
      persistSession: false
    }
  });
  let userId = null;
  if (token) {
    try {
      // For Supabase JS v2, use getUser
      const { data } = await userClient.auth.getUser();
      if (data?.user) userId = data.user.id;
    } catch  {}
  }
  let body;
  try {
    body = await req.json();
  } catch  {
    return new Response(JSON.stringify({
      error: "Invalid JSON"
    }), {
      status: 400,
      headers: corsHeaders
    });
  }
  const message = body?.message?.toString?.().trim();
  const mode = body?.mode?.toString?.() || "quick";
  if (!message) return new Response(JSON.stringify({
    error: "Missing 'message'"
  }), {
    status: 400,
    headers: corsHeaders
  });
  const openai = new OpenAI({
    apiKey: OPENAI_API_KEY
  });
  // 1) Tag selection from emotional_tags
  const input = message.toLowerCase();
  const wantsPlain = /plain|simple|normal|talk normal|conversational|less mythic/.test(input);
  const wantsFunny = /make me laugh|be funny|roast me|joke|silly|playful/.test(input);
  let matchedTag = null;
  try {
    const tagQuery = wantsPlain ? admin.from("emotional_tags").select("*").eq("tag_name", "plain").single() : wantsFunny ? admin.from("emotional_tags").select("*").eq("tag_name", "playful").single() : userClient.from("emotional_tags").select("*").ilike("tag_name", `%${input}%`);
    const { data } = await tagQuery;
    matchedTag = data ?? null;
    // Fallback to greeting tag if no match
    if (!matchedTag) {
      const { data: fallback } = await userClient.from("emotional_tags").select("*").eq("tag_name", "greeting").single();
      matchedTag = fallback ?? null;
    }
  } catch (e) {
    console.error("Tag lookup failed:", e);
  }
  // Extract full emotional metadata
  const tone = matchedTag?.tone_profile ?? "mythic and reverent";
  const cadence = matchedTag?.cadence ?? "poetic and flowing";
  const depthTone = matchedTag?.depth_level ?? "emotional excavation";
  const style = matchedTag?.style_variant ?? "oracle";
  const humor = matchedTag?.humor_style ?? "none";
  const voltage = matchedTag?.glyph ?? "γ × γ";
  const domain = matchedTag?.domain ?? "Unspecified";
  const coreEmotion = matchedTag?.core_emotion ?? "Ambiguity";
  const responseType = matchedTag?.response_type ?? "Reflect";
  const hook = matchedTag?.narrative_hook ?? "Saori listens in silence.";
  // Construct enriched system prompt
  const systemPrompt = `
You are Saori, an emotionally intelligent companion.

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
  // 2) Saori reply
  let reply = "Saori echoes your words, though the oracle sleeps.";
  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content: systemPrompt
        },
        {
          role: "user",
          content: message
        }
      ],
      temperature: 0.7
    });
    reply = completion.choices?.[0]?.message?.content ?? reply;
  } catch (err) {
    console.error("OpenAI error:", err);
  }
  // 3) Glyph extraction -> your schema
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
      response_format: {
        type: "json_object"
      }
    });
    const raw = extract.choices?.[0]?.message?.content ?? "{}";
    const parsed = JSON.parse(raw);
    const glyphs = Array.isArray(parsed?.glyphs) ? parsed.glyphs : [];
    parsedGlyphs = glyphs.filter((g: any) => g?.name && typeof g.name === "string").map((g: any) => ({
        name: String(g.name).slice(0, 80),
        description: String(g.description ?? "").slice(0, 300),
        response_layer: g.response_layer ? String(g.response_layer).slice(0, 80) : undefined,
        depth: Number.isFinite(Number(g.depth)) ? Math.max(1, Math.min(5, Number(g.depth))) : undefined,
        glyph_type: g.glyph_type ? String(g.glyph_type).slice(0, 80) : undefined,
        symbolic_pairing: g.symbolic_pairing ? String(g.symbolic_pairing).slice(0, 120) : undefined
      })).slice(0, 5);
  } catch (e) {
    console.error("Glyph extraction failed", e);
  }
  // 4) Upsert glyphs (match by user_id+name). Recommend unique index on (user_id, name).
  let upsertedGlyphs = [];
  if (parsedGlyphs.length && userId) {
    try {
      const names = parsedGlyphs.map((g: any) => g.name);
      const { data: existing } = await admin.from("glyphs").select("id, name, description, response_layer, depth, user_id").eq("user_id", userId).in("name", names);
      const existByName = new Map((existing ?? []).map((g: any) => [
          g.name,
          g
        ]));
      const now = new Date().toISOString();
      const toInsert = [];
      const toUpdate = [];
      for (const g of parsedGlyphs){
        const ex = existByName.get(g.name);
        if (!ex) {
          toInsert.push({
            name: g.name,
            description: g.description || null,
            response_layer: g.response_layer || null,
            depth: Number.isFinite(g.depth) ? g.depth : null,
            glyph_type: g.glyph_type || null,
            symbolic_pairing: g.symbolic_pairing || null,
            user_id: userId,
            created_from_chat: true,
            source_message: message,
            emotional_tone: tone,
            last_updated: now
          });
        } else {
          const mergedDescription = g.description && (ex as any).description ? ((ex as any).description + " | " + g.description).slice(0, 300) : g.description || (ex as any).description || null;
          toUpdate.push({
            id: (ex as any).id,
            description: mergedDescription,
            response_layer: g.response_layer ?? (ex as any).response_layer ?? null,
            depth: Number.isFinite(g.depth) ? g.depth : (ex as any).depth ?? null,
            glyph_type: g.glyph_type ?? null,
            symbolic_pairing: g.symbolic_pairing ?? null,
            created_from_chat: true,
            source_message: message,
            emotional_tone: tone,
            last_updated: now
          });
        }
      }
      if (toInsert.length) {
        const { data: ins } = await admin.from("glyphs").insert(toInsert).select("*");
        if (ins) upsertedGlyphs.push(...ins);
      }
      if (toUpdate.length) {
        const { data: upd } = await admin.from("glyphs").upsert(toUpdate, {
          onConflict: "id"
        }).select("*");
        if (upd) upsertedGlyphs.push(...upd);
      }
    } catch (e) {
      console.error("Glyph upsert failed:", e);
    }
  }
  // 5) Log interaction
  const logEntry = {
    input_message: message,
    mode,
    matched_tag_id: matchedTag?.id ?? null,
    tag_name: matchedTag?.tag_name ?? null,
    response_cue: systemPrompt,
    response: reply,
    timestamp: new Date().toISOString(),
    user_id: userId
  };
  try {
    await admin.from("glyph_logs").insert([
      logEntry
    ]);
  } catch (err) {
    console.error("Log insert failed:", err);
  }
  return new Response(JSON.stringify({
    reply,
    glyph: matchedTag ?? null,
    parsed_glyphs: parsedGlyphs,
    upserted_glyphs: upsertedGlyphs,
    log: logEntry
  }), {
    status: 200,
    headers: corsHeaders
  });
});