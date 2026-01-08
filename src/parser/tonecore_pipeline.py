from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class SignalParserOutput:
    keyword: str = ""
    signal: str = ""
    voltage: str = ""
    tone: str = ""

    def to_dict(self) -> dict:
        return {
            "keyword": self.keyword,
            "signal": self.signal,
            "voltage": self.voltage,
            "tone": self.tone,
        }


@dataclass
class NRCOutput:
    emotion_scores: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"emotion_scores": dict(self.emotion_scores)}


@dataclass
class TextBlobOutput:
    polarity: float = 0.0
    subjectivity: float = 0.0

    def to_dict(self) -> dict:
        return {"polarity": float(self.polarity), "subjectivity": float(self.subjectivity)}


@dataclass
class SpacyOutput:
    nouns: List[str] = field(default_factory=list)
    verbs: List[str] = field(default_factory=list)
    adjectives: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"nouns": list(self.nouns), "verbs": list(self.verbs), "adjectives": list(self.adjectives)}


@dataclass
class MergedEmotionalData:
    signal_parser: List[SignalParserOutput] = field(default_factory=list)
    nrc: NRCOutput = field(default_factory=NRCOutput)
    textblob: TextBlobOutput = field(default_factory=TextBlobOutput)
    spacy: SpacyOutput = field(default_factory=SpacyOutput)
    dominant_emotion: str = "neutral"
    confidence: float = 0.0
    emotional_arc: List[str] = field(default_factory=lambda: ["neutral"])
    recommended_gates: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "signal_parser": [s.to_dict() for s in self.signal_parser],
            "nrc": self.nrc.to_dict(),
            "textblob": self.textblob.to_dict(),
            "spacy": self.spacy.to_dict(),
            "dominant_emotion": self.dominant_emotion,
            "confidence": float(self.confidence),
            "emotional_arc": list(self.emotional_arc),
            "recommended_gates": list(self.recommended_gates),
        }


@dataclass
class ChordProgression:
    chords: List[str]
    emotion_sequence: List[str]
    arc_description: str

    def to_dict(self) -> dict:
        return {"chords": list(self.chords), "emotion_sequence": list(self.emotion_sequence), "arc_description": self.arc_description}


