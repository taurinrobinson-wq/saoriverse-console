import json
import re
import os
from typing import Dict, List
import datetime


class LexiconLearner:
    """
    Learns new emotional patterns and language from conversations
    to build a medium language model without using AI
    """
    
    def __init__(self, base_lexicon_path: str = "parser/signal_lexicon.json"):
        self.base_lexicon_path = base_lexicon_path
        self.learned_lexicon_path = "parser/learned_lexicon.json"
        self.pattern_history_path = "learning/pattern_history.json"
        
        self.base_lexicon = self._load_lexicon(base_lexicon_path)
        self.learned_lexicon = self._load_lexicon(self.learned_lexicon_path)
        self.pattern_history = self._load_pattern_history()
        
        # Emotional pattern templates
        self.emotional_patterns = {
            'feeling_expressions': [
                r'i feel (\w+)',
                r'feeling (\w+)',
                r'i\'m (\w+)',
                r'makes me (\w+)',
                r'i\'m experiencing (\w+)'
            ],
            'intensity_modifiers': [
                r'very (\w+)',
                r'extremely (\w+)', 
                r'deeply (\w+)',
                r'slightly (\w+)',
                r'intensely (\w+)'
            ],
            'emotional_metaphors': [
                r'like a (\w+)',
                r'feels like (\w+)',
                r'reminds me of (\w+)',
                r'similar to (\w+)'
            ]
        }
    
    def _load_lexicon(self, path: str) -> Dict[str, str]:
        """Load lexicon from JSON file"""
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {path}: {e}")
        return {}
    
    def _load_pattern_history(self) -> Dict:
        """Load pattern learning history"""
        if os.path.exists(self.pattern_history_path):
            try:
                with open(self.pattern_history_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            'learned_patterns': [],
            'effectiveness_scores': {},
            'pattern_frequencies': {},
            'last_updated': None
        }
    
    def _save_lexicon(self, lexicon: Dict[str, str], path: str):
        """Save lexicon to JSON file"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(lexicon, f, ensure_ascii=False, indent=2)
    
    def _save_pattern_history(self):
        """Save pattern history"""
        os.makedirs(os.path.dirname(self.pattern_history_path), exist_ok=True)
        self.pattern_history['last_updated'] = datetime.datetime.now().isoformat()
        with open(self.pattern_history_path, 'w', encoding='utf-8') as f:
            json.dump(self.pattern_history, f, ensure_ascii=False, indent=2)
    
    def extract_emotional_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extract emotional patterns from text using regex"""
        patterns = {}
        text_lower = text.lower()
        
        for pattern_type, regex_list in self.emotional_patterns.items():
            matches = []
            for regex in regex_list:
                found = re.findall(regex, text_lower)
                matches.extend(found)
            patterns[pattern_type] = list(set(matches))  # Remove duplicates
        
        return patterns
    
    def analyze_word_associations(self, user_input: str, system_response: str) -> Dict:
        """Analyze which words in user input led to effective responses"""
        user_words = set(re.findall(r'\b\w+\b', user_input.lower()))
        
        # Score effectiveness based on response characteristics
        effectiveness_score = self._score_response_effectiveness(system_response)
        
        associations = {}
        for word in user_words:
            if word not in ['i', 'me', 'my', 'am', 'is', 'the', 'a', 'an']:  # Skip common words
                associations[word] = effectiveness_score
        
        return associations
    
    def _score_response_effectiveness(self, response: str) -> float:
        """Score how effective a response seems based on its characteristics"""
        score = 0.5  # Base score
        
        # Longer, more thoughtful responses score higher
        word_count = len(response.split())
        if word_count > 15:
            score += 0.2
        elif word_count > 30:
            score += 0.3
        
        # Responses with questions encourage deeper exploration
        if '?' in response:
            score += 0.2
        
        # Responses that acknowledge feelings
        empathy_words = ['feel', 'understand', 'see', 'hear', 'witness', 'acknowledge']
        if any(word in response.lower() for word in empathy_words):
            score += 0.2
        
        # Responses that offer reflection
        reflection_words = ['seems', 'sounds like', 'appears', 'suggests', 'indicates']
        if any(phrase in response.lower() for phrase in reflection_words):
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def learn_from_conversation(self, conversation_data: Dict) -> Dict:
        """Learn patterns from a complete conversation"""
        learning_results = {
            'new_emotional_words': [],
            'effective_response_patterns': [],
            'word_associations': {},
            'conversation_themes': []
        }
        
        messages = conversation_data.get('messages', [])
        
        # Analyze user-system message pairs
        for i in range(0, len(messages) - 1, 2):
            if i + 1 < len(messages):
                user_msg = messages[i]
                system_msg = messages[i + 1]
                
                if user_msg['type'] == 'user' and system_msg['type'] == 'system':
                    user_text = user_msg['content']
                    system_text = system_msg['content']
                    
                    # Extract emotional patterns
                    patterns = self.extract_emotional_patterns(user_text)
                    for pattern_type, words in patterns.items():
                        learning_results['new_emotional_words'].extend(words)
                    
                    # Analyze word associations
                    associations = self.analyze_word_associations(user_text, system_text)
                    learning_results['word_associations'].update(associations)
                    
                    # Track effective response patterns
                    effectiveness = self._score_response_effectiveness(system_text)
                    if effectiveness > 0.7:  # High effectiveness threshold
                        learning_results['effective_response_patterns'].append({
                            'user_pattern': user_text[:100],
                            'effective_response': system_text[:200],
                            'score': effectiveness
                        })
        
        # Identify conversation themes
        all_user_text = ' '.join([msg['content'] for msg in messages if msg['type'] == 'user'])
        themes = self._identify_themes(all_user_text)
        learning_results['conversation_themes'] = themes
        
        return learning_results
    
    def _identify_themes(self, text: str) -> List[str]:
        """Identify dominant emotional themes in text"""
        theme_keywords = {
            'grief': ['loss', 'death', 'gone', 'miss', 'grief', 'mourn', 'funeral', 'died'],
            'anxiety': ['worry', 'anxious', 'nervous', 'panic', 'stress', 'overwhelm'],
            'joy': ['happy', 'joy', 'celebrate', 'excited', 'wonderful', 'amazing'],
            'love': ['love', 'adore', 'cherish', 'affection', 'care', 'devoted'],
            'longing': ['want', 'need', 'desire', 'wish', 'yearn', 'crave', 'ache'],
            'anger': ['angry', 'mad', 'furious', 'rage', 'irritated', 'frustrated'],
            'confusion': ['confused', 'unclear', 'lost', 'uncertain', 'puzzle', 'wonder']
        }
        
        text_lower = text.lower()
        theme_scores = {}
        
        for theme, keywords in theme_keywords.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            if score > 0:
                theme_scores[theme] = score
        
        # Return themes sorted by frequency
        return [theme for theme, score in sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)]
    
    class ToneMemory:
        def __init__(self):
            self.recent_tones = []

        def update(self, tone: str):
            self.recent_tones.append(tone)
            if len(self.recent_tones) > 3:
                self.recent_tones.pop(0)

        def get_default_tone(self):
            return self.recent_tones[-1] if self.recent_tones else "plain"

        @staticmethod
        def parse_glyph_from_patterns(patterns: Dict[str, List[str]]) -> str:
            if patterns.get('feeling_expressions') or patterns.get('intensity_modifiers'):
                return "emotive"
            elif patterns.get('emotional_metaphors'):
                return "mythic"
            else:
                return "plain"

        @staticmethod
        def scale_emotional_voltage(patterns: Dict[str, List[str]]) -> str:
            count = sum(len(v) for v in patterns.values())
            if count > 5:
                return "high"
            elif count > 2:
                return "medium"
            else:
                return "low"

    def update_lexicon_from_learning(self, learning_results: Dict):
        """Update the learned lexicon based on learning results"""
        # Add new emotional words with appropriate signal mappings
        for word in learning_results.get('new_emotional_words', []):
            if word not in self.base_lexicon and word not in self.learned_lexicon:
                # Map to appropriate signal based on word characteristics
                signal = self._map_word_to_signal(word, learning_results)
                if signal:
                    self.learned_lexicon[word] = signal
        
        # Update pattern frequencies
        for word, effectiveness in learning_results.get('word_associations', {}).items():
            if word in self.pattern_history['pattern_frequencies']:
                # Update existing frequency with weighted average
                old_freq = self.pattern_history['pattern_frequencies'][word]
                self.pattern_history['pattern_frequencies'][word] = (old_freq + effectiveness) / 2
            else:
                self.pattern_history['pattern_frequencies'][word] = effectiveness
        
        # Save updated lexicon and history
        self._save_lexicon(self.learned_lexicon, self.learned_lexicon_path)
        self._save_pattern_history()
    
    def _map_word_to_signal(self, word: str, context: Dict) -> str:
        """Map a new word to an appropriate emotional signal"""
        # Simple heuristic mapping - could be made more sophisticated
        signal_mapping = {
            'negative_emotions': 'θ',  # grief, mourning
            'longing_words': 'γ',      # ache, yearning
            'joy_words': 'λ',          # joy, delight
            'protection_words': 'β',    # boundary, contain
            'recognition_words': 'Ω',   # seen, witnessed
            'devotion_words': 'α',      # vow, sacred
            'insight_words': 'ε'        # clarity, understanding
        }
        
        # Categorize word based on common emotional patterns
        word_lower = word.lower()
        
        if any(pattern in word_lower for pattern in ['sad', 'grief', 'mourn', 'loss', 'hurt']):
            return signal_mapping['negative_emotions']
        elif any(pattern in word_lower for pattern in ['ache', 'long', 'yearn', 'crave']):
            return signal_mapping['longing_words']
        elif any(pattern in word_lower for pattern in ['joy', 'happy', 'delight', 'bliss']):
            return signal_mapping['joy_words']
        elif any(pattern in word_lower for pattern in ['protect', 'guard', 'safe', 'bound']):
            return signal_mapping['protection_words']
        elif any(pattern in word_lower for pattern in ['see', 'hear', 'witness', 'notice']):
            return signal_mapping['recognition_words']
        elif any(pattern in word_lower for pattern in ['sacred', 'devot', 'honor', 'reverent']):
            return signal_mapping['devotion_words']
        elif any(pattern in word_lower for pattern in ['clear', 'understand', 'insight', 'realize']):
            return signal_mapping['insight_words']
        
        # Default to general emotional signal
        return 'ε'
    
    def get_combined_lexicon(self) -> Dict[str, str]:
        """Get the combined base + learned lexicon"""
        combined = self.base_lexicon.copy()
        combined.update(self.learned_lexicon)
        return combined
    
    def get_learning_stats(self) -> Dict:
        """Get statistics about the learning progress"""
        return {
            'base_lexicon_size': len(self.base_lexicon),
            'learned_lexicon_size': len(self.learned_lexicon),
            'total_patterns': len(self.pattern_history.get('pattern_frequencies', {})),
            'last_updated': self.pattern_history.get('last_updated'),
            'top_learned_words': self._get_top_learned_words(5)
        }
    
    def _get_top_learned_words(self, n: int) -> List[tuple]:
        """Get top N learned words by effectiveness"""
        frequencies = self.pattern_history.get('pattern_frequencies', {})
        return sorted(frequencies.items(), key=lambda x: x[1], reverse=True)[:n]


