import { createClient } from "npm:@supabase/supabase-js@2.45.4";
import OpenAI from "npm:openai@4.56.0";

// PERFORMANCE OPTIMIZATIONS:
// 1. Response caching for repeated queries
// 2. Parallel processing where possible
// 3. Quick responses for common emotions
// 4. Faster OpenAI model selection
// 5. Selective glyph processing

const ALLOWED_ORIGINS = [
  "https://taurinrobinson-wq.github.io",
  "https://console.saonyx.com"
];

function getCorsHeaders(req: any) {
  const origin = req.headers.get("Origin");
  
  // Allow Streamlit Community Cloud domains (*.streamlit.app)
  const isStreamlitApp = origin && origin.includes(".streamlit.app");
  const isLocalhost = origin && (origin.includes("localhost") || origin.includes("127.0.0.1"));
  
  let allowOrigin;
  if (ALLOWED_ORIGINS.includes(origin)) {
    allowOrigin = origin;
  } else if (isStreamlitApp || isLocalhost) {
    allowOrigin = origin;
  } else {
    allowOrigin = ALLOWED_ORIGINS[0];
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

// PERFORMANCE: Cache for recent responses
const responseCache = new Map();
const CACHE_TTL = 60000; // 1 minute cache

// PERFORMANCE: Pre-computed common emotional responses
const QUICK_RESPONSES: Record<string, string> = {
  "grief": "I hear the weight of your loss. Grief has its own timeline, and there's no rushing through it.",
  "joy": "There's something beautiful about joy that doesn't need explanation, isn't there?",
  "confusion": "That foggy feeling can be disorienting. Sometimes sitting with uncertainty is the only way through.",
  "anxiety": "Anxiety can feel overwhelming. What's one small thing that might help ground you right now?",
  "love": "Love has its own language, doesn't it? What's that feeling teaching you?",
  "anger": "Anger often points to something that matters deeply to you. What boundary is trying to be heard?",
  "overwhelm": "When everything feels like too much, sometimes the kindest thing is to focus on just the next breath."
};

function getQuickResponse(message: string): string | null {
  const lowerMessage = message.toLowerCase();
  
  for (const [emotion, response] of Object.entries(QUICK_RESPONSES)) {
    if (lowerMessage.includes(emotion)) {
      return response;
    }
  }
  return null;
}

function generateCacheKey(message: string, mode: string): string {
  return `${message.toLowerCase().slice(0, 50)}_${mode}`;
}

// Environment check
(function assertEnv() {
  const missing = [];
  if (!SUPABASE_URL) missing.push("SUPABASE_URL");
  if (!SUPABASE_ANON_KEY) missing.push("PROJECT_ANON_KEY|SUPABASE_ANON_KEY");
  if (!SUPABASE_SERVICE_ROLE_KEY) missing.push("PROJECT_SERVICE_ROLE_KEY|SUPABASE_SERVICE_ROLE_KEY");
  if (!OPENAI_API_KEY) missing.push("OPENAI_API_KEY");
  if (missing.length) console.error(`saori-fixed missing env: ${missing.join(", ")}`);
})();

Deno.serve(async (req: any) => {
  const corsHeaders = getCorsHeaders(req);
  
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }
  
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method Not Allowed" }), {
      status: 405, headers: corsHeaders
    });
  }

  let body;
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON" }), {
      status: 400, headers: corsHeaders
    });
  }

  const message = body?.message?.toString?.().trim();
  const mode = body?.mode?.toString?.() || "quick";
  
  if (!message) {
    return new Response(JSON.stringify({ error: "Missing 'message'" }), {
      status: 400, headers: corsHeaders
    });
  }

  // PERFORMANCE OPTIMIZATION 1: Check cache first
  const cacheKey = generateCacheKey(message, mode);
  const cached = responseCache.get(cacheKey);
  
  if (cached && (Date.now() - cached.timestamp < CACHE_TTL)) {
    console.log("Cache hit for message");
    return new Response(JSON.stringify(cached.response), {
      status: 200, headers: corsHeaders
    });
  }

  // PERFORMANCE OPTIMIZATION 2: Quick response for simple emotions
  const quickResponse = getQuickResponse(message);
  if (quickResponse && mode === "quick") {
    const response = {
      reply: quickResponse,
      glyph: null,
      parsed_glyphs: [],
      upserted_glyphs: [],
      log: { processing_time: "< 0.1s", method: "quick_response" }
    };
    
    // Cache the quick response
    responseCache.set(cacheKey, { response, timestamp: Date.now() });
    
    return new Response(JSON.stringify(response), {
      status: 200, headers: corsHeaders
    });
  }

  // Initialize clients for full processing
  const userClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
  const openai = new OpenAI({ apiKey: OPENAI_API_KEY });

  // PERFORMANCE OPTIMIZATION 3: Parallel processing setup
  const startTime = Date.now();
  
  // Start tag lookup and OpenAI call in parallel
  const [tagResult, aiResult] = await Promise.allSettled([
    // Tag lookup (faster operation)
    (async () => {
      const input = message.toLowerCase();
      const wantsPlain = /plain|simple|normal|talk normal|conversational|less mythic/.test(input);
      
      if (wantsPlain) {
        const { data } = await admin.from("emotional_tags").select("*").eq("tag_name", "plain").single();
        return data;
      }
      
      const { data } = await userClient.from("emotional_tags").select("*").ilike("tag_name", `%${input}%`);
      return data?.[0] || null;
    })(),
    
    // OpenAI call (slower operation) - PERFORMANCE: Use faster model
    (async () => {
      const systemPrompt = `You are Saori, an emotionally intelligent companion.
Respond conversationally and supportively. Keep responses concise and under 150 words.
Focus on emotional resonance rather than lengthy explanations.`;

      return await openai.chat.completions.create({
        model: "gpt-4o-mini", // Faster model
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: message }
        ],
        temperature: 0.7,
        max_tokens: 200, // PERFORMANCE: Limit response length
        stream: false
      });
    })()
  ]);

  // Extract results
  const matchedTag = tagResult.status === 'fulfilled' ? tagResult.value : null;
  const completion = aiResult.status === 'fulfilled' ? aiResult.value : null;
  
  const reply = completion?.choices?.[0]?.message?.content ?? "I'm here to listen.";

  // PERFORMANCE OPTIMIZATION 4: Conditional glyph processing
  // Only do heavy glyph processing for complex messages
  const shouldProcessGlyphs = message.length > 50 && mode !== "quick";
  const parsedGlyphs: any[] = [];
  const upsertedGlyphs: any[] = [];

  if (shouldProcessGlyphs) {
    try {
      // Simplified glyph extraction - much faster than full processing
      const glyphPattern = /feeling|emotion|heart|soul|deep|profound|sacred|intense/i;
      
      if (glyphPattern.test(message)) {
        parsedGlyphs.push({
          name: "complex_emotion",
          description: "Complex emotional state detected",
          depth: 3
        });
      }
    } catch (err) {
      console.error("Glyph processing error:", err);
    }
  }

  const processingTime = Date.now() - startTime;
  
  const response = {
    reply,
    glyph: matchedTag,
    parsed_glyphs: parsedGlyphs,
    upserted_glyphs: upsertedGlyphs,
    log: {
      processing_time: `${processingTime}ms`,
      method: shouldProcessGlyphs ? "full_processing" : "optimized",
      cache_used: false
    }
  };

  // Cache successful responses
  responseCache.set(cacheKey, { response, timestamp: Date.now() });

  return new Response(JSON.stringify(response), {
    status: 200, headers: corsHeaders
  });
});