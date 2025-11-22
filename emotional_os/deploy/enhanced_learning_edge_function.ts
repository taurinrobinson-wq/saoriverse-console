import { createClient } from "npm:@supabase/supabase-js@2.45.4";
import OpenAI from "npm:openai@4.56.0";

// ENHANCED VERSION with OpenAI Response Learning
// Builds local vocabulary from AI responses for eventual OpenAI replacement

const ALLOWED_ORIGINS = [
  "https://taurinrobinson-wq.github.io",
  "https://console.saonyx.com"
];

function getCorsHeaders(req: any) {
  const origin = req.headers.get("Origin");

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

// Performance cache
const responseCache = new Map();
const CACHE_TTL = 60000;

// ENHANCED: Expanded quick responses with learning integration
const QUICK_RESPONSES: Record<string, string> = {
  "grief": "I hear the weight of your loss. Grief has its own timeline, and there's no rushing through it.",
  "joy": "There's something beautiful about joy that doesn't need explanation, isn't there?",
  "confusion": "That foggy feeling can be disorienting. Sometimes sitting with uncertainty is the only way through.",
  "anxiety": "Anxiety can feel overwhelming. What's one small thing that might help ground you right now?",
  "love": "Love has its own language, doesn't it? What's that feeling teaching you?",
  "anger": "Anger often points to something that matters deeply to you. What boundary is trying to be heard?",
  "overwhelm": "When everything feels like too much, sometimes the kindest thing is to focus on just the next breath.",
  "healing": "Healing rarely follows a straight line. What feels most supportive for you right now?",
  "vulnerable": "Vulnerability takes courage. Thank you for sharing something so tender."
};

// LEARNING SYSTEM: Analyze OpenAI responses for vocabulary building
async function analyzeForLearning(userMessage: string, aiResponse: string, admin: any) {
  try {
    const emotionalKeywords = extractEmotionalKeywords(userMessage);
    const responsePatterns = extractResponsePatterns(aiResponse);
    const keyPhrases = extractKeyPhrases(aiResponse);

    const learningData = {
      timestamp: new Date().toISOString(),
      user_emotions: emotionalKeywords,
      ai_patterns: responsePatterns,
      key_phrases: keyPhrases,
      confidence: calculateLearningConfidence(emotionalKeywords, responsePatterns, keyPhrases)
    };

    // Store in response_learning table
    await storeLearningData(learningData, admin);

    return learningData;
  } catch (err) {
    console.error("Learning analysis failed:", err);
    return null;
  }
}

function extractEmotionalKeywords(message: string): Record<string, string[]> {
  const emotionCategories = {
    grief: ['grief', 'loss', 'mourning', 'sorrow', 'died', 'death', 'funeral', 'missing', 'gone'],
    joy: ['joy', 'happy', 'excited', 'celebrate', 'amazing', 'wonderful', 'delight', 'thrilled'],
    anxiety: ['anxious', 'worry', 'panic', 'stress', 'overwhelm', 'nervous', 'fear', 'tense'],
    love: ['love', 'adore', 'cherish', 'relationship', 'partner', 'romantic', 'connection'],
    confusion: ['confused', 'unclear', 'lost', 'uncertain', 'ambiguous', 'direction', 'foggy'],
    anger: ['angry', 'mad', 'frustrated', 'annoyed', 'irritated', 'furious', 'rage'],
    healing: ['healing', 'recovery', 'growth', 'progress', 'transformation', 'journey'],
    vulnerable: ['vulnerable', 'exposed', 'tender', 'raw', 'open', 'fragile', 'sensitive']
  };

  const messageLower = message.toLowerCase();
  const foundEmotions: Record<string, string[]> = {};

  for (const [emotion, keywords] of Object.entries(emotionCategories)) {
    const matches = keywords.filter(keyword => messageLower.includes(keyword));
    if (matches.length > 0) {
      foundEmotions[emotion] = matches;
    }
  }

  return foundEmotions;
}

function extractResponsePatterns(response: string): Record<string, boolean> {
  const patterns = {
    acknowledgment: /^(I hear|I sense|I understand|That sounds)/i,
    validation: /(valid|natural|makes sense|understandable|normal)/i,
    guidance: /(consider|might|perhaps|could|what if|try)/i,
    empathy: /(with you|beside you|not alone|together|here for you)/i,
    timeline: /(timeline|time|process|journey|gradually)/i,
    question: /\?/,
    metaphor: /(like|as if|imagine|picture|seems like)/i
  };

  const foundPatterns: Record<string, boolean> = {};

  for (const [patternType, regex] of Object.entries(patterns)) {
    foundPatterns[patternType] = regex.test(response);
  }

  return foundPatterns;
}

function extractKeyPhrases(response: string): string[] {
  const sentences = response.split(/[.!?]+/).filter(s => s.trim().length > 0);

  const keyPhrases = sentences
    .filter(sentence => {
      const wordCount = sentence.trim().split(/\s+/).length;
      return wordCount >= 4 && wordCount <= 12; // Good for future quick responses
    })
    .map(sentence => sentence.trim())
    .slice(0, 3);

  return keyPhrases;
}

function calculateLearningConfidence(emotions: Record<string, string[]>, patterns: Record<string, boolean>, phrases: string[]): number {
  const emotionCount = Object.keys(emotions).length;
  const patternCount = Object.values(patterns).filter(Boolean).length;
  const phraseCount = phrases.length;

  // Higher confidence for clear emotional context + response patterns + useful phrases
  const baseScore = Math.min(0.95, (emotionCount * 0.25 + patternCount * 0.15 + phraseCount * 0.1 + 0.4));
  return Math.round(baseScore * 100) / 100;
}

async function storeLearningData(learningData: any, admin: any) {
  try {
    // Create table if it doesn't exist
    await admin.from('response_learning').upsert([{
      id: `learning_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: learningData.timestamp,
      emotion_keywords: JSON.stringify(learningData.user_emotions),
      response_patterns: JSON.stringify(learningData.ai_patterns),
      key_phrases: JSON.stringify(learningData.key_phrases),
      confidence_score: learningData.confidence,
      created_from_chat: true,
      last_updated: learningData.timestamp
    }], { onConflict: 'id' });

    console.log(`Learning stored: ${Object.keys(learningData.user_emotions).length} emotions, confidence ${learningData.confidence}`);
  } catch (err) {
    console.error("Failed to store learning data:", err);
  }
}

async function getLearnedResponse(userMessage: string, emotions: Record<string, string[]>, admin: any): Promise<string | null> {
  try {
    if (Object.keys(emotions).length === 0) return null;

    const { data: learnedData } = await admin
      .from('response_learning')
      .select('key_phrases, confidence_score, emotion_keywords')
      .gte('confidence_score', 0.7)
      .order('confidence_score', { ascending: false })
      .limit(10);

    if (learnedData && learnedData.length > 0) {
      for (const learned of learnedData) {
        try {
          const learnedEmotions = JSON.parse(learned.emotion_keywords || '{}');
          const phrases = JSON.parse(learned.key_phrases || '[]');

          // Check if current emotions match learned emotions
          const emotionMatch = Object.keys(emotions).some(emotion =>
            Object.keys(learnedEmotions).includes(emotion)
          );

          if (emotionMatch && phrases.length > 0) {
            console.log(`Using learned response with confidence ${learned.confidence_score}`);
            return phrases[0];
          }
        } catch (parseErr) {
          // Skip malformed entries
          continue;
        }
      }
    }

    return null;
  } catch (err) {
    console.error("Error fetching learned responses:", err);
    return null;
  }
}

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

  // Check cache first
  const cacheKey = generateCacheKey(message, mode);
  const cached = responseCache.get(cacheKey);

  if (cached && (Date.now() - cached.timestamp < CACHE_TTL)) {
    console.log("Cache hit");
    return new Response(JSON.stringify(cached.response), {
      status: 200, headers: corsHeaders
    });
  }

  // Initialize clients
  const userClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
  const openai = new OpenAI({ apiKey: OPENAI_API_KEY });

  const startTime = Date.now();

  // ENHANCED: Extract emotions for learning
  const detectedEmotions = extractEmotionalKeywords(message);

  // Try learned responses first (eventual OpenAI replacement)
  const learnedResponse = await getLearnedResponse(message, detectedEmotions, admin);
  if (learnedResponse) {
    const response = {
      reply: learnedResponse,
      glyph: null,
      parsed_glyphs: [],
      upserted_glyphs: [],
      log: {
        processing_time: `${Date.now() - startTime}ms`,
        method: "learned_response",
        emotions_detected: Object.keys(detectedEmotions),
        source: "local_learning"
      }
    };

    responseCache.set(cacheKey, { response, timestamp: Date.now() });
    return new Response(JSON.stringify(response), {
      status: 200, headers: corsHeaders
    });
  }

  // Fall back to quick responses
  const quickResponse = getQuickResponse(message);
  if (quickResponse && mode === "quick") {
    const response = {
      reply: quickResponse,
      glyph: null,
      parsed_glyphs: [],
      upserted_glyphs: [],
      log: {
        processing_time: `${Date.now() - startTime}ms`,
        method: "quick_response",
        emotions_detected: Object.keys(detectedEmotions)
      }
    };

    responseCache.set(cacheKey, { response, timestamp: Date.now() });
    return new Response(JSON.stringify(response), {
      status: 200, headers: corsHeaders
    });
  }

  // Full OpenAI processing with parallel operations
  const [tagResult, aiResult] = await Promise.allSettled([
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

    (async () => {
      const systemPrompt = `You are Saori, an emotionally intelligent companion.
Respond conversationally and supportively. Keep responses concise and under 150 words.
Focus on emotional resonance rather than lengthy explanations.`;

      return await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: message }
        ],
        temperature: 0.7,
        max_tokens: 200,
        stream: false
      });
    })()
  ]);

  const matchedTag = tagResult.status === 'fulfilled' ? tagResult.value : null;
  const completion = aiResult.status === 'fulfilled' ? aiResult.value : null;

  // Build a deterministic choice for short/generic fallbacks so that
  // responses feel less repetitive across platforms.
  const _fallbackAlternatives = [
    "I hear you — tell me more when you're ready.",
    "I'm listening. What's coming up for you right now?",
    "Thank you for sharing. I'm here to listen and support you."
  ];

  function _stableChoice(seed: string, choices: string[]) {
    let h = 0;
    for (let i = 0; i < seed.length; i++) {
      h = (h << 5) - h + seed.charCodeAt(i);
      h |= 0;
    }
    return choices[Math.abs(h) % choices.length];
  }

  let reply = completion?.choices?.[0]?.message?.content ?? _stableChoice(message || (completion?.id || ''), _fallbackAlternatives);

  // ENHANCED: Learn from OpenAI response for future local processing
  const genericFallbacks = new Set(["I'm here to listen.", "I'm here to listen and help.", "I'm here to listen and support you."]);
  if (completion && !genericFallbacks.has(reply)) {
    analyzeForLearning(message, reply, admin).catch(err =>
      console.error("Learning analysis failed:", err)
    );
  }

  // Simplified glyph processing for complex messages
  const shouldProcessGlyphs = message.length > 50 && mode !== "quick";
  const parsedGlyphs: any[] = [];

  if (shouldProcessGlyphs) {
    try {
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
    upserted_glyphs: [],
    log: {
      processing_time: `${processingTime}ms`,
      method: shouldProcessGlyphs ? "full_processing_with_learning" : "optimized_with_learning",
      emotions_detected: Object.keys(detectedEmotions),
      learning_active: true,
      cache_used: false
    }
  };

  // Cache the response
  responseCache.set(cacheKey, { response, timestamp: Date.now() });

  return new Response(JSON.stringify(response), {
    status: 200, headers: corsHeaders
  });
});