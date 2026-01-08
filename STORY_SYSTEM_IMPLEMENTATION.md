# Story System Implementation Guide

**Status:** ✅ Complete and tested
**Date:** December 15, 2025
**Version:** 1.0
## 

## What You Now Have

A **complete, self-contained story editing system** that gives you full independence to write, edit,
validate, and build your Velinor story without needing an AI agent to modify JSON.

### The Pipeline

```
story_map_velinor.md (Your outline, source of truth)
         ↓
story_definitions.py (Readable Python, what you edit)
         ↓
build_story.py (Auto-convert to JSON)
         ↓
sample_story.json (What the game engine reads)
         ↓
story_validator.py (Catch errors before runtime)
```

## 

## Quick Start (3 Steps)

### 1. Edit Your Story

Open `velinor/stories/story_definitions.py` and modify the story:

```python
story.add_passage(
    name="market_arrival",
    text="""Your story text here. Write naturally.""",
    is_start=True,
    tags=["act1", "marketplace"]
)

# Add player choices
story.add_choice(
    from_passage_name="market_arrival",
    choice_text="What player sees",
    to_passage_name="next_scene"
)
```


### 2. Build to JSON

```bash
python velinor/stories/build_story.py
```


This converts your Python to JSON automatically.

### 3. Validate for Errors

```bash
python velinor/stories/build_story.py --validate
```


Catches broken links, dead ends, missing passages, etc.
## 

## File Inventory

| File | Purpose | Status |
|------|---------|--------|
| `story_definitions.py` | Python story authoring (EDIT THIS) | ✅ Working |
| `sample_story.json` | Generated JSON (auto-updated) | ✅ Generated |
| `build_story.py` | Build orchestrator (python → json) | ✅ Working |
| `story_validator.py` | Validation system | ✅ Working |
| `story_map_parser.py` | Markdown parser (optional) | ✅ Ready |
| `README.md` | Detailed usage guide | ✅ Complete |
## 

## Key Features

✅ **Readable Python Code**
- Story reads like Python, not JSON
- Clean Git diffs (meaningful version history)
- Comments and organization preserved

✅ **Auto-Generation**
- Python → JSON conversion (one command)
- Watch mode for auto-rebuild on save
- No manual JSON editing needed

✅ **Validation Built-In**
- Broken link detection
- Dead end warnings
- Unreachable content detection
- Missing field validation

✅ **Markdown Integration** (Optional)
- Parse your existing story_map_velinor.md
- Auto-generate Python scaffolding
- Keep outline and prose aligned

✅ **Complete Branching Support**
- Multiple choice paths per passage
- Converging story branches
- Path tracking via tags
## 

## Complete Workflow

```bash

# 1. Edit the story
nano velinor/stories/story_definitions.py

# 2. Save and auto-build (watch mode)
python velinor/stories/build_story.py --watch

# 3. In another terminal, validate + test
python velinor/stories/build_story.py --validate

# 4. Commit when happy
git add velinor/stories/story_definitions.py
git commit -m "story: [Your message]"

# 5. Push
git push
```

## 

## Story Structure (Current)

### Act 1: Marketplace Awakening
- **Start:** market_arrival
- **NPCs:** Ravi, Nima, Kaelen
- **Locations:** Market District, Thieves' Cache, Shrines
- **Passages:** 14 (prototype stage)
- **Choices:** Branching dialogue paths

### Path 1: Ravi's Trust
- Step forward openly
- Learn about the Tone
- Establish relationship

### Path 2: Nima's Caution
- Keep distance
- Ask careful questions
- Build respect through wisdom

### Path 3: Kaelen's Shadow
- Seek the Thieves' Cache
- Risky direct approach
- Enter the underground

### Shared Ending
- Marketplace Shelter (rest)
- Decision point for Act 2
## 

## Stat Effects System

Each choice can affect player stats:

```python
story.add_choice(
    from_passage_name="scene",
    choice_text="Push forward boldly",
    to_passage_name="next",
    # Stat effects optional - game engine applies these
    # Examples: courage, empathy, wisdom, trust, observation
)
```


The game engine reads these to track emotional trajectory.
## 

## Advanced Features

### Convert Markdown to Python

If you want to auto-generate Python from your Markdown outline:

```bash
python velinor/stories/build_story.py --parse-markdown
```


This reads `story_map_velinor.md` and creates Python scaffolding.

### Watch for Changes

Auto-rebuild while editing:

```bash
python velinor/stories/build_story.py --watch
```


Rebuilds JSON + validates every time you save story_definitions.py

### Validate as JSON

Check the generated JSON directly:

```bash
python velinor/stories/story_validator.py velinor/stories/sample_story.json
```

## 

## Common Tasks

### Add a New Passage

```python
story.add_passage(
    name="new_scene_name",
    text="""Multi-line story text works fine here.
    Indent for readability.""",
    tags=["act2", "location_name"]
)
```


### Link Two Passages

```python
story.add_choice(
    from_passage_name="current",
    choice_text="Go to the temple",
    to_passage_name="temple_entrance"
)
```


### Create a Branching Path

