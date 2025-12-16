# API Reference - SaoriVerse Console

**Date**: December 3, 2025

##

## Core Modules

### src.response_generator

**Main orchestrator for the emotional response pipeline.**

#### `process_user_input(user_input: str, context: dict = None) -> str`

Orchestrate the entire response pipeline from user input to response text.

**Parameters:**

- `user_input`: User's text input
- `context`: Optional context dict with metadata

**Returns:** Response text (str)

**Steps:**

1. Tag input (symbolic tags) 2. Detect phase 3. Generate tone-adapted response 4. Adapt to
user-facing language 5. Store relational memory capsule

**Raises:** May raise on invalid input or system errors

**Example:**

```python
from src import process_user_input

response = process_user_input("I'm feeling overwhelmed")
```text

```text
```


##

### src.signal_parser

**Convert text to emotional signals.**

#### `parse_input(user_input: str) -> dict`

Extract emotional signals from user text.

**Parameters:**

- `user_input`: User's text input

**Returns:** Signal dict with keys:

- `voltage`: Intensity (0.0-1.0)
- `tone`: Emotional tone (str)
- `attunement`: Connection level (0.0-1.0)
- `certainty`: Confidence in assessment (0.0-1.0)
- `valence`: Positive/negative (-1.0 to 1.0)

**Example:**

```python

from src.signal_parser import parse_input

signal = parse_input("I'm happy about the news")
print(signal)

# {
#   "voltage": 0.7,
#   "tone": "Joy",
#   "attunement": 0.8,
#   "certainty": 0.9,
#   "valence": 0.8

```text

```

#### `extract_themes(user_input: str) -> list`

Extract semantic themes from text.

**Parameters:**

- `user_input`: User's text input

**Returns:** List of theme strings

**Example:**

```python

themes = extract_themes("Work is stressful and relationships are complicated")

```text
```text

```

##

### src.enhanced_response_composer

**Compose multi-glyph responses.**

#### `class DynamicResponseComposer`

Blend multiple glyphs into coherent responses.

##### `__init__(reward_model=None)`

Initialize composer with optional reward model.

**Parameters:**

- `reward_model`: Optional reward model for response ranking

##### `compose_multi_glyph_response(signal: dict, glyphs: list) -> str`

Compose response from multiple glyphs.

**Parameters:**

- `signal`: Emotional signal dict
- `glyphs`: List of glyph dicts

**Returns:** Composed response text

**Example:**

```python


from src.enhanced_response_composer import DynamicResponseComposer

composer = DynamicResponseComposer()

```text
```


##

### src.voice_interface

**High-level voice I/O API.**

#### `class VoiceInterface`

Orchestrate voice input/output for Streamlit app.

##### `__init__()`

Initialize voice interface with TTS/STT engines.

##### `transcribe_audio(audio_path: str) -> str`

Transcribe audio file to text (STT).

**Parameters:**

- `audio_path`: Path to audio file (mp3, wav, etc.)

**Returns:** Transcribed text

**Example:**

```python
from src.voice_interface import VoiceInterface

voice = VoiceInterface()
```text

```text
```


##### `synthesize_speech(text: str, glyph: dict) -> bytes`

Synthesize text to speech with glyph prosody (TTS).

**Parameters:**

- `text`: Text to synthesize
- `glyph`: Glyph dict with emotional context

**Returns:** Audio bytes (mp3 format)

**Example:**

```python

```text

```

##

### src.relational_memory

**Persist interaction memories for learning.**

#### `class RelationalMemoryCapsule`

Represent a single interaction memory.

**Attributes:**

- `user_input`: Original user input
- `signal`: Extracted emotional signal
- `response`: Generated response
- `glyph`: Selected glyph
- `timestamp`: When interaction occurred
- `session_id`: Session identifier

#### `store_capsule(capsule: RelationalMemoryCapsule) -> bool`

Store memory capsule to disk.

**Parameters:**

- `capsule`: RelationalMemoryCapsule instance

**Returns:** True if stored successfully

**Example:**

```python

from src.relational_memory import RelationalMemoryCapsule, store_capsule