class ToneCorePipeline:
    EMOTION_GATE_MAPPINGS = {
        "joy": ["Gate 5", "Gate 6"],
        "sadness": ["Gate 4", "Gate 10"],
        "fear": ["Gate 4", "Gate 2"],
        "neutral": ["Gate 9"],
    }

    def __init__(self, enable_cache: bool = False):
        self.enable_cache = enable_cache
        self._cache: Dict[str, MergedEmotionalData] = {}

    def analyze(self, text: str) -> MergedEmotionalData:
        key = text or ""
        if self.enable_cache and key in self._cache:
            return self._cache[key]

        # Very small heuristic-based pipeline sufficient for tests
        if not text or not text.strip():
            res = MergedEmotionalData(dominant_emotion="neutral", confidence=0.0)
        else:
            low = text.lower()
            if any(w in low for w in ("happy", "joy", "glad", "delighted")):
                dom = "joy"
                conf = 0.8
            elif any(w in low for w in ("sad", "grief", "loss", "alone")):
                dom = "sadness"
                conf = 0.7
            elif any(w in low for w in ("fear", "afraid", "scared", "panic")):
                dom = "fear"
                conf = 0.75
            else:
                dom = "neutral"
                conf = 0.4

            res = MergedEmotionalData(dominant_emotion=dom, confidence=conf)
            res.recommended_gates = self.EMOTION_GATE_MAPPINGS.get(dom, [])
            # Simple arc: repeat dominant emotion
            res.emotional_arc = [dom]

        if self.enable_cache:
            self._cache[key] = res

        return res

    def mergeEmotionalData(self, signal_parser, nrc, textblob, spacy) -> MergedEmotionalData:
        # Fused heuristics: prefer NRC top score, else polarity
        dom = "neutral"
        conf = 0.0
        if nrc and isinstance(nrc, NRCOutput) and nrc.emotion_scores:
            # choose highest-scoring emotion
            dom = max(nrc.emotion_scores.items(), key=lambda kv: kv[1])[0]
            conf = float(max(nrc.emotion_scores.values())) / 5.0 if nrc.emotion_scores else 0.5
        elif textblob and isinstance(textblob, TextBlobOutput):
            if textblob.polarity > 0.2:
                dom = "joy"
                conf = abs(textblob.polarity)
            elif textblob.polarity < -0.2:
                dom = "sadness"
                conf = abs(textblob.polarity)
        merged = MergedEmotionalData(signal_parser=signal_parser or [], nrc=nrc or NRCOutput(), textblob=textblob or TextBlobOutput(), spacy=spacy or SpacyOutput(), dominant_emotion=dom, confidence=conf)
        merged.recommended_gates = self.EMOTION_GATE_MAPPINGS.get(dom, [])
        merged.emotional_arc = [dom]
        return merged

    def generate_chord_progression(self, merged: MergedEmotionalData, length: int = 4) -> ChordProgression:
        emotion = merged.dominant_emotion or "neutral"
        # Map emotion to chords (simplified)
        base_map = {
            "joy": ["I", "IV", "V", "I"],
            "sadness": ["i", "iv", "V", "i"],
            "longing": ["i", "iv", "V", "i"],
            "fear": ["ii", "v", "i", "ii"],
            "neutral": ["I", "vi", "IV", "V"],
        }
        pattern = base_map.get(emotion, base_map["neutral"])
        # Repeat the pattern to reach requested length
        if length <= 0:
            length = 4
        seq = [pattern[i % len(pattern)] for i in range(length)]

        # Build emotion sequence based on the provided emotional arc where possible
        arc = merged.emotional_arc or [emotion]
        if not arc:
            arc = [emotion]
        # If arc has a single emotion, repeat it to match length
        if len(arc) == 1:
            emo_seq = [arc[0] for _ in range(length)]
        else:
            # Cycle through the arc to fill length
            emo_seq = [arc[i % len(arc)] for i in range(length)]

        # Arc description: mention transition when arc spans different emotions,
        # otherwise indicate sustained emotion.
        if len(set(arc)) > 1:
            arc_desc = "Transition: " + "->".join(arc[:2]) if len(arc) >= 2 else f"Transition: {arc[0]}"
        else:
            arc_desc = f"Sustained {arc[0]}"

        return ChordProgression(chords=seq, emotion_sequence=emo_seq, arc_description=arc_desc)

    def _calculate_emotional_arc(self, nrc: Optional[NRCOutput]) -> List[str]:
        """Compute a short emotional arc from an NRCOutput.

        Returns the top 3 emotions by score in descending order. If no
        scores are present, returns ["neutral"].
        """
        if not nrc or not isinstance(nrc, NRCOutput) or not nrc.emotion_scores:
            return ["neutral"]

        # Sort emotions by score descending and return top 3 keys
        sorted_emotions = sorted(nrc.emotion_scores.items(), key=lambda kv: kv[1], reverse=True)
        top_keys = [k for k, _ in sorted_emotions[:3]]
        return top_keys

    # convenience for tests
    def get_cache_stats(self) -> dict:
        return {"size": len(self._cache)}

    def clear_cache(self):
        self._cache.clear()


_GLOBAL_PIPELINE: Optional[ToneCorePipeline] = None


def get_pipeline() -> ToneCorePipeline:
    global _GLOBAL_PIPELINE
    if _GLOBAL_PIPELINE is None:
        _GLOBAL_PIPELINE = ToneCorePipeline(enable_cache=True)
    return _GLOBAL_PIPELINE


def analyze_text(text: str) -> MergedEmotionalData:
    return get_pipeline().analyze(text)


def generate_chord_progression(text_or_merged, length: int = 4) -> ChordProgression:
    if isinstance(text_or_merged, MergedEmotionalData):
        merged = text_or_merged
    else:
        merged = analyze_text(text_or_merged)
    return get_pipeline().generate_chord_progression(merged, length=length)
