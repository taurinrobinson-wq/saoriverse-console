/*
Enhanced Edge Function Integration
Adds OpenAI response learning to the optimized edge function
Creates feedback loop: OpenAI response → local vocabulary expansion → eventually replace OpenAI calls
*/

// This code should be added to your Supabase edge function to enhance learning

// Add this to the end of your clean_optimized_edge_function.ts
const ENHANCED_LEARNING_CODE = `
// LEARNING ENHANCEMENT: Analyze OpenAI responses for local vocabulary building
async function analyzeForLearning(userMessage, aiResponse) {
  try {
    // Extract emotional keywords from user message
    const emotionalKeywords = extractEmotionalKeywords(userMessage);
    
    // Extract response patterns from AI response
    const responsePatterns = extractResponsePatterns(aiResponse);
    
    // Identify key phrases for future quick responses
    const keyPhrases = extractKeyPhrases(aiResponse);
    
    // Store learning data
    const learningData = {
      timestamp: new Date().toISOString(),
      user_emotions: emotionalKeywords,
      ai_patterns: responsePatterns,
      key_phrases: keyPhrases,
      confidence: calculateLearningConfidence(emotionalKeywords, responsePatterns)
    };
    
    // Store in database for future local processing
    await storeLearningData(learningData);
    
    return learningData;
  } catch (err) {
    console.error("Learning analysis failed:", err);
    return null;
  }
}

function extractEmotionalKeywords(message) {
  const emotionCategories = {
    grief: ['grief', 'loss', 'mourning', 'sorrow', 'died', 'death', 'funeral', 'missing'],
    joy: ['joy', 'happy', 'excited', 'celebrate', 'amazing', 'wonderful', 'delight'],
    anxiety: ['anxious', 'worry', 'panic', 'stress', 'overwhelm', 'nervous', 'fear'],
    love: ['love', 'adore', 'cherish', 'relationship', 'partner', 'romantic'],
    confusion: ['confused', 'unclear', 'lost', 'uncertain', 'ambiguous', 'direction'],
    anger: ['angry', 'mad', 'frustrated', 'annoyed', 'irritated', 'furious']
  };
  
  const messageLower = message.toLowerCase();
  const foundEmotions = {};
  
  for (const [emotion, keywords] of Object.entries(emotionCategories)) {
    const matches = keywords.filter(keyword => messageLower.includes(keyword));
    if (matches.length > 0) {
      foundEmotions[emotion] = matches;
    }
  }
  
  return foundEmotions;
}

function extractResponsePatterns(response) {
  const patterns = {
    acknowledgment: /^(I hear|I sense|I understand|That sounds)/i,
    validation: /(valid|natural|makes sense|understandable|normal)/i,
    guidance: /(consider|might|perhaps|could|what if|try)/i,
    empathy: /(with you|beside you|not alone|together|here for you)/i,
    timeline: /(timeline|time|process|journey|gradually)/i
  };
  
  const foundPatterns = {};
  
  for (const [patternType, regex] of Object.entries(patterns)) {
    if (regex.test(response)) {
      foundPatterns[patternType] = true;
    }
  }
  
  return foundPatterns;
}

function extractKeyPhrases(response) {
  // Split into sentences and find short, impactful ones
  const sentences = response.split(/[.!?]+/).filter(s => s.trim().length > 0);
  
  const keyPhrases = sentences
    .filter(sentence => {
      const wordCount = sentence.trim().split(/\s+/).length;
      return wordCount >= 5 && wordCount <= 15; // Optimal length for quick responses
    })
    .map(sentence => sentence.trim())
    .slice(0, 3); // Top 3 phrases
  
  return keyPhrases;
}

function calculateLearningConfidence(emotions, patterns) {
  const emotionCount = Object.keys(emotions).length;
  const patternCount = Object.keys(patterns).length;
  
  // Higher confidence for clear emotional context + clear response patterns
  return Math.min(0.95, (emotionCount * 0.3 + patternCount * 0.2 + 0.3));
}

async function storeLearningData(learningData) {
  try {
    await admin.from('response_learning').insert([{
      timestamp: learningData.timestamp,
      emotion_keywords: JSON.stringify(learningData.user_emotions),
      response_patterns: JSON.stringify(learningData.ai_patterns),
      key_phrases: JSON.stringify(learningData.key_phrases),
      confidence_score: learningData.confidence,
      created_from_chat: true
    }]);
    
    console.log('Learning data stored with confidence ' + learningData.confidence.toFixed(2));
  } catch (err) {
    console.error("Failed to store learning data:", err);
  }
}

async function getLearnedResponses(userMessage, emotions) {
  try {
    // Query learned responses for similar emotional contexts
    const { data: learnedData } = await admin
      .from('response_learning')
      .select('key_phrases, confidence_score')
      .gte('confidence_score', 0.7)
      .order('confidence_score', { ascending: false })
      .limit(5);
    
    if (learnedData && learnedData.length > 0) {
      // Find best matching learned response
      for (const learned of learnedData) {
        const phrases = JSON.parse(learned.key_phrases || '[]');
        if (phrases.length > 0) {
          return {
            response: phrases[0],
            confidence: learned.confidence_score,
            source: 'learned_from_ai'
          };
        }
      }
    }
    
    return null;
  } catch (err) {
    console.error("Error fetching learned responses:", err);
    return null;
  }
}
`;

export default ENHANCED_LEARNING_CODE;