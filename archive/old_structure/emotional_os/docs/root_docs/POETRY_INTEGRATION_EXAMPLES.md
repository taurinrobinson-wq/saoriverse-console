# Integration Examples

This shows how to integrate clean poetry data into all your existing processing systems.

## 1. Integration with Signal Extraction

**File**: `bulk_text_processor.py` (Updated)

```python
from poetry_data_hub import PoetryDataHub, ProcessingModeAdapter
from em_trace.signal_extraction import AdaptiveSignalExtractor

class EnhancedBulkTextProcessor:
    """Processes poetry through signal extraction using clean data."""

    def __init__(self):
        # Load clean poetry from hub
        self.hub = PoetryDataHub("poetry_data")
        self.adapter = ProcessingModeAdapter(self.hub)
        self.extractor = AdaptiveSignalExtractor()

    def process_all_poetry(self):
        """Process all validated poetry collections."""
        # Get clean poetry for signal extraction
        poetry_data = self.adapter.for_signal_extraction()

        results = {}
        for collection_name, text in poetry_data.items():
            print(f"Extracting signals from: {collection_name}")

            # Text is already clean, validated, non-fragmented
            signals = self.extractor.extract(text)
            results[collection_name] = signals

        return results

# Usage
processor = EnhancedBulkTextProcessor()
all_signals = processor.process_all_poetry()
```



## 2. Integration with Lexicon Learning

**File**: `learning/lexicon_learner.py` (Updated)

```python
from poetry_data_hub import PoetryDataHub, ProcessingModeAdapter
from learning.pattern_history import PatternHistory

class EnhancedLexiconLearner:
    """Learns emotional patterns from clean poetry."""

    def __init__(self):
        self.hub = PoetryDataHub("poetry_data")
        self.adapter = ProcessingModeAdapter(self.hub)
        self.patterns = PatternHistory()

    def learn_from_poetry(self):
        """Learn emotional lexicon from all poetry."""
        # Get clean poetry for learning
        poetry_data = self.adapter.for_lexicon_learning()

        for collection_name, text in poetry_data.items():
            print(f"Learning from: {collection_name}")

            # Text is already clean and validated
            self.patterns.learn_from_text(text)

        return self.patterns

# Usage
learner = EnhancedLexiconLearner()
updated_patterns = learner.learn_from_poetry()
```



## 3. Integration with Glyph Generation

**File**: `poetry_glyph_generator.py` (Updated)

```python
from poetry_data_hub import PoetryDataHub, ProcessingModeAdapter

class EnhancedPoetryGlyphGenerator:
    """Generates emotional glyphs from clean poetry."""

    def __init__(self):
        self.hub = PoetryDataHub("poetry_data")
        self.adapter = ProcessingModeAdapter(self.hub)

    def generate_glyphs_for_all(self):
        """Generate glyphs for all poetry collections."""
        # Get poetry formatted for glyph generation
        poetry_data = self.adapter.for_glyph_generation()  # Returns [(name, text), ...]

        glyphs = {}
        for name, text in poetry_data:
            print(f"Generating glyphs from: {name}")

            # Text is already clean and validated
            collection_glyphs = self.generate_glyphs(text, name)
            glyphs[name] = collection_glyphs

        return glyphs

    def generate_glyphs(self, text, collection_name):
        """Generate glyphs from cleaned poetry."""
        # Your existing glyph generation logic
        # Text quality is guaranteed
        pass

# Usage
generator = EnhancedPoetryGlyphGenerator()
all_glyphs = generator.generate_glyphs_for_all()
```



## 4. Integration with Ritual Processing

**File**: `ritual_processor.py` (New or Updated)

```python
from poetry_data_hub import PoetryDataHub, ProcessingModeAdapter

class RitualProcessor:
    """Processes poetry into emotional rituals."""

    def __init__(self):
        self.hub = PoetryDataHub("poetry_data")
        self.adapter = ProcessingModeAdapter(self.hub)

    def generate_rituals(self):
        """Generate emotional rituals from clean poetry."""
        # Get poetry with coherence checks
        poetry_data = self.adapter.for_ritual_processing()

        rituals = {}
        for name, text in poetry_data.items():
            print(f"Creating ritual from: {name}")

            # Text is coherence-checked for ritual processing
            ritual = self.create_ritual(text, name)
            rituals[name] = ritual

        return rituals

    def create_ritual(self, text, collection_name):
        """Transform poetry into emotional ritual."""
        # Your ritual creation logic
        pass

# Usage
processor = RitualProcessor()
all_rituals = processor.generate_rituals()
```



## 5. Complete End-to-End Workflow

