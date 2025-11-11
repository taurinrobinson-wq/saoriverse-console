// Dynamically import subbase JS (npm) in Deno; fall back will surface a clear
// module fetch error if network access is blocked. This lets Deno fetch the
// npm package automatically when running in the Codespace.
export { };

// Try loading the Supabase JS client from a CDN (jsdelivr). This avoids
// requiring Deno to resolve npm packages and should work in offline-free
// environments that allow external module fetches. If the import fails, we
// rethrow so the error is visible in logs.
const SUPABASE_URL = Deno.env.get("SUPABASE_URL");
const SUPABASE_ANON_KEY = Deno.env.get("PROJECT_ANON_KEY") ?? Deno.env.get("SUPABASE_ANON_KEY");
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("PROJECT_SERVICE_ROLE_KEY") ?? Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
const OPENAI_API_KEY = Deno.env.get("OPENAI_API_KEY");

let createClient: any;
try {
  const supabasePkg = await import('https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm');
  createClient = supabasePkg.createClient;
} catch (err) {
  console.error('Failed to import @supabase/supabase-js from CDN:', err);
  throw err;
}

// Inline minimal RLS-aware client factory to avoid depending on the local
// supabaseRlsClient module which may itself import npm packages.
function supabaseRlsClient(token: string) {
  return createClient(SUPABASE_URL!, SUPABASE_ANON_KEY!, {
    global: {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    }
  });
}
// OpenAI npm package may not be available in the local Deno environment.
// Attempt a dynamic import and fall back to a lightweight stub for
// local/dev runs (this lets us exercise Supabase DB paths without
// requiring the real OpenAI package or network access).
let OpenAI: any;
try {
  // top-level await is supported in Deno
  // prefer the npm package when available
  // @ts-ignore
  OpenAI = (await import('openai')).default;
} catch (err) {
  // Fallback stub: provides the minimal chat completions.create API
  // used below and returns a simple canned reply.
  OpenAI = class {
    constructor(opts: any) { }
    chat = {
      completions: {
        create: async (_opts: any) => {
          // If the caller requests a JSON-formatted response (response_format),
          // return a valid JSON string so downstream JSON.parse works during dev.
          if (_opts && _opts.response_format) {
            const payload = { glyphs: [] };
            return { choices: [{ message: { content: JSON.stringify(payload) } }] };
          }
          // Otherwise, return a simple textual reply
          return { choices: [{ message: { content: '(dev stub reply)' } }] };
        }
      }
    };
  };
}
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
// env vars were read above
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
  // Dev-fast can be used without a real OpenAI key; detect the header early
  // so we can allow a reduced set of required secrets during local testing.
  const devFastEarly = (req.headers.get('X-Dev-Fast') || '').toLowerCase() === 'true' || (req.headers.get('X-Dev-Fast') || '') === '1';
  // If not running in dev-fast mode, require all secrets. When dev-fast is
  // active we allow missing keys so local matching can be exercised offline.
  if (!devFastEarly && (!SUPABASE_URL || !SUPABASE_ANON_KEY || !SUPABASE_SERVICE_ROLE_KEY || !OPENAI_API_KEY)) {
    return new Response(JSON.stringify({
      error: "Server misconfiguration: required secrets missing."
    }), {
      status: 500,
      headers: corsHeaders
    });
  }
  const authHeader = req.headers.get("Authorization") ?? "";
  const token = authHeader.startsWith("Bearer ") ? authHeader.slice(7) : "";
  // Create supabase clients only when the environment provides the required
  // variables. In dev-fast mode we may intentionally omit these secrets so we
  // can run purely local matching without DB access.
  let userClient: any = null;
  let admin: any = null;
  if (SUPABASE_URL && SUPABASE_ANON_KEY) {
    userClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
      global: {
        headers: token ? {
          Authorization: `Bearer ${token}`
        } : {}
      }
    });
  }
  if (SUPABASE_URL && SUPABASE_SERVICE_ROLE_KEY) {
    admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
      auth: {
        persistSession: false
      }
    });
  }
  let rlsClient = null;
  try {
    rlsClient = token ? supabaseRlsClient(token) : null;
  } catch (e) {
    console.error('Failed to create RLS client:', e);
    rlsClient = null;
  }
  let userId = null;
  if (token) {
    try {
      // For Supabase JS v2, use getUser
      const { data } = await userClient.auth.getUser();
      if (data?.user) userId = data.user.id;
    } catch { }
  }
  let body;
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify({
      error: "Invalid JSON"
    }), {
      status: 400,
      headers: corsHeaders
    });
  }
  // Developer bypass: allow forcing a user_id for local testing via header
  // `X-Dev-User-Id` or request body `dev_user_id`. This causes the function
  // to exercise the conversation persistence/upsert path using the admin
  // client (bypassing RLS) so we can capture DB errors during debug runs.
  if (!userId) {
    const devHeader = req.headers.get('X-Dev-User-Id');
    if (devHeader) {
      userId = devHeader;
      console.info('Using dev-forced userId from header:', userId);
    } else if (body?.dev_user_id) {
      userId = body.dev_user_id;
      console.info('Using dev-forced userId from body:', userId);
    }
  }
  const message = body?.message?.toString?.().trim();
  const mode = body?.mode?.toString?.() || "quick";
  if (!message) return new Response(JSON.stringify({
    error: "Missing 'message'"
  }), {
    status: 400,
    headers: corsHeaders
  });
  // Dev-fast shortcut: when X-Dev-Fast header is present, skip OpenAI and use
  // a local validated glyph lexicon to produce immediate parsed_glyphs and
  // optionally persist them. This is non-invasive to production because it
  // only runs when the header is explicitly set by a developer/test harness.
  const devFast = (req.headers.get('X-Dev-Fast') || '').toLowerCase() === 'true' || (req.headers.get('X-Dev-Fast') || '') === '1';
  if (devFast) {
    console.info('Dev-fast path engaged: performing local lexicon matching');
    let parsedGlyphs: any[] = [];
    let upsertedGlyphs: any[] = [];
    let reply = '(dev-fast) quick local glyph matching';
    let matchedTag: any = { tag_name: 'dev-fast', id: null, tone_profile: 'dev' };
    try {
      // Load validated lexicon from disk
      const lexPath = './emotional_os/glyphs/glyph_lexicon_rows_validated.json';
      const txt = await Deno.readTextFile(lexPath);
      const lex = JSON.parse(txt);
      // Improved heuristic: normalize input and triggers, tokenize, and apply
      // minimal stemming to improve recall for common inflections.
      const normalize = (s: string) => String(s || '').toLowerCase()
        // replace punctuation with spaces
        .replace(/[\p{P}\p{S}]+/gu, ' ')
        .replace(/\s+/g, ' ')
        .trim();
      const stem = (w: string) => {
        if (!w) return w;
        // simple suffix stripping for common English inflections
        if (w.length > 5 && w.endsWith('ing')) return w.slice(0, -3);
        if (w.length > 4 && w.endsWith('ied')) return w.slice(0, -3) + 'y';
        if (w.length > 3 && w.endsWith('ed')) return w.slice(0, -2);
        if (w.length > 2 && w.endsWith('s')) return w.slice(0, -1);
        return w;
      };
      const normText = normalize(message);
      const textTokens = new Set((normText || '').split(' ').filter(Boolean).map(stem));
      // Small synonym map to capture common emotional paraphrases. Keys and
      // values should be in normalized, lowercased form. This is intentionally
      // small and editable — we can expand it later or load from a file.
      const synonymMap: Record<string, string[]> = {
        'unmoored': ['adrift', 'ungrounded', 'float'],
        'adrift': ['unmoored', 'ungrounded'],
        'furious': ['angry', 'irate', 'enraged'],
        'angry': ['furious', 'irate'],
        'miss': ['longing', 'yearn', 'ache'],
        'ache': ['miss', 'longing'],
        'joy': ['contentment', 'bliss', 'pleasure'],
        'overwhelmed': ['burdened', 'swamped', 'overloaded', 'stressed']
      };
      // Expand text tokens with synonyms (stemmed) to increase recall.
      for (const tk of Array.from(textTokens)) {
        const syns = synonymMap[tk];
        if (Array.isArray(syns)) {
          for (const s of syns) textTokens.add(stem(s));
        }
      }
      // lex entries expected to have: name, description, triggers (array or string)
      const candidates: any[] = [];
      // fuzzy helpers: token similarity with simple edit-distance and substring checks
      const levenshtein = (a: string, b: string) => {
        if (!a || !b) return Math.max(a?.length ?? 0, b?.length ?? 0);
        const m = a.length, n = b.length;
        const dp: number[][] = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
        for (let i = 0; i <= m; i++) dp[i][0] = i;
        for (let j = 0; j <= n; j++) dp[0][j] = j;
        for (let i = 1; i <= m; i++) {
          for (let j = 1; j <= n; j++) {
            const cost = a[i - 1] === b[j - 1] ? 0 : 1;
            dp[i][j] = Math.min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost);
          }
        }
        return dp[m][n];
      };
      const tokenSimilarity = (t1: string, t2: string) => {
        if (!t1 || !t2) return 0;
        if (t1 === t2) return 1;
        if (t1.includes(t2) || t2.includes(t1)) return 0.8;
        const dist = levenshtein(t1, t2);
        const maxLen = Math.max(t1.length, t2.length);
        if (maxLen === 0) return 0;
        const sim = 1 - dist / maxLen;
        return sim > 0.6 ? sim : 0;
      };

      for (const row of lex) {
        const triggers = Array.isArray(row.triggers) ? row.triggers : typeof row.triggers === 'string' ? [row.triggers] : [];
        let score = 0;
        // Exact normalized trigger phrase match (strong)
        for (const t of triggers) {
          if (!t) continue;
          const tNorm = normalize(String(t));
          if (!tNorm) continue;
          if (normText.includes(tNorm)) {
            score += 6;
            continue;
          }
          // token overlap between trigger and text with fuzzy similarity
          const tTokens = (tNorm.split(' ').filter(Boolean).map(stem));
          for (const tk of tTokens) {
            for (const tt of textTokens) {
              const sim = tokenSimilarity(tk, tt);
              if (sim >= 0.95) score += 2; // near exact
              else if (sim >= 0.75) score += 1.2; // fuzzy
            }
          }
        }
        // Name token match (moderate boost) with fuzzy scoring
        if (row.name) {
          const nameNorm = normalize(String(row.name));
          if (nameNorm && normText.includes(nameNorm)) score += 5;
          const nameTokens = (nameNorm.split(' ').filter(Boolean).map(stem));
          for (const nt of nameTokens) {
            for (const tt of textTokens) {
              const sim = tokenSimilarity(nt, tt);
              if (sim >= 0.95) score += 1.5;
              else if (sim >= 0.75) score += 0.8;
            }
          }
        }
        // Accept low-threshold matches: any score > 1.5
        if (score > 1.5) candidates.push({ row, score });
      }
      candidates.sort((a, b) => b.score - a.score);
      const top = candidates.slice(0, 5).map((c) => c.row);
      parsedGlyphs = top.map((g: any) => ({
        name: String(g.name),
        description: g.description ?? null,
        response_layer: g.response_layer ?? null,
        depth: g.depth ?? null,
        glyph_type: g.glyph_type ?? null,
        symbolic_pairing: g.symbolic_pairing ?? null
      }));

      // Persist matches to DB (admin client so RLS doesn't block dev tests).
      // This is best-effort: only run persistence when we actually have a
      // usable admin client and a service role key present in the env.
      if (parsedGlyphs.length && userId && admin && SUPABASE_SERVICE_ROLE_KEY) {
        try {
          const glyphDb = admin; // explicit admin client for dev path
          const names = parsedGlyphs.map((g: any) => g.name);
          const { data: existing } = await glyphDb.from('glyphs').select('id, name, description, response_layer, depth, user_id').eq('user_id', userId).in('name', names);
          const existByName = new Map((existing ?? []).map((g: any) => [g.name, g]));
          const now = new Date().toISOString();
          const toInsert: any[] = [];
          const toUpdate: any[] = [];
          for (const g of parsedGlyphs) {
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
                emotional_tone: 'dev-fast',
                last_updated: now
              });
            } else {
              toUpdate.push({
                id: ex.id,
                description: g.description || ex.description || null,
                response_layer: g.response_layer ?? ex.response_layer ?? null,
                depth: Number.isFinite(g.depth) ? g.depth : ex.depth ?? null,
                glyph_type: g.glyph_type ?? ex.glyph_type ?? null,
                symbolic_pairing: g.symbolic_pairing ?? ex.symbolic_pairing ?? null,
                created_from_chat: true,
                source_message: message,
                emotional_tone: 'dev-fast',
                last_updated: now
              });
            }
          }
          if (toInsert.length) {
            const { data: ins, error: insErr } = await glyphDb.from('glyphs').insert(toInsert).select('*');
            if (insErr) console.error('Dev-fast glyph insert supabase error:', insErr);
            if (ins) upsertedGlyphs.push(...ins);
          }
          if (toUpdate.length) {
            const { data: upd, error: updErr } = await glyphDb.from('glyphs').upsert(toUpdate, { onConflict: 'id' }).select('*');
            if (updErr) console.error('Dev-fast glyph upsert supabase error:', updErr);
            if (upd) upsertedGlyphs.push(...upd);
          }
        } catch (e) {
          console.error('Dev-fast glyph persistence failed:', e);
        }
      } else if (parsedGlyphs.length && userId) {
        console.info('Dev-fast: skipping persistence because admin/service role not available');
      }
    } catch (e) {
      console.error('Dev-fast matching failed:', e);
    }

    const logEntry = {
      input_message: message,
      mode,
      matched_tag_id: matchedTag?.id ?? null,
      tag_name: matchedTag?.tag_name ?? null,
      response_cue: '(dev-fast)',
      response: reply,
      timestamp: new Date().toISOString(),
      user_id: userId
    };
    // Try to write minimal log row (best-effort)
    try {
      const logsDb = admin;
      await logsDb.from('glyph_logs').insert([logEntry]);
    } catch (err) {
      console.error('Dev-fast log insert failed:', err);
    }

    return new Response(JSON.stringify({
      reply,
      glyph: matchedTag ?? null,
      parsed_glyphs: parsedGlyphs,
      upserted_glyphs: upsertedGlyphs,
      log: logEntry,
      dev_fast: true
    }), {
      status: 200,
      headers: corsHeaders
    });
  }
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
      const glyphDb = rlsClient ?? admin;
      const names = parsedGlyphs.map((g: any) => g.name);
      const { data: existing } = await admin.from("glyphs").select("id, name, description, response_layer, depth, user_id").eq("user_id", userId).in("name", names);
      const existByName = new Map((existing ?? []).map((g: any) => [
        g.name,
        g
      ]));
      const now = new Date().toISOString();
      const toInsert = [];
      const toUpdate = [];
      for (const g of parsedGlyphs) {
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
        const { data: ins } = await glyphDb.from("glyphs").insert(toInsert).select("*");
        if (ins) upsertedGlyphs.push(...ins);
      }
      if (toUpdate.length) {
        const { data: upd } = await glyphDb.from("glyphs").upsert(toUpdate, {
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
    const logsDb = rlsClient ?? admin;
    await logsDb.from("glyph_logs").insert([
      logEntry
    ]);
  } catch (err) {
    console.error("Log insert failed:", err);
  }
  // Persist messages and conversation metadata for authenticated users
  try {
    if (userId) {
      // Allow client to pass a conversation_id to continue an existing thread,
      // otherwise generate a new UUID for a new conversation.
      const conversationId = body?.conversation_id || (typeof crypto !== "undefined" && (crypto as any).randomUUID ? (crypto as any).randomUUID() : new Date().toISOString());
      const nowIso = new Date().toISOString();

      // Insert user message as a row in conversation_messages
      try {
        const convDb = rlsClient ?? admin;
        const { data: insertUserData, error: insertUserError } = await convDb.from("conversation_messages").insert([{
          user_id: userId,
          conversation_id: conversationId,
          role: "user",
          message: message,
          first_name: body?.first_name ?? null,
          timestamp: nowIso
        }]);
        if (insertUserError) {
          console.error("Insert user message failed (supabase error):", insertUserError);
        }
      } catch (e) {
        console.error("Insert user message failed (exception):", e);
      }

      // Insert assistant reply as a row in conversation_messages
      try {
        const convDb = rlsClient ?? admin;
        const { data: insertAssistantData, error: insertAssistantError } = await convDb.from("conversation_messages").insert([{
          user_id: userId,
          conversation_id: conversationId,
          role: "assistant",
          message: reply,
          timestamp: new Date().toISOString()
        }]);
        if (insertAssistantError) {
          console.error("Insert assistant message failed (supabase error):", insertAssistantError);
        }
      } catch (e) {
        console.error("Insert assistant message failed (exception):", e);
      }

      // Compute message count for the conversation (exact count)
      let messageCount: number | null = null;
      try {
        const convDb = rlsClient ?? admin;
        const { count } = await convDb.from("conversation_messages").select("id", { count: "exact" }).eq("user_id", userId).eq("conversation_id", conversationId);
        messageCount = typeof count === "number" ? count : null;
      } catch (e) {
        console.error("Count query failed:", e);
      }

      // Fetch existing conversation metadata if present
      let existingConv: any = null;
      try {
        const convDb = rlsClient ?? admin;
        const { data: found } = await convDb.from("conversations").select("id, title, first_message, first_response, message_count, processing_mode, emotional_context, topics, archived").eq("user_id", userId).eq("conversation_id", conversationId).maybeSingle();
        existingConv = found ?? null;
      } catch (e) {
        existingConv = null;
      }

      const upsertRow = {
        user_id: userId,
        conversation_id: conversationId,
        title: existingConv?.title ?? (body?.title ?? "New Conversation"),
        first_message: existingConv?.first_message ?? message,
        first_response: existingConv?.first_response ?? reply,
        message_count: messageCount ?? ((existingConv?.message_count ?? 0) + 2),
        updated_at: nowIso,
        archived: existingConv?.archived ?? false,
        emotional_context: existingConv?.emotional_context ?? (matchedTag ? { tag: matchedTag.tag_name } : {}),
        topics: existingConv?.topics ?? []
      };

      try {
        const convDb = rlsClient ?? admin;
        const { data: upsertData, error: upsertError } = await convDb.from("conversations").upsert([upsertRow], { onConflict: "user_id,conversation_id" }).select();
        if (upsertError) {
          console.error("Conversation metadata upsert failed (supabase error):", upsertError, "upsertRow:", upsertRow);
        }
      } catch (e) {
        console.error("Conversation metadata upsert failed (exception):", e, "upsertRow:", upsertRow);
      }
    }
  } catch (e) {
    console.error("Conversation persistence error:", e);
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