# Usage functions for the UI
def learn_from_conversation_data(conversation_data: Dict) -> Dict:
    """Main function to learn from conversation data"""
    learner = LexiconLearner()
    learning_results = learner.learn_from_conversation(conversation_data)
    learner.update_lexicon_from_learning(learning_results)
    return learning_results

def get_enhanced_lexicon() -> Dict[str, str]:
    """Get the enhanced lexicon that includes learned patterns"""
    learner = LexiconLearner()
    return learner.get_combined_lexicon()

def get_learning_insights() -> Dict:
    """Get insights about what the system has learned"""
    learner = LexiconLearner()
    return learner.get_learning_stats()

from typing import Dict, List

from typing import Dict, List

class LexiconLearner:
    """
    Learns new emotional patterns and language from conversations
    to build a medium language model without using AI
    """
    
    def __init__(self, base_lexicon_path: str = "parser/signal_lexicon.json"):
        self.base_lexicon_path = base_lexicon_path
        self.learned_lexicon_path = "parser/learned_lexicon.json"
        self.pattern_history_path = "learning/pattern_history.json"
        
        self.base_lexicon = self._load_lexicon(base_lexicon_path)
        self.learned_lexicon = self._load_lexicon(self.learned_lexicon_path)
        self.pattern_history = self._load_pattern_history()
        
        # Emotional pattern templates
        self.emotional_patterns = {
            'feeling_expressions': [
                r'i feel (\w+)',
                r'feeling (\w+)',
                r'i\'m (\w+)',
                r'makes me (\w+)',
                r'i\'m experiencing (\w+)'
            ],
            'intensity_modifiers': [
                r'very (\w+)',
                r'extremely (\w+)', 
                r'deeply (\w+)',
                r'slightly (\w+)',
                r'intensely (\w+)'
            ],
            'emotional_metaphors': [
                r'like a (\w+)',
                r'feels like (\w+)',
                r'reminds me of (\w+)',
                r'similar to (\w+)'
            ]
        }
    
    def _load_lexicon(self, path: str) -> Dict[str, str]:
        """Load lexicon from JSON file"""
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {path}: {e}")
        return {}
    
    def _load_pattern_history(self) -> Dict:
        """Load pattern learning history"""
        if os.path.exists(self.pattern_history_path):
            try:
                with open(self.pattern_history_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            'learned_patterns': [],
            'effectiveness_scores': {},
            'pattern_frequencies': {},
            'last_updated': None
        }
    
    def _save_lexicon(self, lexicon: Dict[str, str], path: str):
        """Save lexicon to JSON file"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(lexicon, f, ensure_ascii=False, indent=2)
    
    def _save_pattern_history(self):
        """Save pattern history"""
        os.makedirs(os.path.dirname(self.pattern_history_path), exist_ok=True)
        self.pattern_history['last_updated'] = datetime.datetime.now().isoformat()
        with open(self.pattern_history_path, 'w', encoding='utf-8') as f:
            json.dump(self.pattern_history, f, ensure_ascii=False, indent=2)
    
    def extract_emotional_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extract emotional patterns from text using regex"""
        patterns = {}
        text_lower = text.lower()
        
        for pattern_type, regex_list in self.emotional_patterns.items():
            matches = []
            for regex in regex_list:
                found = re.findall(regex, text_lower)
                matches.extend(found)
            patterns[pattern_type] = list(set(matches))  # Remove duplicates
        
        return patterns
    
    def analyze_word_associations(self, user_input: str, system_response: str) -> Dict:
        """Analyze which words in user input led to effective responses"""
        user_words = set(re.findall(r'\b\w+\b', user_input.lower()))
        
        # Score effectiveness based on response characteristics
        effectiveness_score = self._score_response_effectiveness(system_response)
        
        associations = {}
        for word in user_words:
            if word not in ['i', 'me', 'my', 'am', 'is', 'the', 'a', 'an']:  # Skip common words
                associations[word] = effectiveness_score
        
        return associations
    
    def _score_response_effectiveness(self, response: str) -> float:
        """Score how effective a response seems based on its characteristics"""
        score = 0.5  # Base score
        
        # Longer, more thoughtful responses score higher
        word_count = len(response.split())
        if word_count > 15:
            score += 0.2
        elif word_count > 30:
            score += 0.3
        
        # Responses with questions encourage deeper exploration
        if '?' in response:
            score += 0.2
        
        # Responses that acknowledge feelings
        empathy_words = ['feel', 'understand', 'see', 'hear', 'witness', 'acknowledge']
        if any(word in response.lower() for word in empathy_words):
            score += 0.2
        
        # Responses that offer reflection
        reflection_words = ['seems', 'sounds like', 'appears', 'suggests', 'indicates']
        if any(phrase in response.lower() for phrase in reflection_words):
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def learn_from_conversation(self, conversation_data: Dict) -> Dict:
        """Learn patterns from a complete conversation"""
        learning_results = {
            'new_emotional_words': [],
            'effective_response_patterns': [],
            'word_associations': {},
            'conversation_themes': []
        }
        
        messages = conversation_data.get('messages', [])
        
        # Analyze user-system message pairs
        for i in range(0, len(messages) - 1, 2):
            if i + 1 < len(messages):
                user_msg = messages[i]
                system_msg = messages[i + 1]
                
                if user_msg['type'] == 'user' and system_msg['type'] == 'system':
                    user_text = user_msg['content']
                    system_text = system_msg['content']
                    
                    # Extract emotional patterns
                    patterns = self.extract_emotional_patterns(user_text)
                    for pattern_type, words in patterns.items():
                        learning_results['new_emotional_words'].extend(words)
                    
                    # Analyze word associations
                    associations = self.analyze_word_associations(user_text, system_text)
                    learning_results['word_associations'].update(associations)
                    
                    # Track effective response patterns
                    effectiveness = self._score_response_effectiveness(system_text)
                    if effectiveness > 0.7:  # High effectiveness threshold
                        learning_results['effective_response_patterns'].append({
                            'user_pattern': user_text[:100],
                            'effective_response': system_text[:200],
                            'score': effectiveness
                        })
        
        # Identify conversation themes
        all_user_text = ' '.join([msg['content'] for msg in messages if msg['type'] == 'user'])
        themes = self._identify_themes(all_user_text)
        learning_results['conversation_themes'] = themes
        
        return learning_results
    
    def _identify_themes(self, text: str) -> List[str]:
        """Identify dominant emotional themes in text"""
        theme_keywords = {
            'grief': ['loss', 'death', 'gone', 'miss', 'grief', 'mourn', 'funeral', 'died'],
            'anxiety': ['worry', 'anxious', 'nervous', 'panic', 'stress', 'overwhelm'],
            'joy': ['happy', 'joy', 'celebrate', 'excited', 'wonderful', 'amazing'],
            'love': ['love', 'adore', 'cherish', 'affection', 'care', 'devoted'],
            'longing': ['want', 'need', 'desire', 'wish', 'yearn', 'crave', 'ache'],
            'anger': ['angry', 'mad', 'furious', 'rage', 'irritated', 'frustrated'],
            'confusion': ['confused', 'unclear', 'lost', 'uncertain', 'puzzle', 'wonder']
        }
        
        text_lower = text.lower()
        theme_scores = {}
        
        for theme, keywords in theme_keywords.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            if score > 0:
                theme_scores[theme] = score
        
        # Return themes sorted by frequency
        return [theme for theme, score in sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)]
    
    class ToneMemory:
        def __init__(self):
            self.recent_tones = []

        def update(self, tone: str):
            self.recent_tones.append(tone)
            if len(self.recent_tones) > 3:
                self.recent_tones.pop(0)

        def get_default_tone(self):
            return self.recent_tones[-1] if self.recent_tones else "plain"

        @staticmethod
        def parse_glyph_from_patterns(patterns: Dict[str, List[str]]) -> str:
            if patterns.get('feeling_expressions') or patterns.get('intensity_modifiers'):
                return "emotive"
            elif patterns.get('emotional_metaphors'):
                return "mythic"
            else:
                return "plain"

        @staticmethod
        def scale_emotional_voltage(patterns: Dict[str, List[str]]) -> str:
            count = sum(len(v) for v in patterns.values())
            if count > 5:
                return "high"
            elif count > 2:
                return "medium"
            else:
                return "low"

    def update_lexicon_from_learning(self, learning_results: Dict):
        """Update the learned lexicon based on learning results"""
        # Add new emotional words with appropriate signal mappings
        for word in learning_results.get('new_emotional_words', []):
            if word not in self.base_lexicon and word not in self.learned_lexicon:
                # Map to appropriate signal based on word characteristics
                signal = self._map_word_to_signal(word, learning_results)
                if signal:
                    self.learned_lexicon[word] = signal
        
        # Update pattern frequencies
        for word, effectiveness in learning_results.get('word_associations', {}).items():
            if word in self.pattern_history['pattern_frequencies']:
                # Update existing frequency with weighted average
                old_freq = self.pattern_history['pattern_frequencies'][word]
                self.pattern_history['pattern_frequencies'][word] = (old_freq + effectiveness) / 2
            else:
                self.pattern_history['pattern_frequencies'][word] = effectiveness
        
        # Save updated lexicon and history
        self._save_lexicon(self.learned_lexicon, self.learned_lexicon_path)
        self._save_pattern_history()
    
    def _map_word_to_signal(self, word: str, context: Dict) -> str:
        """Map a new word to an appropriate emotional signal"""
        # Simple heuristic mapping - could be made more sophisticated
        signal_mapping = {
            'negative_emotions': 'θ',  # grief, mourning
            'longing_words': 'γ',      # ache, yearning
            'joy_words': 'λ',          # joy, delight
            'protection_words': 'β',    # boundary, contain
            'recognition_words': 'Ω',   # seen, witnessed
            'devotion_words': 'α',      # vow, sacred
            'insight_words': 'ε'        # clarity, understanding
        }
        
        # Categorize word based on common emotional patterns
        word_lower = word.lower()
        
        if any(pattern in word_lower for pattern in ['sad', 'grief', 'mourn', 'loss', 'hurt']):
            return signal_mapping['negative_emotions']
        elif any(pattern in word_lower for pattern in ['ache', 'long', 'yearn', 'crave']):
            return signal_mapping['longing_words']
        elif any(pattern in word_lower for pattern in ['joy', 'happy', 'delight', 'bliss']):
            return signal_mapping['joy_words']
        elif any(pattern in word_lower for pattern in ['protect', 'guard', 'safe', 'bound']):
            return signal_mapping['protection_words']
        elif any(pattern in word_lower for pattern in ['see', 'hear', 'witness', 'notice']):
            return signal_mapping['recognition_words']
        elif any(pattern in word_lower for pattern in ['sacred', 'devot', 'honor', 'reverent']):
            return signal_mapping['devotion_words']
        elif any(pattern in word_lower for pattern in ['clear', 'understand', 'insight', 'realize']):
            return signal_mapping['insight_words']
        
        # Default to general emotional signal
        return 'ε'
    
    def get_combined_lexicon(self) -> Dict[str, str]:
        """Get the combined base + learned lexicon"""
        combined = self.base_lexicon.copy()
        combined.update(self.learned_lexicon)
        return combined
    
    def get_learning_stats(self) -> Dict:
        """Get statistics about the learning progress"""
        return {
            'base_lexicon_size': len(self.base_lexicon),
            'learned_lexicon_size': len(self.learned_lexicon),
            'total_patterns': len(self.pattern_history.get('pattern_frequencies', {})),
            'last_updated': self.pattern_history.get('last_updated'),
            'top_learned_words': self._get_top_learned_words(5)
        }
    
    def _get_top_learned_words(self, n: int) -> List[tuple]:
        """Get top N learned words by effectiveness"""
        frequencies = self.pattern_history.get('pattern_frequencies', {})
        return sorted(frequencies.items(), key=lambda x: x[1], reverse=True)[:n]

# Usage functions for the UI
def learn_from_conversation_data(conversation_data: Dict) -> Dict:
    """Main function to learn from conversation data"""
    learner = LexiconLearner()
    learning_results = learner.learn_from_conversation(conversation_data)
    learner.update_lexicon_from_learning(learning_results)
    return learning_results

def get_enhanced_lexicon() -> Dict[str, str]:
    """Get the enhanced lexicon that includes learned patterns"""
    learner = LexiconLearner()
    return learner.get_combined_lexicon()

def get_learning_insights() -> Dict:
    """Get insights about what the system has learned"""
    learner = LexiconLearner()
    return learner.get_learning_stats()