```python
#!/usr/bin/env python3
"""
Complete workflow: Download → Clean → Validate → Process all modes
"""

from poetry_data_pipeline import PoetryDataPipeline
from poetry_data_hub import PoetryDataHub, ProcessingModeAdapter

def main():
    # Step 1: Run the pipeline (if not done)
    print("Step 1: Processing poetry data...")
    pipeline = PoetryDataPipeline("poetry_data")
    status = pipeline.get_pipeline_status()

    if status['pipeline_stats']['validated'] == 0:
        print("  Running full pipeline...")
        results = pipeline.process_all()
        print(f"  ✓ Processed {len(results['processed'])} collections")
    else:
        print(f"  ✓ Already have {status['hub_status']['validated']} validated collections")

    # Step 2: Access clean poetry for all processing modes
    print("\nStep 2: Accessing clean poetry...")
    hub = PoetryDataHub("poetry_data")
    adapter = ProcessingModeAdapter(hub)

    # Step 3: Process for all modes
    print("\nStep 3: Processing for all modes...")

    # Signal extraction
    signal_data = adapter.for_signal_extraction()
    print(f"  ✓ Signal extraction: {len(signal_data)} collections")

    # Lexicon learning
    lexicon_data = adapter.for_lexicon_learning()
    print(f"  ✓ Lexicon learning: {len(lexicon_data)} collections")

    # Glyph generation
    glyph_data = adapter.for_glyph_generation()
    print(f"  ✓ Glyph generation: {len(glyph_data)} collections")

    # Ritual processing
    ritual_data = adapter.for_ritual_processing()
    print(f"  ✓ Ritual processing: {len(ritual_data)} collections")

    # Step 4: Export for distribution
    print("\nStep 4: Exporting clean poetry...")
    manifest = pipeline.export_for_all_modes("poetry_export")
    print(f"  ✓ Exported to poetry_export/")

    # Summary
    hub_status = hub.get_hub_status()
    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETE")
    print("=" * 70)
    print(f"Total collections: {hub_status['total_collections']}")
    print(f"Validated: {hub_status['validated']}")
    print(f"Total words: {hub_status['total_words']:,}")
    print(f"Ready for all processing modes: YES")
    print("=" * 70)

if __name__ == "__main__":
    main()
```



## 6. Monitoring Quality

```python
#!/usr/bin/env python3
"""
Monitor poetry data quality over time
"""

from poetry_data_hub import PoetryDataHub

def monitor_quality():
    """Check quality metrics for all collections."""
    hub = PoetryDataHub("poetry_data")

    # Get all collections
    collections = hub.get_all_collections()

    print("POETRY DATA QUALITY REPORT")
    print("=" * 70)

    for collection in collections:
        name = collection['name']
        poet = collection['poet']

        # Get metrics
        metrics = hub.db.execute("""
            SELECT metric_name, metric_value FROM quality_metrics
            WHERE collection_id = ?
            ORDER BY metric_name
        """, (collection['id'],)).fetchall()

        print(f"\n{name} ({poet})")
        print("-" * 70)

        for metric_name, value in metrics:
            print(f"  {metric_name}: {value}")

    # Overall stats
    status = hub.get_hub_status()
    print("\n" + "=" * 70)
    print("OVERALL STATISTICS")
    print("=" * 70)
    print(f"Total collections: {status['total_collections']}")
    print(f"Validated: {status['validated']} ({status['validated_percent']:.1f}%)")
    print(f"Total words: {status['total_words']:,}")
    print(f"Average size: {status['avg_size'] / 1024:.1f} KB")
    print("=" * 70)

if __name__ == "__main__":
    monitor_quality()
```



## 7. Quick Access Pattern

For any processing system, the pattern is always the same:

```python
from poetry_data_hub import PoetryDataHub, ProcessingModeAdapter

# Initialize once
hub = PoetryDataHub("poetry_data")
adapter = ProcessingModeAdapter(hub)

# Get clean data for your processing mode
if my_mode == "signals":
    data = adapter.for_signal_extraction()
elif my_mode == "lexicon":
    data = adapter.for_lexicon_learning()
elif my_mode == "glyphs":
    data = adapter.for_glyph_generation()
elif my_mode == "rituals":
    data = adapter.for_ritual_processing()

# Use the data - it's guaranteed to be:

# ✓ Clean (OCR artifacts removed)

# ✓ Usable (no fragmentation)

# ✓ Validated (quality checked)

# ✓ Coherent (ready for processing)

for name, text in data.items():
    result = process_function(text)
```



## Integration Checklist

- [ ] Run pipeline to process all collections: `python poetry_data_pipeline.py --process`
- [ ] Check pipeline status: `python poetry_data_pipeline.py --status`
- [ ] Update signal extraction to use `ProcessingModeAdapter.for_signal_extraction()`
- [ ] Update lexicon learning to use `ProcessingModeAdapter.for_lexicon_learning()`
- [ ] Update glyph generation to use `ProcessingModeAdapter.for_glyph_generation()`
- [ ] Update ritual processing to use `ProcessingModeAdapter.for_ritual_processing()`
- [ ] Test each processing mode with clean data
- [ ] Monitor quality metrics regularly
- [ ] Export clean poetry periodically with `python poetry_data_pipeline.py --export`

## Benefits

✓ **Clean Data**: All OCR artifacts, encoding issues, fragmentation removed
✓ **Quality Assured**: Every collection validated before use
✓ **Mode-Ready**: Data formatted correctly for each processing system
✓ **Tracked**: Full audit trail of what was done to each text
✓ **Reproducible**: Same clean data used everywhere
✓ **Scalable**: Add more poetry collections anytime
✓ **Accessible**: Unified interface for all processing modes
