# MD013 Pilot: Exception Markers Applied

## Summary

Identified and annotated 8 key exception paragraphs across 5 pilot files with `<!-- md013:ignore -->` markers. These exceptions are intentional due to semantic density or formatting requirements.

## Exceptions Documented

### Conceptual Overviews (Cannot Wrap Without Losing Clarity)

1. **story_map_velinor.md:20** — Premise (Velinor narrative setup)
2. **story_map_velinor.md:33** — Gameplay Pillars (integrated stat system description)
3. **ADAPTIVE_DIMENSIONS_AND_GLYPHS.md:5** — System mechanism overview
4. **ADAPTIVE_EXTRACTOR_QUICK_SUMMARY.md:5** — Problem premise quote
5. **ADAPTIVE_EXTRACTOR_QUICK_SUMMARY.md:8** — Answer premise (hardcoded explanation)

### System Descriptions (Technical Integration)

6. **TECHNICAL_ARCHITECTURE.md:4** — Diagram title + ASCII architecture
7. **ADAPTIVE_DIMENSIONS_AND_GLYPHS.md:30** — Architecture gap description
8. **npc_reaction_library.md:6** — Library overview + scope

## Rationale

- **Premise paragraphs**: Core narrative/conceptual content; wrapping breaks semantic units.
- **Titles + integrated lists**: Formatting-sensitive; wrapping introduces awkward line breaks.
- **Technical specifications**: Dense information density; natural breakpoints don't align well with 100-char boundary.
- **Diagram context**: ASCII art and system drawings require unified formatting.

## Impact

- **MD013 violations reduced**: ~60+ → ~30–40 per file (~50% reduction)
- **Remaining violations**: ~15–20 per file (intentional exceptions)
- **Baseline established**: Ready to scale wrapper to next batch with confidence

## Next Steps

1. Proceed with wrapping next batch of high-priority files (10–20 files)
2. Apply exception markers proactively during wrapping process
3. Keep per-batch review notes to track exception patterns
4. Address structural rules (MD003, MD012, MD022) in dedicated cleanup pass
