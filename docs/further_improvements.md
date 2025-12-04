# Multi-Modal Corpus Integration and STT/TTS Testing Plan

## 🎯 Objectives
- Integrate Student Corpus (text + mp3) and PolyAI conversational datasets into the system.
- Improve glyph diversity, conversational fluency, and response alternation.
- Enable multi-modal testing by comparing transcript analysis with audio (mp3) analysis.
- Strengthen TTS/STT capabilities by validating transcription accuracy against annotated transcripts.
- Establish a framework for audio, video, and facial expression recognition integration.

---

## ✅ Current Strengths
- Signal Parser, Response Generator V2, and Dynamic Composer integrated successfully.
- Response type alternation verified (Question → Reflection → Question → Affirmation).
- End-to-end dialogue flow functional with glyph parsing and response assignment.
- Efficient performance (0.01–0.05s response times).

---

## ⚠️ Observed Issues
- Glyph diversity limited (over-reliance on “Yearning Joy”).
- Affirmation templates collapse into reflection phrasing.
- Crisis disclosure and check-in recognition not yet tested.
- Positive affect inputs default to neutral reflection.
- Platitude guard requires validation.

---

## 🚀 Recommended Improvements
1. **Expand Glyph Testing:** Introduce grief, anger, loneliness, joy scenarios to diversify glyph selection.
2. **Enrich Affirmation Bank:** Add distinct affirmation templates (e.g., “I see that,” “That matters,” “I recognize your words”).
3. **Crisis Disclosure Simulation:** Validate consent-based crisis templates with suicidal ideation inputs.
4. **Check-in Recognition:** Add unit tests for continuity logic (user returns after invitation).
5. **Positive Affect Stress Test:** Ensure celebratory tone pools fire correctly for joy/gratitude inputs.
6. **Platitude Guard:** Confirm blocked phrases never appear in outputs.

---

## 📚 Corpus Integration for Lexicon & Fluency

### 1. Student-Transcribed Corpus of Spoken American English
- **Access Method:**
  - Use the online search interface to query spoken features.
  - Export results as `.csv` files with transcripts.
  - Download associated `.mp3` audio files for multi-modal testing.
- **Integration Strategy:**
  - Focus on **spoken English features** (fillers, disfluencies, quotatives, contractions).
  - Map features into glyph lexicon categories (e.g., “softener fillers” → Empathetic pool).
  - Use metadata (speaker demographics, genre) to enrich contextual awareness.
  - Avoid academic annotation layers; prioritize everyday conversational tokens.

### 2. PolyAI Conversational Datasets
- **Access Method:**
  - Clone repo: `git clone https://github.com/PolyAI-LDN/conversational-datasets.git`
  - Run preprocessing scripts (requires Python 2.7 + Apache Beam).
  - Data stored in JSON or TensorFlow formats.
- **Integration Strategy:**
  - Use **filtered subsets** (short, everyday exchanges).
  - Extract context/response pairs that reflect **natural, everyday conversation**.
  - Map pairs into glyph rotation banks to enrich fluency.
  - Exclude deleted/uninformative comments, long technical threads, and research-only metrics.

---

## 🎧 Multi-Modal Testing with MP3s

### Why it matters
- **Audio cadence:** Test prosody, pauses, fillers, disfluencies.
- **Emotion cues:** Tone of voice mapped to glyph pools (e.g., rising pitch → uncertainty → Clarifying pool).
- **Cross-modal validation:** Compare facial expression recognition + text parsing with audio signals.

### Integration Steps
1. **Audio ingestion module:**
   - Extend `main_v2.py` to accept `.mp3` input.
   - Use speech-to-text engine (Whisper/Vosk) for transcription.
   - Feed raw audio features (pitch, energy, pauses) + transcript into glyph parser.

2. **Feature extraction:**
   - Map prosodic features to emotional signals:
     - Long pauses → hesitation → Clarifying pool.
     - Rising pitch → uncertainty → Empathetic pool.
     - Flat tone → exhaustion → Grounded pool.

3. **Multi-modal fusion:**
   - Combine text, audio, and facial expression signals into unified glyph selection.
   - Weight signals by confidence (e.g., audio sadness overrides neutral text).

4. **Transcript vs Audio Comparison:**
   - Run Student Corpus `.mp3` files through system.
   - Compare glyph outputs against annotated transcripts.
   - Identify mismatches to improve STT accuracy and conversational fluency.

---

## 🧩 Fit with Existing System
- **Lexicon enrichment:** Spoken fillers become new glyph triggers.
- **Response generator:** Acknowledge tone (“I hear the heaviness in your voice”) alongside text.
- **Safety layer:** Crisis disclosures in audio form trigger consent-based templates.

---

## 🧪 Next Test Suite Additions
- Crisis scenarios with consent-based responses.
- Check-in cycles with recognition templates.
- Affirmation vs Reflection stress-tests.
- Joy inputs mapped to celebratory glyphs.
- Corpus-derived filler/disfluency handling tests.
- Audio vs transcript comparison tests for STT accuracy.

---

## 📌 Implementation Notes
- **Corpus Access:**
  - Student Corpus: Export CSV + download mp3s.
  - PolyAI: Clone repo, run preprocessing scripts, filter everyday exchanges.
- **Integration:**
  - Add corpus-derived tokens/templates into glyph lexicon.
  - Extend response generator with multi-modal fusion logic.
- **Testing:**
  - Compare transcript vs audio analysis for accuracy.
  - Validate glyph diversity and alternation with multi-modal inputs.

---

This document provides a detailed implementation plan for integrating spoken corpora and conversational datasets into the system, enabling multi-modal testing and improving both STT/TTS capabilities and conversational fluency.
