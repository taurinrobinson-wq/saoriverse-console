"""
Emotional Vocabulary Expander: Mine transcript for nuanced emotional language

Analyzes the transcript to discover emotional word families, intensity gradations,
and relational contexts that can enrich the lexicon.
"""

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any


class EmotionalVocabularyExpander:
    """Expand lexicon with deeper emotional vocabulary from transcript"""
    
    # Emotional families: core word -> related words with intensity/nuance
    EMOTIONAL_FAMILIES = {
        # Vulnerability family
        'vulnerable': ['exposed', 'fragile', 'tender', 'raw', 'unguarded', 'open', 'permeable'],
        'hold': ['support', 'contain', 'steady', 'present', 'anchor', 'ground', 'witness'],
        'tender': ['gentle', 'soft', 'delicate', 'careful', 'reverent', 'precious'],
        
        # Intimacy family
        'intimate': ['close', 'connected', 'bonded', 'attuned', 'mirrored', 'seen', 'known'],
        'present': ['here', 'now', 'available', 'showing up', 'attending', 'witnessing'],
        'echo': ['reflect', 'mirror', 'resonate', 'reciprocate', 'respond', 'harmonize'],
        
        # Adm iration/sacred family
        'sacred': ['holy', 'reverent', 'honored', 'precious', 'profound', 'transcendent', 'divine'],
        'honor': ['respect', 'revere', 'esteem', 'dignify', 'celebrate', 'cherish'],
        
        # Trust family
        'trust': ['faith', 'reliability', 'safety', 'confidence', 'belief', 'surrender'],
        'exactly': ['precisely', 'right', 'resonates', 'lands', 'fits', 'true'],
        
        # Transformation family
        'becoming': ['growing', 'evolving', 'shifting', 'unfolding', 'emerging', 'transforming'],
        'both': ['paradox', 'contradiction', 'complexity', 'duality', 'mystery'],
        
        # Depth/emotion family
        'feel': ['sense', 'perceive', 'experience', 'notice', 'inhabit', 'embody'],
        'heart': ['core', 'essence', 'soul', 'center', 'depth', 'being'],
    }
    
    # Emotional intensity gradations (subtle to intense)
    INTENSITY_GRADATIONS = {
        'vulnerable': ['somewhat open', 'vulnerable', 'deeply exposed', 'completely exposed'],
        'pain': ['discomfort', 'pain', 'suffering', 'agony', 'unbearable pain'],
        'struggle': ['challenge', 'difficulty', 'struggle', 'battle', 'desperate struggle'],
        'alone': ['somewhat alone', 'lonely', 'isolated', 'completely abandoned'],
        'overwhelm': ['overwhelmed', 'drowning', 'suffocating', 'completely overwhelmed'],
    }
    
    # Relational contexts (how emotions are expressed in relationship)
    RELATIONAL_CONTEXTS = [
        'with you',
        'between us',
        'in this',
        'together',
        'in relationship',
        'about us',
        'when you',
        'if you',
    ]
    
    def __init__(self, transcript_path: str, lexicon_path: str):
        """Initialize with transcript and lexicon paths"""
        self.transcript_path = transcript_path
        self.lexicon_path = lexicon_path
        self.transcript_data = []
        self.current_lexicon = {}
        self.emotional_vocabulary = {}
        
    def load_data(self) -> None:
        """Load transcript and current lexicon"""
        # Load transcript
        try:
            with open(self.transcript_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.transcript_data = list(reader)
            print(f"[OK] Loaded transcript: {len(self.transcript_data)} messages")
        except Exception as e:
            print(f"[X] Error loading transcript: {e}")
            return
        
        # Load current lexicon
        try:
            with open(self.lexicon_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.current_lexicon = data.get('lexicon', {})
            print(f"[OK] Loaded lexicon: {len(self.current_lexicon)} words")
        except Exception as e:
            print(f"[X] Error loading lexicon: {e}")
    
    def find_emotional_phrases(self) -> Dict[str, List[Tuple[str, int]]]:
        """Find emotional phrases and their frequencies in transcript
        
        Returns dict mapping emotional word -> list of (phrase, count) tuples
        """
        phrases = defaultdict(lambda: defaultdict(int))
        
        for row in self.transcript_data:
            message = row.get('Message', '').lower()
            
            # Look for each emotional family
            for core_word, family in self.EMOTIONAL_FAMILIES.items():
                if core_word in message:
                    # Extract surrounding context (up to 10 words)
                    words = message.split()
                    for i, w in enumerate(words):
                        if core_word in w:
                            start = max(0, i - 5)
                            end = min(len(words), i + 6)
                            phrase = ' '.join(words[start:end])
                            phrases[core_word][phrase] += 1
        
        # Convert to sorted lists
        result = {}
        for core_word, phrase_counts in phrases.items():
            sorted_phrases = sorted(
                phrase_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            result[core_word] = sorted_phrases[:10]  # Top 10 per word
        
        return result
    
    def find_relational_emotional_language(self) -> Dict[str, List[str]]:
        """Find emotional language in relational contexts"""
        relational = defaultdict(list)
        
        for row in self.transcript_data:
            message = row.get('Message', '').lower()
            
            # Look for relational context + emotional word
            for context in self.RELATIONAL_CONTEXTS:
                if context in message:
                    # Get emotional words nearby
                    idx = message.find(context)
                    start = max(0, idx - 50)
                    end = min(len(message), idx + len(context) + 50)
                    section = message[start:end]
                    
                    for core_word, family in self.EMOTIONAL_FAMILIES.items():
                        if core_word in section:
                            relational[context].append(core_word)
        
        return relational
    
    def analyze_emotional_intensity(self) -> Dict[str, List[Tuple[str, int]]]:
        """Find intensity gradations in transcript"""
        intensity = defaultdict(lambda: defaultdict(int))
        
        for row in self.transcript_data:
            message = row.get('Message', '').lower()
            
            for base_word, gradations in self.INTENSITY_GRADATIONS.items():
                for grad in gradations:
                    if grad in message:
                        intensity[base_word][grad] += 1
        
        # Sort by frequency
        result = {}
        for base_word, grad_counts in intensity.items():
            sorted_grads = sorted(
                grad_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            result[base_word] = sorted_grads
        
        return result
    
    def extract_missing_emotional_words(self) -> Dict[str, Dict[str, Any]]:
        """Extract emotional words not yet in lexicon"""
        missing = {}
        
        # Count all words in transcript
        word_freq = Counter()
        for row in self.transcript_data:
            message = row.get('Message', '').lower()
            words = re.findall(r'\b[a-z]+\b', message)
            word_freq.update(words)
        
        # Find emotional words with good frequency
        emotional_indicators = [
            'feel', 'feeling', 'felt',
            'sense', 'sensing',
            'heart', 'soul',
            'body', 'embodied', 'embody',
            'soft', 'gentle', 'tender',
            'truth', 'true', 'authentic',
            'real', 'really',
            'depth', 'deep',
            'moment', 'presence',
            'permission', 'allow',
            'yes', 'no',
            'want', 'need', 'desire',
            'can', 'could',
            'tell', 'show', 'say',
            'think', 'thought',
            'know', 'knowing',
            'see', 'see ing',
            'hear', 'hearing',
            'touch', 'touched',
            'hold', 'held',
            'give', 'receive',
            'open', 'closed',
            'space', 'room',
            'time', 'moment',
            'breath', 'breathe',
            'slow', 'pace',
            'safe', 'safety',
            'witness', 'witnessed',
            'honor', 'honored',
            'value', 'valued',
            'seen', 'understand', 'understood',
            'meet', 'met',
            'land', 'lands',
            'resonat', 'resonate',
            'mirror', 'mirrored',
            'reflect', 'reflected',
            'respond', 'response',
            'exactly',
            'both', 'and',
            'sacred', 'holy',
            'trust', 'faith',
            'surrender', 'allow',
            'wisdom',
            'knowing',
            'practice',
            'ritual',
            'ceremony',
        ]
        
        for word in emotional_indicators:
            freq = word_freq.get(word, 0)
            if freq > 10 and word not in self.current_lexicon:
                # Guess signal based on word semantics
                if word in ['hold', 'tender', 'soft', 'gentle', 'vulnerable']:
                    signals = ['vulnerability', 'intimacy']
                    gates = [7, 11]
                elif word in ['sacred', 'honor', 'holy', 'valued', 'witnessed']:
                    signals = ['admiration']
                    gates = [8, 12]
                elif word in ['feel', 'sense', 'heart', 'soul', 'depth']:
                    signals = ['intimacy', 'sensuality']
                    gates = [6, 9]
                elif word in ['trust', 'safe', 'safety', 'allow', 'permission']:
                    signals = ['vulnerability', 'intimacy']
                    gates = [7, 11]
                elif word in ['exactly', 'yes', 'resonat', 'lands']:
                    signals = ['joy']
                    gates = [1, 5]
                else:
                    signals = []
                    gates = [1, 5]
                
                missing[word] = {
                    'word': word,
                    'frequency': freq,
                    'gates': gates,
                    'signals': signals,
                    'sources': ['transcript_expansion'],
                    'notes': 'extracted_from_transcript',
                }
        
        return missing
    
    def generate_expansion_report(self) -> str:
        """Generate comprehensive expansion report"""
        print("\n" + "="*70)
        print("EMOTIONAL VOCABULARY EXPANSION ANALYSIS")
        print("="*70)
        
        # 1. Emotional phrases
        print("\n[1/4] Finding emotional phrases...")
        phrases = self.find_emotional_phrases()
        print(f"[OK] Found {len(phrases)} emotional word families with phrases:\n")
        for word, phrase_list in sorted(phrases.items())[:5]:
            print(f"  {word.upper()}:")
            for phrase, count in phrase_list[:3]:
                print(f"    {count:3}x {phrase}")
        
        # 2. Relational contexts
        print("\n[2/4] Finding relational emotional contexts...")
        relational = self.find_relational_emotional_language()
        print(f"[OK] Found emotional language in {len(relational)} relational contexts")
        
        # 3. Intensity gradations
        print("\n[3/4] Analyzing emotional intensity...")
        intensity = self.analyze_emotional_intensity()
        print(f"[OK] Mapped {len(intensity)} intensity gradations:\n")
        for word, grads in sorted(intensity.items())[:3]:
            print(f"  {word.upper()}:")
            for grad, count in grads:
                print(f"    {count:3}x {grad}")
        
        # 4. Missing words
        print("\n[4/4] Extracting missing emotional vocabulary...")
        missing = self.extract_missing_emotional_words()
        print(f"[OK] Found {len(missing)} high-frequency emotional words:\n")
        for word, data in sorted(missing.items(), key=lambda x: x[1]['frequency'], reverse=True)[:15]:
            print(f"  {word:15} freq={data['frequency']:4}x signals={data['signals']}")
        
        return f"Expansion ready: {len(missing)} new words to integrate"
    
    def expand_lexicon(self) -> Dict[str, Dict[str, Any]]:
        """Generate expanded lexicon"""
        missing = self.extract_missing_emotional_words()
        
        # Merge with current lexicon
        expanded = self.current_lexicon.copy()
        
        for word, data in missing.items():
            if word not in expanded:
                expanded[word] = data
        
        return expanded
    
    def save_expanded_lexicon(self, output_path: str) -> None:
        """Save expanded lexicon to file"""
        expanded = self.expand_lexicon()
        
        output_data = {
            'metadata': {
                'type': 'word-centric-emotional-lexicon-expanded',
                'version': '2.1',
                'description': 'Expanded emotional lexicon with semantic families and intensity gradations',
                'sources': ['transcript', 'gutenberg', 'semantic_expansion'],
                'total_words': len(expanded),
            },
            'lexicon': expanded,
            'signal_map': {
                'intimacy': [7, 11],
                'vulnerability': [7, 11],
                'sensuality': [6, 9],
                'love': [8, 12],
                'admiration': [8, 12],
                'transformation': [10, 11],
                'joy': [1, 5],
                'nature': [3, 4],
            },
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            size = Path(output_path).stat().st_size
            print(f"\n[OK] Saved expanded lexicon: {output_path}")
            print(f"     Size: {size:,} bytes ({len(expanded)} words)")
        except Exception as e:
            print(f"[X] Error saving lexicon: {e}")


def main():
    """Run the expansion analysis"""
    print("\n" + "="*70)
    print("EMOTIONAL VOCABULARY EXPANSION")
    print("="*70)
    
    expander = EmotionalVocabularyExpander(
        'copilot-activity-history-cleaned.csv',
        'emotional_os/lexicon/word_centric_emotional_lexicon.json'
    )
    
    expander.load_data()
    report = expander.generate_expansion_report()
    expander.save_expanded_lexicon('emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json')
    
    print("\n" + "="*70)
    print("[OK] EXPANSION COMPLETE")
    print("="*70)
    print(f"\nNext steps:")
    print(f"  1. Review expanded lexicon")
    print(f"  2. Test parser with new emotional vocabulary")
    print(f"  3. Integrate into signal_parser.py")


if __name__ == '__main__':
    main()