```python

# Decision point
story.add_choice(from_passage_name="fork", choice_text="Path A", to_passage_name="path_a_1")
story.add_choice(from_passage_name="fork", choice_text="Path B", to_passage_name="path_b_1")

# Both paths converge later
story.add_choice(from_passage_name="path_a_1", choice_text="Meet up", to_passage_name="convergence")
story.add_choice(from_passage_name="path_b_1", choice_text="Meet up", to_passage_name="convergence")
```


### Tag Organization

Use tags to organize:

```python
story.add_passage(
    name="scene",
    text="...",
    tags=[
        "act1",           # Which act
        "marketplace",    # Which location
        "ravi_path",      # Which NPC path
        "dialogue"        # What type
    ]
)
```


**Recommended tag system:**
- Act: `act1`, `act2`, `act3`, `act4`
- Location: `marketplace`, `archive`, `temple`, `underground`
- NPC: `ravi_path`, `nima_path`, `kaelen_path`
- Type: `dialogue`, `exploration`, `choice_point`, `ending`
## 

## Error Messages & Solutions

### "Passage 'X' has broken link to 'Y'"

Your choice points to a passage that doesn't exist.

**Fix:** Check the `to_passage_name` matches exactly:

```python
story.add_choice(
    from_passage_name="current",
    choice_text="Go somewhere",
    to_passage_name="correct_name"  # Must match exactly!
)
```


### "Start passage (pid=1) does not exist"

First passage not found.

**Fix:** Ensure your first passage has `is_start=True`:

```python
story.add_passage(
    name="market_arrival",
    text="...",
    is_start=True  # Only one passage should have this
)
```


### "Passage 'X' is a dead end"

Passage has no choices and isn't marked as ending.

**Fix (choose one):**
- Add choices: `story.add_choice(..., to_passage_name="next")`
- Mark as ending: Add to passage definition
- Add loop back: `story.add_choice(..., to_passage_name="previous")`
## 

## Version Control

Your `story_definitions.py` is pure Python, so Git diffs are clean:

```diff
- story.add_passage(name="old_keeper", text="...")
+ story.add_passage(name="ravi", text="...")
```


Much better than JSON diffs!

**Commit frequently:**

```bash
git add velinor/stories/story_definitions.py
git commit -m "story: Add Act 2 opening scene"
```

## 

## Next Steps

### Immediate (This Week)

1. **Review current prototype**
   - Read `velinor/stories/story_definitions.py`
   - See how the system works

2. **Update story content**
   - Replace Keeper scenes with Ravi/Nima
   - Update NPC dialogue throughout
   - Expand placeholder passages

3. **Extend Act 1**
   - Flesh out all branching paths
   - Add choice consequences
   - Create multiple endings

### Short Term (This Month)

4. **Write Acts 2-4**
   - Outline in Markdown
   - Convert to Python using parser
   - Fill in dialogue and description

5. **Test in game**
   - Run velinor-web with your story
   - Verify choices lead correctly
   - Check stat effects apply

6. **Iterate**
   - Edit story_definitions.py
   - Build + validate
   - Test + refine

### Long Term (Ongoing)

7. **Expand content**
   - Add more NPCs and relationships
   - Create deeper branching
   - Build multiple endings
   - Implement consequence tracking

8. **Optimize**
   - Performance improvements
   - Better stat tracking
   - Enhanced choice system
## 

## Integration with Velinor Engine

The game engine (`velinor-web`) loads `sample_story.json` and:

1. Reads story metadata (title, start passage) 2. Displays passage text to player 3. Provides
buttons for each choice 4. Applies stat effects when choices made 5. Navigates to next passage

**You don't modify JSON directly.** Just:
- Edit Python definitions
- Run build_story.py
- Game automatically picks up changes
## 

## Support & Documentation

- **Quick Reference:** `velinor/stories/README.md`
- **Build System:** `velinor/stories/build_story.py` (inline help)
- **Validation:** `velinor/stories/story_validator.py` (error messages)
- **Parser:** `velinor/stories/story_map_parser.py` (Markdown conversion)
## 

## Summary

You now have:

✅ A **readable, editable story system** (Python, not JSON) ✅ **Automatic JSON generation** (one
command) ✅ **Built-in validation** (catches errors early) ✅ **Git-friendly** (clean diffs, version
history) ✅ **Complete independence** (no agent needed for story edits) ✅ **Extensible architecture**
(add features easily)

**You're in control of your narrative.** 📖

Write the story. Run the build. Validate. Play. Repeat.
## 

## Quick Reference Commands

```bash

# Build story (Python → JSON)
python velinor/stories/build_story.py

# Build + validate
python velinor/stories/build_story.py --validate

# Watch for changes + auto-rebuild
python velinor/stories/build_story.py --watch

# Parse Markdown to Python scaffold
python velinor/stories/build_story.py --parse-markdown

# Just validate existing JSON
python velinor/stories/story_validator.py velinor/stories/sample_story.json
```

## 

**Ready to write?** Start editing `velinor/stories/story_definitions.py` and bring Velinor to life! 🌟
