"""
Enhanced Learning Pipeline: OpenAI Response → Local Vocabulary Builder
Analyzes OpenAI responses to extract emotional patterns and expand local capabilities
"""

import json
import re
import sqlite3
from collections import defaultdict, Counter
from datetime import datetime
import logging
from typing import Dict, List, Tuple, Set
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

class OpenAIResponseLearner:
    """
    Learns from OpenAI responses to build local emotional intelligence
    Goal: Eventually replace OpenAI calls with learned local responses
    """
    
    def __init__(self, db_path="glyphs.db"):
        self.db_path = db_path
        self.setup_logging()
        self.init_nltk_resources()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Enhanced emotional vocabulary categories
        self.emotional_categories = {
            'grief': ['loss', 'mourning', 'sorrow', 'ache', 'weight', 'heavy', 'timeline', 'rushing'],
            'joy': ['beautiful', 'celebration', 'light', 'bubbling', 'wonderful', 'amazing', 'delight'],
            'anxiety': ['overwhelming', 'worry', 'tension', 'ground', 'calm', 'breathe', 'center'],
            'confusion': ['unclear', 'foggy', 'uncertain', 'ambiguous', 'clarity', 'direction'],
            'love': ['connection', 'warmth', 'intimacy', 'bond', 'cherish', 'devotion', 'heart'],
            'anger': ['boundary', 'frustration', 'injustice', 'violation', 'respect', 'limit'],
            'healing': ['process', 'growth', 'transformation', 'journey', 'progress', 'recovery'],
            'vulnerability': ['exposed', 'tender', 'raw', 'open', 'fragile', 'sensitive', 'courage']
        }
        
        self.response_patterns = {
            'acknowledgment': ['I hear', 'I sense', 'I understand', 'That sounds', 'I can feel'],
            'validation': ['valid', 'natural', 'makes sense', 'understandable', 'normal'],
            'guidance': ['consider', 'might', 'perhaps', 'could', 'what if', 'try'],
            'empathy': ['with you', 'beside you', 'not alone', 'together', 'here for you'],
            'reframing': ['another way', 'different perspective', 'also', 'while', 'and yet']
        }
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def init_nltk_resources(self):
        """Download required NLTK resources if not present"""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords') 
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('vader_lexicon')
            
    def analyze_openai_response(self, user_message: str, ai_response: str) -> Dict:
        """
        Analyze OpenAI response to extract learning patterns
        Returns structured data for local vocabulary building
        """
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'user_emotion_keywords': self.extract_emotion_keywords(user_message),
            'ai_response_patterns': self.extract_response_patterns(ai_response),
            'emotional_sentiment': self.analyze_sentiment(user_message, ai_response),
            'key_phrases': self.extract_key_phrases(ai_response),
            'response_structure': self.analyze_response_structure(ai_response),
            'learning_opportunities': []
        }
        
        # Identify learning opportunities
        analysis['learning_opportunities'] = self.identify_learning_patterns(
            user_message, ai_response, analysis
        )
        
        return analysis
    
    def extract_emotion_keywords(self, message: str) -> Dict[str, List[str]]:
        """Extract emotional keywords from user message"""
        message_lower = message.lower()
        words = word_tokenize(message_lower)
        
        found_emotions = {}
        for emotion, keywords in self.emotional_categories.items():
            matches = [word for word in words if any(kw in word for kw in keywords)]
            if matches:
                found_emotions[emotion] = matches
                
        return found_emotions
    
    def extract_response_patterns(self, response: str) -> Dict[str, List[str]]:
        """Extract response patterns from AI response"""
        response_lower = response.lower()
        
        found_patterns = {}
        for pattern_type, patterns in self.response_patterns.items():
            matches = [p for p in patterns if p in response_lower]
            if matches:
                found_patterns[pattern_type] = matches
                
        return found_patterns
    
    def analyze_sentiment(self, user_message: str, ai_response: str) -> Dict:
        """Analyze sentiment flow from user to AI response"""
        user_sentiment = self.sentiment_analyzer.polarity_scores(user_message)
        ai_sentiment = self.sentiment_analyzer.polarity_scores(ai_response)
        
        return {
            'user_sentiment': user_sentiment,
            'ai_sentiment': ai_sentiment,
            'sentiment_shift': {
                'compound_change': ai_sentiment['compound'] - user_sentiment['compound'],
                'emotional_direction': self.determine_emotional_direction(user_sentiment, ai_sentiment)
            }
        }
    
    def determine_emotional_direction(self, user_sent: Dict, ai_sent: Dict) -> str:
        """Determine if AI response is stabilizing, uplifting, or reflecting"""
        user_compound = user_sent['compound']
        ai_compound = ai_sent['compound']
        
        if ai_compound > user_compound + 0.1:
            return 'uplifting'
        elif ai_compound < user_compound - 0.1:
            return 'deepening'  # Going deeper into emotion
        else:
            return 'reflecting'  # Mirroring emotional state
    
    def extract_key_phrases(self, response: str) -> List[str]:
        """Extract key phrases that could become local responses"""
        sentences = sent_tokenize(response)
        key_phrases = []
        
        # Look for short, impactful sentences (good for local responses)
        for sentence in sentences:
            if 5 <= len(sentence.split()) <= 15:  # Optimal length for quick responses
                key_phrases.append(sentence.strip())
        
        return key_phrases[:3]  # Top 3 phrases
    
    def analyze_response_structure(self, response: str) -> Dict:
        """Analyze the structure of AI responses for pattern learning"""
        sentences = sent_tokenize(response)
        
        structure = {
            'sentence_count': len(sentences),
            'avg_sentence_length': sum(len(s.split()) for s in sentences) / len(sentences),
            'starts_with_acknowledgment': any(ack in sentences[0].lower() for ack in ['i hear', 'i sense', 'that sounds']),
            'includes_question': any('?' in s for s in sentences),
            'includes_metaphor': self.detect_metaphor(response)
        }
        
        return structure
    
    def detect_metaphor(self, text: str) -> bool:
        """Simple metaphor detection"""
        metaphor_indicators = ['like', 'as if', 'imagine', 'picture', 'seems like']
        return any(indicator in text.lower() for indicator in metaphor_indicators)
    
    def identify_learning_patterns(self, user_message: str, ai_response: str, analysis: Dict) -> List[Dict]:
        """Identify specific patterns that can improve local responses"""
        opportunities = []
        
        # Pattern 1: Emotion + Response Pattern Mapping
        for emotion, keywords in analysis['user_emotion_keywords'].items():
            for pattern_type, patterns in analysis['ai_response_patterns'].items():
                opportunities.append({
                    'type': 'emotion_response_mapping',
                    'emotion': emotion,
                    'response_pattern': pattern_type,
                    'confidence': 0.8,
                    'example_phrases': analysis['key_phrases'][:1]
                })
        
        # Pattern 2: Sentiment Stabilization
        sentiment_shift = analysis['emotional_sentiment']['sentiment_shift']
        if sentiment_shift['emotional_direction'] == 'uplifting':
            opportunities.append({
                'type': 'uplifting_pattern',
                'sentiment_change': sentiment_shift['compound_change'],
                'key_phrases': analysis['key_phrases'],
                'confidence': 0.9
            })
        
        # Pattern 3: Short Response Candidates
        for phrase in analysis['key_phrases']:
            if len(phrase.split()) <= 10:  # Short enough for quick responses
                opportunities.append({
                    'type': 'quick_response_candidate',
                    'phrase': phrase,
                    'applicable_emotions': list(analysis['user_emotion_keywords'].keys()),
                    'confidence': 0.7
                })
        
        return opportunities
    
    def store_learning_data(self, analysis: Dict):
        """Store learning analysis in database for future local processing"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create learning table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS response_learning (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    emotion_keywords TEXT,
                    response_patterns TEXT,
                    sentiment_analysis TEXT,
                    key_phrases TEXT,
                    learning_opportunities TEXT,
                    confidence_score REAL
                )
            ''')
            
            # Calculate overall confidence
            confidence = sum(opp['confidence'] for opp in analysis['learning_opportunities']) / max(1, len(analysis['learning_opportunities']))
            
            # Insert analysis
            cursor.execute('''
                INSERT INTO response_learning 
                (timestamp, emotion_keywords, response_patterns, sentiment_analysis, key_phrases, learning_opportunities, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis['timestamp'],
                json.dumps(analysis['user_emotion_keywords']),
                json.dumps(analysis['ai_response_patterns']),
                json.dumps(analysis['emotional_sentiment']),
                json.dumps(analysis['key_phrases']),
                json.dumps(analysis['learning_opportunities']),
                confidence
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Stored learning data with confidence {confidence:.2f}")
            
        except Exception as e:
            self.logger.error(f"Error storing learning data: {e}")
    
    def get_local_response_suggestions(self, user_message: str) -> List[Dict]:
        """
        Generate local response suggestions based on learned patterns
        Goal: Eventually replace OpenAI calls for common patterns
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract emotions from current message
            current_emotions = self.extract_emotion_keywords(user_message)
            
            suggestions = []
            
            # Find matching learned patterns
            cursor.execute('''
                SELECT key_phrases, learning_opportunities, confidence_score 
                FROM response_learning 
                WHERE confidence_score > 0.7
                ORDER BY confidence_score DESC
                LIMIT 10
            ''')
            
            results = cursor.fetchall()
            
            for key_phrases_json, opportunities_json, confidence in results:
                key_phrases = json.loads(key_phrases_json)
                opportunities = json.loads(opportunities_json)
                
                # Check if any learned patterns match current emotions
                for opportunity in opportunities:
                    if opportunity['type'] == 'emotion_response_mapping':
                        if opportunity['emotion'] in current_emotions:
                            suggestions.append({
                                'response_type': 'learned_pattern',
                                'emotion': opportunity['emotion'],
                                'suggested_phrases': key_phrases[:2],
                                'confidence': confidence,
                                'source': 'learned_from_openai'
                            })
                    elif opportunity['type'] == 'quick_response_candidate':
                        applicable_emotions = opportunity.get('applicable_emotions', [])
                        if any(emotion in current_emotions for emotion in applicable_emotions):
                            suggestions.append({
                                'response_type': 'quick_learned',
                                'phrase': opportunity['phrase'],
                                'confidence': confidence,
                                'source': 'learned_from_openai'
                            })
            
            conn.close()
            
            # Sort by confidence and return top suggestions
            suggestions.sort(key=lambda x: x['confidence'], reverse=True)
            return suggestions[:3]
            
        except Exception as e:
            self.logger.error(f"Error getting local suggestions: {e}")
            return []
    
    def process_conversation_learning(self, user_message: str, ai_response: str) -> Dict:
        """
        Main method to process a conversation and extract learning
        Call this after each OpenAI response to build local intelligence
        """
        self.logger.info("Processing conversation for learning...")
        
        # Analyze the OpenAI response
        analysis = self.analyze_openai_response(user_message, ai_response)
        
        # Store learning data
        self.store_learning_data(analysis)
        
        # Get local suggestions for future similar messages
        local_suggestions = self.get_local_response_suggestions(user_message)
        
        learning_summary = {
            'emotions_detected': list(analysis['user_emotion_keywords'].keys()),
            'patterns_learned': len(analysis['learning_opportunities']),
            'key_phrases_extracted': len(analysis['key_phrases']),
            'local_suggestions_available': len(local_suggestions),
            'confidence_score': sum(opp['confidence'] for opp in analysis['learning_opportunities']) / max(1, len(analysis['learning_opportunities'])),
            'next_local_candidates': local_suggestions
        }
        
        self.logger.info(f"Learning complete: {learning_summary['patterns_learned']} patterns, {learning_summary['local_suggestions_available']} local suggestions")
        
        return learning_summary

# Integration function for use with existing system
def enhance_with_openai_learning(user_message: str, ai_response: str) -> Dict:
    """
    Easy integration function to add learning to existing conversation flow
    """
    learner = OpenAIResponseLearner()
    return learner.process_conversation_learning(user_message, ai_response)

# Usage example:
"""
# After getting OpenAI response:
user_input = "I'm feeling overwhelmed by grief"
openai_response = "I hear the weight of your loss. Grief has its own timeline..."

learning_result = enhance_with_openai_learning(user_input, openai_response)
print(f"Learned {learning_result['patterns_learned']} patterns")
print(f"Local suggestions available: {learning_result['local_suggestions_available']}")
"""