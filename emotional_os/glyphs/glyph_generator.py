#!/usr/bin/env python3
"""
Auto-evolving Glyph Generator for Saoriverse Console
Continuously creates new glyphs and emotional tags to make the system more nuanced and human-like
"""

import json
import logging
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

import requests


@dataclass
class EmotionalPattern:
    """Represents a detected emotional pattern that might need a new glyph"""
    emotions: List[str]
    intensity: float
    context_words: List[str]
    frequency: int
    first_seen: datetime
    last_seen: datetime

@dataclass
class NewGlyph:
    """Represents a newly generated glyph"""
    glyph_symbol: str
    tag_name: str
    core_emotion: str
    response_cue: str
    domain: str
    response_type: str
    narrative_hook: str
    tone_profile: str
    cadence: str
    depth_level: str
    style_variant: str
    humor_style: str

class GlyphGenerator:
    """
    Generates new glyphs by analyzing emotional patterns in conversations
    and automatically adds them to the emotional_tags system
    """

    def __init__(self,
                 supabase_url: Optional[str] = None,
                 supabase_key: Optional[str] = None,
                 min_pattern_frequency: int = 3,
                 novelty_threshold: float = 0.7):

        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.min_pattern_frequency = min_pattern_frequency
        self.novelty_threshold = novelty_threshold

        # Setup logging first
        self.setup_logging()

        # Load existing emotional tags to avoid duplication
        self.existing_tags = self._load_existing_tags()
        self.detected_patterns = self._load_pattern_cache()

        # Base glyph symbols for combinations
        self.base_symbols = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'θ', 'λ', 'Ω']
        self.combination_operators = ['×', '⊕', '∧', '∨', '⟡']

        # Emotional domain mappings
        self.emotion_domains = {
            'joy': 'Joy & Levity',
            'delight': 'Joy & Levity',
            'happiness': 'Joy & Levity',
            'grief': 'Grief & Rupture',
            'loss': 'Grief & Rupture',
            'sadness': 'Grief & Rupture',
            'anger': 'Conflict & Power',
            'rage': 'Conflict & Power',
            'boundary': 'Conflict & Power',
            'longing': 'Longing & Threshold',
            'desire': 'Longing & Threshold',
            'ache': 'Longing & Threshold',
            'confusion': 'Confusion & Clarity',
            'clarity': 'Clarity & Grounding',
            'understanding': 'Clarity & Grounding',
            'stillness': 'Stillness & Peace',
            'calm': 'Stillness & Peace',
            'peace': 'Stillness & Peace',
            'connection': 'Connection & Grounding',
            'intimacy': 'Longing & Threshold',
            'vulnerability': 'Longing & Threshold',
            'devotion': 'Devotion & Containment',
            'sacred': 'Devotion & Containment'
        }

        # Response type mappings
        self.response_types = {
            'high_energy': 'Disrupt',
            'supportive': 'Soothe',
            'reflective': 'Witness',
            'instructive': 'Guide',
            'protective': 'Contain',
            'liberating': 'Release',
            'welcoming': 'Welcome',
            'connecting': 'Companion'
        }

    def setup_logging(self):
        """Setup logging for glyph generation tracking"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Only add handlers if they don't already exist
        if not self.logger.handlers:
            # Add console handler (always available)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            # Try to add file handler, but don't fail if we can't
            try:
                file_handler = logging.FileHandler('glyph_generation.log')
                file_handler.setLevel(logging.INFO)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except Exception:
                # If we can't create the file handler, just use console
                pass

    def _load_existing_tags(self) -> Dict[str, Dict]:
        """Load existing emotional tags from the system"""
        try:
            # Try to load from emotional_tags_rows.sql or a JSON cache
            existing_tags = {}

            # Parse the SQL file if it exists
            sql_path = "emotional_tags_rows.sql"
            if os.path.exists(sql_path):
                with open(sql_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract tag names and glyphs from SQL INSERT statements
                    pattern = r"'([^']+)',\s*'([^']+)',\s*'([^']+)',\s*'([^']+)',\s*'([^']+)'"
                    matches = re.findall(pattern, content)

                    for match in matches:
                        if len(match) >= 5:
                            tag_id, tag_name, core_emotion, response_cue, glyph = match[:5]
                            existing_tags[tag_name.lower()] = {
                                'id': tag_id,
                                'tag_name': tag_name,
                                'core_emotion': core_emotion,
                                'glyph': glyph,
                                'response_cue': response_cue
                            }

            self.logger.info(f"Loaded {len(existing_tags)} existing emotional tags")
            return existing_tags

        except Exception as e:
            self.logger.error(f"Error loading existing tags: {e}")
            return {}

    def _load_pattern_cache(self) -> Dict[str, EmotionalPattern]:
        """Load cached emotional patterns"""
        cache_path = "learning/detected_patterns.json"
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                    patterns = {}
                    for key, value in data.items():
                        patterns[key] = EmotionalPattern(
                            emotions=value['emotions'],
                            intensity=value['intensity'],
                            context_words=value['context_words'],
                            frequency=value['frequency'],
                            first_seen=datetime.fromisoformat(value['first_seen']),
                            last_seen=datetime.fromisoformat(value['last_seen'])
                        )
                    return patterns
            except Exception as e:
                self.logger.error(f"Error loading pattern cache: {e}")
        return {}

    def _save_pattern_cache(self):
        """Save detected patterns to cache"""
        try:
            cache_path = "learning/detected_patterns.json"
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)

            data = {}
            for key, pattern in self.detected_patterns.items():
                data[key] = {
                    'emotions': pattern.emotions,
                    'intensity': pattern.intensity,
                    'context_words': pattern.context_words,
                    'frequency': pattern.frequency,
                    'first_seen': pattern.first_seen.isoformat(),
                    'last_seen': pattern.last_seen.isoformat()
                }

            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            # In Streamlit or restricted environments, file writing might fail
            # Just log the error and continue
            if hasattr(self, 'logger'):
                self.logger.error(f"Error saving pattern cache: {e}")
            else:
                print(f"Error saving pattern cache: {e}")

    def detect_new_emotional_patterns(self, conversation_text: str, context: Optional[Dict] = None) -> List[EmotionalPattern]:
        """
        Analyze conversation text to detect new emotional patterns
        that might need new glyphs
        """
        new_patterns = []
        text_lower = conversation_text.lower()

        # Extract emotional expressions
        emotion_expressions = self._extract_emotion_expressions(text_lower)

        # Extract emotional combinations (complex feelings)
        emotion_combinations = self._extract_emotion_combinations(text_lower)

        # Extract contextual modifiers
        context_words = self._extract_context_words(text_lower)

        # Calculate emotional intensity
        intensity = self._calculate_emotional_intensity(text_lower)

        # Generate pattern keys for tracking
        for combo in emotion_combinations:
            if len(combo) >= 2:  # Only interested in complex emotional states
                pattern_key = " + ".join(sorted(combo))

                # Check if this is a novel pattern
                if self._is_novel_pattern(combo):
                    now = datetime.now(timezone.utc)

                    if pattern_key in self.detected_patterns:
                        # Update existing pattern
                        pattern = self.detected_patterns[pattern_key]
                        pattern.frequency += 1
                        pattern.last_seen = now
                        pattern.context_words.extend(context_words)
                        pattern.context_words = list(set(pattern.context_words))  # Remove duplicates
                    else:
                        # Create new pattern
                        pattern = EmotionalPattern(
                            emotions=combo,
                            intensity=intensity,
                            context_words=context_words,
                            frequency=1,
                            first_seen=now,
                            last_seen=now
                        )
                        self.detected_patterns[pattern_key] = pattern

                    new_patterns.append(pattern)

        # Save updated patterns
        self._save_pattern_cache()

        return new_patterns

    def _extract_emotion_expressions(self, text: str) -> List[str]:
        """Extract explicit emotion words and expressions"""
        emotion_patterns = [
            r'i feel (\w+)',
            r'feeling (\w+)',
            r'i\'?m (\w+)',
            r'makes me (\w+)',
            r'i\'?m experiencing (\w+)',
            r'sense of (\w+)',
            r'overwhelmed by (\w+)',
            r'filled with (\w+)',
            r'struck by (\w+)',
            r'consumed by (\w+)'
        ]

        emotions = []
        for pattern in emotion_patterns:
            matches = re.findall(pattern, text)
            emotions.extend(matches)

        # Also look for standalone emotion words
        emotion_words = [
            'joy', 'sorrow', 'grief', 'bliss', 'ache', 'longing', 'desire',
            'confusion', 'clarity', 'peace', 'chaos', 'stillness', 'motion',
            'connection', 'separation', 'vulnerability', 'strength', 'weakness',
            'devotion', 'detachment', 'expansion', 'contraction', 'flow', 'resistance'
        ]

        for word in emotion_words:
            if word in text:
                emotions.append(word)

        return list(set(emotions))  # Remove duplicates

    def _extract_emotion_combinations(self, text: str) -> List[List[str]]:
        """Extract complex emotional combinations from text"""
        emotions = self._extract_emotion_expressions(text)

        # Look for combination indicators
        combination_indicators = [
            'and', 'but', 'while', 'with', 'mixed with', 'alongside',
            'combined with', 'tinged with', 'flavored by', 'touched by'
        ]

        combinations = []

        # If we have multiple emotions in close proximity, consider them a combination
        if len(emotions) >= 2:
            combinations.append(emotions)

        # Look for specific combination phrases
        combo_patterns = [
            r'(\w+) and (\w+)',
            r'(\w+) but (\w+)',
            r'(\w+) with (\w+)',
            r'(\w+) mixed with (\w+)',
            r'(\w+) tinged with (\w+)'
        ]

        for pattern in combo_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if all(word in self._get_all_emotion_words() for word in match):
                    combinations.append(list(match))

        return combinations

    def _extract_context_words(self, text: str) -> List[str]:
        """Extract contextual words that might influence glyph generation"""
        context_categories = {
            'intensity': ['deeply', 'intensely', 'slightly', 'overwhelmingly', 'gently', 'powerfully'],
            'quality': ['sacred', 'raw', 'pure', 'complex', 'simple', 'nuanced', 'profound'],
            'movement': ['flowing', 'rushing', 'creeping', 'exploding', 'settling', 'spiraling'],
            'container': ['held', 'contained', 'overflowing', 'constrained', 'liberated', 'trapped']
        }

        context_words = []
        for category, words in context_categories.items():
            for word in words:
                if word in text:
                    context_words.append(word)

        return context_words

    def _calculate_emotional_intensity(self, text: str) -> float:
        """Calculate the emotional intensity of the text"""
        intensity_indicators = {
            'low': ['slightly', 'gently', 'softly', 'mildly', 'barely'],
            'medium': ['moderately', 'reasonably', 'fairly', 'quite'],
            'high': ['deeply', 'intensely', 'powerfully', 'overwhelmingly', 'completely'],
            'extreme': ['utterly', 'absolutely', 'totally', 'entirely', 'devastatingly']
        }

        intensity_scores = {'low': 0.25, 'medium': 0.5, 'high': 0.75, 'extreme': 1.0}

        max_intensity = 0.0
        for level, words in intensity_indicators.items():
            for word in words:
                if word in text:
                    max_intensity = max(max_intensity, intensity_scores[level])

        # Default to medium intensity if no indicators found
        return max_intensity if max_intensity > 0 else 0.5

    def _is_novel_pattern(self, emotion_combo: List[str]) -> bool:
        """Check if this emotional combination represents a novel pattern"""
        combo_key = " + ".join(sorted(emotion_combo))

        # Check against existing tags
        for tag_name, tag_data in self.existing_tags.items():
            if any(emotion.lower() in tag_name.lower() or
                   emotion.lower() in tag_data.get('core_emotion', '').lower()
                   for emotion in emotion_combo):
                # Similar pattern already exists
                return False

        # Check novelty threshold
        return True

    def _get_all_emotion_words(self) -> Set[str]:
        """Get all known emotion words"""
        return set([
            'joy', 'sorrow', 'grief', 'bliss', 'ache', 'longing', 'desire',
            'confusion', 'clarity', 'peace', 'chaos', 'stillness', 'motion',
            'connection', 'separation', 'vulnerability', 'strength', 'weakness',
            'devotion', 'detachment', 'expansion', 'contraction', 'flow', 'resistance',
            'delight', 'loss', 'anger', 'boundary', 'understanding', 'calm',
            'intimacy', 'sacred', 'love', 'fear', 'hope', 'despair', 'wonder',
            'awe', 'contempt', 'disgust', 'surprise', 'anticipation', 'trust'
        ])

    def generate_new_glyph(self, pattern: EmotionalPattern) -> Optional[NewGlyph]:
        """Generate a new glyph based on an emotional pattern"""
        try:
            # Generate glyph symbol
            glyph_symbol = self._generate_glyph_symbol(pattern)

            # Generate tag name
            tag_name = self._generate_tag_name(pattern)

            # Determine core emotion
            core_emotion = self._determine_core_emotion(pattern)

            # Generate response cue
            response_cue = self._generate_response_cue(pattern)

            # Determine domain
            domain = self._determine_domain(pattern)

            # Determine response type
            response_type = self._determine_response_type(pattern)

            # Generate narrative hook
            narrative_hook = f"Triggers Saori's {tag_name.lower().replace(' ', '_')} ritual"

            # Determine tone and style attributes
            tone_profile, cadence, depth_level, style_variant, humor_style = self._determine_style_attributes(pattern)

            return NewGlyph(
                glyph_symbol=glyph_symbol,
                tag_name=tag_name,
                core_emotion=core_emotion,
                response_cue=response_cue,
                domain=domain,
                response_type=response_type,
                narrative_hook=narrative_hook,
                tone_profile=tone_profile,
                cadence=cadence,
                depth_level=depth_level,
                style_variant=style_variant,
                humor_style=humor_style
            )

        except Exception as e:
            self.logger.error(f"Error generating new glyph: {e}")
            return None

    def _generate_glyph_symbol(self, pattern: EmotionalPattern) -> str:
        """Generate a unique glyph symbol for the pattern"""
        # Use emotion combinations to create symbol combinations
        if len(pattern.emotions) >= 2:
            # Map emotions to base symbols
            emotion_symbol_map = {
                'joy': 'λ', 'delight': 'λ', 'happiness': 'λ',
                'grief': 'θ', 'loss': 'θ', 'sadness': 'θ',
                'ache': 'γ', 'longing': 'γ', 'desire': 'γ',
                'clarity': 'ε', 'understanding': 'ε', 'insight': 'ε',
                'stillness': 'δ', 'peace': 'δ', 'calm': 'δ',
                'connection': 'α', 'intimacy': 'α', 'love': 'α',
                'boundary': 'β', 'structure': 'β', 'containment': 'β',
                'expansion': 'ζ', 'growth': 'ζ', 'motion': 'ζ',
                'recognition': 'Ω', 'witness': 'Ω', 'mirror': 'Ω'
            }

            # Get symbols for the emotions
            symbols = []
            for emotion in pattern.emotions[:2]:  # Use first two emotions
                symbol = emotion_symbol_map.get(emotion.lower(), 'α')
                symbols.append(symbol)

            # Combine with operator based on context
            if 'with' in pattern.context_words or 'and' in pattern.context_words:
                operator = '×'
            elif 'but' in pattern.context_words:
                operator = '⊕'
            else:
                operator = '×'

            return f"{symbols[0]} {operator} {symbols[1]}"

        # Single emotion - use base symbol
        emotion = pattern.emotions[0] if pattern.emotions else 'connection'
        emotion_symbol_map = {
            'joy': 'λ', 'delight': 'λ', 'happiness': 'λ',
            'grief': 'θ', 'loss': 'θ', 'sadness': 'θ',
            'ache': 'γ', 'longing': 'γ', 'desire': 'γ',
            'clarity': 'ε', 'understanding': 'ε', 'insight': 'ε',
            'stillness': 'δ', 'peace': 'δ', 'calm': 'δ',
            'connection': 'α', 'intimacy': 'α', 'love': 'α',
            'boundary': 'β', 'structure': 'β', 'containment': 'β',
            'expansion': 'ζ', 'growth': 'ζ', 'motion': 'ζ',
            'recognition': 'Ω', 'witness': 'Ω', 'mirror': 'Ω'
        }
        return emotion_symbol_map.get(emotion.lower(), 'α')

    def _generate_tag_name(self, pattern: EmotionalPattern) -> str:
        """Generate a descriptive tag name"""
        # Combine emotion words with context modifiers
        base_emotions = pattern.emotions[:2] if len(pattern.emotions) >= 2 else pattern.emotions

        # Add contextual modifiers
        modifiers = [word for word in pattern.context_words if word in [
            'sacred', 'spiral', 'contained', 'expansive', 'quiet', 'deep',
            'gentle', 'intense', 'flowing', 'still', 'raw', 'pure'
        ]]

        if modifiers and base_emotions:
            return f"{modifiers[0].title()} {base_emotions[0].title()}"
        if len(base_emotions) >= 2:
            return f"{base_emotions[0].title()} {base_emotions[1].title()}"
        if base_emotions:
            return f"Emergent {base_emotions[0].title()}"
        return "Unnamed Pattern"

    def _determine_core_emotion(self, pattern: EmotionalPattern) -> str:
        """Determine the core emotion category"""
        emotion_categories = {
            'Delight': ['joy', 'happiness', 'bliss', 'delight'],
            'Loss': ['grief', 'sorrow', 'loss', 'sadness'],
            'Ache': ['longing', 'desire', 'ache', 'yearning'],
            'Clarity': ['understanding', 'clarity', 'insight', 'recognition'],
            'Stillness': ['peace', 'calm', 'stillness', 'quiet'],
            'Connection': ['love', 'intimacy', 'connection', 'unity'],
            'Boundary': ['anger', 'boundary', 'protection', 'strength'],
            'Separation': ['detachment', 'distance', 'independence'],
            'Confusion': ['uncertainty', 'confusion', 'chaos', 'disorder']
        }

        for category, words in emotion_categories.items():
            if any(emotion.lower() in words for emotion in pattern.emotions):
                return category

        return 'Clarity'  # Default

    def _generate_response_cue(self, pattern: EmotionalPattern) -> str:
        """Generate a response cue based on the pattern"""
        templates = {
            'joy': [
                "Celebrate the emergence of light.",
                "Honor the bloom within stillness.",
                "Witness joy without grasping."
            ],
            'grief': [
                "Hold space for the sacred wound.",
                "Contain sorrow without fixing.",
                "Mirror loss with presence."
            ],
            'ache': [
                "Witness longing without judgment.",
                "Hold desire as sacred fire.",
                "Mirror the depth of yearning."
            ],
            'clarity': [
                "Reflect truth without distortion.",
                "Guide toward deeper seeing.",
                "Mirror insight with precision."
            ],
            'stillness': [
                "Rest in the sanctuary of quiet.",
                "Honor the sacred pause.",
                "Witness peace without disturbing."
            ]
        }

        # Find matching template
        primary_emotion = pattern.emotions[0].lower() if pattern.emotions else 'clarity'

        for emotion_type, cues in templates.items():
            if primary_emotion in emotion_type or emotion_type in primary_emotion:
                return cues[pattern.frequency % len(cues)]

        return f"Hold space for {primary_emotion} with presence."

    def _determine_domain(self, pattern: EmotionalPattern) -> str:
        """Determine the emotional domain"""
        if not pattern.emotions:
            return 'Recognition & Mirror'

        primary_emotion = pattern.emotions[0].lower()
        return self.emotion_domains.get(primary_emotion, 'Recognition & Mirror')

    def _determine_response_type(self, pattern: EmotionalPattern) -> str:
        """Determine the response type based on pattern characteristics"""
        if pattern.intensity > 0.8:
            return 'Contain'
        if pattern.intensity > 0.6:
            return 'Witness'
        if pattern.intensity > 0.4:
            return 'Guide'
        return 'Soothe'

    def _determine_style_attributes(self, pattern: EmotionalPattern) -> Tuple[str, str, str, str, str]:
        """Determine tone profile, cadence, depth level, style variant, and humor style"""
        # Tone profile based on emotions
        if any(emotion in ['grief', 'loss', 'sorrow'] for emotion in pattern.emotions):
            tone_profile = 'tender and slow'
        elif any(emotion in ['joy', 'delight', 'happiness'] for emotion in pattern.emotions):
            tone_profile = 'bright and playful'
        elif any(emotion in ['clarity', 'understanding'] for emotion in pattern.emotions):
            tone_profile = 'precise and slow'
        else:
            tone_profile = 'gentle and affirming'

        # Cadence based on intensity
        if pattern.intensity > 0.7:
            cadence = 'poetic and elliptical'
        elif pattern.intensity > 0.4:
            cadence = 'measured and clear'
        else:
            cadence = 'short and steady'

        # Depth level based on complexity
        if len(pattern.emotions) > 1 or pattern.intensity > 0.6:
            depth_level = 'emotional excavation'
        else:
            depth_level = 'surface reflection'

        # Style variant based on emotion type
        if any(emotion in ['grief', 'loss', 'ache'] for emotion in pattern.emotions):
            style_variant = 'oracle'
        elif any(emotion in ['clarity', 'understanding'] for emotion in pattern.emotions):
            style_variant = 'mentor'
        elif any(emotion in ['joy', 'delight'] for emotion in pattern.emotions):
            style_variant = 'friend'
        else:
            style_variant = 'companion'

        # Humor style
        if any(emotion in ['joy', 'delight'] for emotion in pattern.emotions):
            humor_style = 'playful pun'
        elif 'boundary' in pattern.emotions or 'anger' in pattern.emotions:
            humor_style = 'dry wit'
        else:
            humor_style = 'none'

        return tone_profile, cadence, depth_level, style_variant, humor_style

    def should_create_glyph(self, pattern: EmotionalPattern) -> bool:
        """Determine if a pattern should generate a new glyph"""
        return (pattern.frequency >= self.min_pattern_frequency and
                self._is_novel_pattern(pattern.emotions))

    def create_emotional_tag_entry(self, glyph: NewGlyph) -> Dict:
        """Create a new emotional tag entry for insertion into the database"""
        tag_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        return {
            'id': tag_id,
            'tag_name': glyph.tag_name,
            'core_emotion': glyph.core_emotion,
            'response_cue': glyph.response_cue,
            'glyph': glyph.glyph_symbol,
            'domain': glyph.domain,
            'response_type': glyph.response_type,
            'narrative_hook': glyph.narrative_hook,
            'created_at': created_at,
            'tone_profile': glyph.tone_profile,
            'cadence': glyph.cadence,
            'depth_level': glyph.depth_level,
            'style_variant': glyph.style_variant,
            'humor_style': glyph.humor_style
        }

    def insert_new_glyph_to_supabase(self, emotional_tag: Dict) -> bool:
        """Insert new emotional tag into Supabase"""
        if not self.supabase_url or not self.supabase_key:
            self.logger.warning("Supabase credentials not provided, skipping database insertion")
            return False

        try:
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }

            url = f"{self.supabase_url}/rest/v1/emotional_tags"

            response = requests.post(url, json=emotional_tag, headers=headers)
            response.raise_for_status()

            self.logger.info(f"Successfully inserted new glyph: {emotional_tag['tag_name']}")
            return True

        except Exception as e:
            self.logger.error(f"Error inserting glyph to Supabase: {e}")
            return False

    def save_glyph_to_sql_file(self, emotional_tag: Dict):
        """Save new glyph as SQL INSERT statement for backup"""
        try:
            sql_statement = f"""INSERT INTO "public"."emotional_tags" ("id", "tag_name", "core_emotion", "response_cue", "glyph", "domain", "response_type", "narrative_hook", "created_at", "tone_profile", "cadence", "depth_level", "style_variant", "humor_style") VALUES ('{emotional_tag['id']}', '{emotional_tag['tag_name']}', '{emotional_tag['core_emotion']}', '{emotional_tag['response_cue']}', '{emotional_tag['glyph']}', '{emotional_tag['domain']}', '{emotional_tag['response_type']}', '{emotional_tag['narrative_hook']}', '{emotional_tag['created_at']}', '{emotional_tag['tone_profile']}', '{emotional_tag['cadence']}', '{emotional_tag['depth_level']}', '{emotional_tag['style_variant']}', '{emotional_tag['humor_style']}');"""

            # Append to generated glyphs file
            os.makedirs('generated', exist_ok=True)
            with open('generated/new_glyphs.sql', 'a') as f:
                f.write(sql_statement + '\n')
        except Exception as e:
            # In Streamlit or restricted environments, file writing might fail
            # Just log the error and continue
            if hasattr(self, 'logger'):
                self.logger.warning(f"Could not save glyph to SQL file: {e}")
            else:
                print(f"Could not save glyph to SQL file: {e}")

    def process_conversation_for_glyphs(self, conversation_text: str, context: Optional[Dict] = None) -> List[Dict]:
        """
        Main method to process a conversation and generate new glyphs if needed
        Returns list of newly created emotional tags
        """
        new_glyphs = []

        try:
            # Detect new emotional patterns
            patterns = self.detect_new_emotional_patterns(conversation_text, context)

            # Process patterns that meet criteria for glyph generation
            for pattern in patterns:
                if self.should_create_glyph(pattern):
                    # Generate new glyph
                    new_glyph = self.generate_new_glyph(pattern)
                    if new_glyph:
                        # Create emotional tag entry
                        emotional_tag = self.create_emotional_tag_entry(new_glyph)

                        # Save to database
                        if self.insert_new_glyph_to_supabase(emotional_tag):
                            new_glyphs.append(emotional_tag)
                            self.logger.info(f"Created new glyph: {new_glyph.tag_name} ({new_glyph.glyph_symbol})")

                        # Save to SQL file as backup
                        self.save_glyph_to_sql_file(emotional_tag)

                        # Update existing tags cache to avoid duplicates
                        self.existing_tags[new_glyph.tag_name.lower()] = emotional_tag

            return new_glyphs

        except Exception as e:
            self.logger.error(f"Error processing conversation for glyphs: {e}")
            return []

# Example usage and testing
if __name__ == "__main__":
    # Initialize the glyph generator
    generator = GlyphGenerator(
        min_pattern_frequency=2,  # Lower threshold for testing
        novelty_threshold=0.5
    )

    # Test with sample conversations
    test_conversations = [
        "I'm feeling a deep joy mixed with profound sadness, like witnessing something sacred ending and beginning at the same time.",
        "There's this gentle ache that flows through me when I think about connection - not painful, but yearning and peaceful together.",
        "I experience this intense clarity that comes with overwhelming confusion, like seeing truth through a fractured lens.",
        "Sometimes I feel contained stillness - not trapped, but held in a sacred quiet that pulses with life."
    ]

    print("Testing Glyph Generation...")
    for i, conversation in enumerate(test_conversations):
        print(f"\n--- Processing conversation {i+1} ---")
        print(f"Text: {conversation}")

        new_glyphs = generator.process_conversation_for_glyphs(conversation)

        if new_glyphs:
            for glyph in new_glyphs:
                print(f"Generated glyph: {glyph['tag_name']} ({glyph['glyph']})")
        else:
            print("No new glyphs generated for this conversation")