capsule = RelationalMemoryCapsule( user_input="I'm feeling lost", signal=signal_dict, response="That
sounds difficult...", glyph=selected_glyph, )

```text
```text

```

#### `query_capsules(session_id: str) -> list`

Retrieve memories for a session.

**Parameters:**

- `session_id`: Session identifier

**Returns:** List of RelationalMemoryCapsule instances

##

### src.prosody_planner

**Map emotional context to speech prosody.**

#### `class ProsodyPlanner`

Plan prosody parameters based on glyph.

##### `__init__()`

Initialize prosody planner with glyph-to-prosody mappings.

##### `plan_prosody(glyph: dict, text: str) -> dict`

Generate prosody parameters for text.

**Parameters:**

- `glyph`: Glyph dict with emotional context
- `text`: Text to generate prosody for

**Returns:** Prosody dict with:

- `pitch`: Pitch range (0.5-2.0)
- `rate`: Speaking rate (0.5-2.0)
- `energy`: Volume/intensity (0.0-1.0)
- `pauses`: Pause locations and durations

**Example:**

```python


from src.prosody_planner import ProsodyPlanner

planner = ProsodyPlanner()

```text
```


##

### src.streaming_tts

**Streaming Text-to-Speech engine.**

#### `class StreamingTTS`

Manage text-to-speech synthesis.

##### `__init__()`

Initialize TTS engine.

##### `synthesize(text: str, prosody: dict = None) -> bytes`

Synthesize text to audio.

**Parameters:**

- `text`: Text to synthesize
- `prosody`: Optional prosody parameters

**Returns:** Audio bytes (mp3 format)

**Example:**

```python
from src.streaming_tts import StreamingTTS

tts = StreamingTTS()
```text

```text
```


##

### src.audio_pipeline

**Speech-to-Text (STT) pipeline.**

#### `class AudioPipeline`

Manage audio input and transcription.

##### `__init__()`

Initialize audio pipeline with STT engine.

##### `transcribe(audio_path: str) -> str`

Transcribe audio file to text.

**Parameters:**

- `audio_path`: Path to audio file

**Returns:** Transcribed text

**Raises:** May raise on invalid audio file

**Example:**

```python

from src.audio_pipeline import AudioPipeline

pipeline = AudioPipeline()

```text

```

##

### src.lexicon_learner

**Learn from interactions to improve lexicon.**

#### `class LexiconLearner`

Learn emotional patterns from user interactions.

##### `__init__()`

Initialize lexicon learner.

##### `extract_patterns(user_input: str, signal: dict) -> list`

Extract learnable patterns from interaction.

**Parameters:**

- `user_input`: User's text
- `signal`: Extracted emotional signal

**Returns:** List of pattern dicts

**Example:**

```python

from src.lexicon_learner import LexiconLearner

learner = LexiconLearner()

```text
```text

```

##

## Entry Point

### app.py

**Streamlit application entry point.**

**Run the app:**

```bash


```text
```


**Environment:**

- Port: 8501 (default Streamlit)
- Browser: Opens automatically
- Auth: Optional (configured in app)

##

## Common Workflows

### Text-to-Response (Text Chat)

```python
from src import process_user_input

response = process_user_input("I'm feeling lost")
```text

```text
```


### Audio-to-Audio (Voice Chat)

```python

from src.voice_interface import VoiceInterface
from src import process_user_input

voice = VoiceInterface()

# 1. Transcribe audio to text
text = voice.transcribe_audio("user_input.mp3")

# 2. Generate response
response = process_user_input(text)

# 3. Synthesize response to audio

```text

```

### Learning System

```python

from src.signal_parser import parse_input from src.lexicon_learner import LexiconLearner from
src.relational_memory import RelationalMemoryCapsule, store_capsule

user_input = "I'm feeling overwhelmed" signal = parse_input(user_input)

# Learn from interaction
learner = LexiconLearner() patterns = learner.extract_patterns(user_input, signal)

# Store memory
capsule = RelationalMemoryCapsule( user_input=user_input, signal=signal, response=response,
glyph=selected_glyph, )

```text
```text

```

##

## Error Handling

All API functions may raise exceptions. Recommended pattern:

```python


from src import process_user_input

try: response = process_user_input(user_input) except ValueError as e: print(f"Invalid input: {e}")
except Exception as e:

```text
```


##

## Data Structures

### Signal Dict

```python
{
    "voltage": 0.6,              # Intensity (0.0-1.0)
    "tone": "Yearning",          # Emotional tone
    "attunement": 0.7,           # Connection level
    "certainty": 0.5,            # Confidence
    "valence": 0.3,              # Positive/negative
```text

```text
```


### Glyph Dict

```python

{
    "glyph_name": "Euphoric Yearning",
    "gate": "Gate 5",
    "description": "Hopeful desire with presence",
    "response_templates": [...],
    "base_emotion": "Joy",
    "prosody_profile": {...},

```text

```

### Prosody Dict

```python

{ "pitch": 1.2,                # Pitch range "rate": 0.9,                 # Speaking rate "energy":
0.8,               # Volume/intensity "pauses": [                  # Pause locations {"position":
0.3, "duration": 0.5}, {"position": 0.7, "duration": 0.3}, ]

```text
```text

```

##

## Module Relationships

```


app.py (Streamlit) ↓ src.response_generator (main orchestrator)
    ├── src.signal_parser
    ├── src.response_adapter
    ├── src.enhanced_response_composer
    ├── src.relational_memory
    └── src.phase_modulator

src.voice_interface
    ├── src.audio_pipeline (STT)
    ├── src.streaming_tts (TTS)
    └── src.prosody_planner

src.lexicon_learner
    └── src.relational_memory

```

##

**For architecture overview, see**: `docs/ARCHITECTURE.md`
**For testing, see**: `docs/TESTING_GUIDE.md`
