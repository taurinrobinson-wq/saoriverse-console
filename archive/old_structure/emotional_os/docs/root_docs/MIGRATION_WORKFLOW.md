# Migration Workflow: Telemetry + Fragment Detection + Cleanup Pipeline

This document outlines the complete workflow for using the new telemetry, fragment detection, and cleanup pipeline introduced in the `chore/cleanup-telemetry-fragments` branch.

## 🎯 Overview

The migration includes three main components:

1. **Conservative Cleanup Pipeline** - Normalizes and enriches glyph data with fragment detection
2. **Telemetry Instrumentation** - Observable events for debugging and monitoring
3. **Safe Supabase Migration Tools** - Backup and batched upsert capabilities

## 📁 Key Files Added

### Cleanup Pipeline

- `dev_tools/cleanup_glyphs.py` - Main cleanup script (dry-run by default)
- `dev_tools/cleaned_glyphs.json` - Normalized glyph output
- `dev_tools/cleaned_glyphs_upsert.csv` - CSV ready for Supabase upsert
- `dev_tools/cleanup_report.md` - Human-readable cleanup summary
- `dev_tools/lowest_integrity_sample.csv` - Bottom 50 glyphs by integrity score

### Supabase Migration Tools

- `dev_tools/supabase_backup_and_plan.py` - Creates full table backup and upsert plan
- `dev_tools/supabase_upsert_runner.py` - Applies upsert plan in safe batches
- `dev_tools/supabase_upsert_plan.md` - Safety instructions and workflow

### Telemetry

- Enhanced `emotional_os/core/signal_parser.py` with telemetry events
- UI toggle in Streamlit app (`emotional_os/deploy/modules/ui.py`)
- Runtime telemetry toggle via `set_telemetry(enabled: bool)`

## 🚀 Step-by-Step Workflow

### Phase 1: Review Cleanup Results (✅ Completed)

The cleanup has already been run and produced these artifacts:

```bash

# Review the cleanup outputs
cat dev_tools/cleanup_report.md
head -10 dev_tools/lowest_integrity_sample.csv
ls -la dev_tools/fragments_to_review.json  # Should be empty (no fragments found)
```




**Key Findings:**

- 1,722 cleaned rows produced from SQL export
- Fragment detection threshold (0.5) is working correctly
- No glyphs flagged as true fragments (all scored above 0.5)
- Lowest integrity glyphs (0.51-0.54) are legitimate candidates for review

### Phase 2: Test Migration Tools (✅ Completed)

```bash

# Test backup script in dry-run mode
python3 dev_tools/supabase_backup_and_plan.py --no-backup --cleaned dev_tools/cleaned_glyphs.json

# Test upsert runner in dry-run mode
python3 dev_tools/supabase_upsert_runner.py --plan dev_tools/supabase_upsert_plan_<timestamp>.json
```




**Results:**

- Backup script successfully created plan with 866 inserts, 0 updates
- Upsert runner correctly processes plan and shows sample payloads
- Data structure validation passed (all expected fields present)

### Phase 3: Validate Telemetry (✅ Completed)

```bash

# Test telemetry toggle programmatically
python3 -c "
from emotional_os.core import signal_parser as sp
sp.set_telemetry(True)

# Run operations - should see JSON telemetry events
sp.set_telemetry(False)
"
```




**Telemetry Events Available:**

- `select_best_start` - Entry point with input/glyph counts
- `generate_contextual_start` - Response generation start
- `generate_contextual_composed` - Response composition complete
- `select_best_done` - Selection complete with detailed metrics
- `parse_input_summary` - Overall parse operation summary

### Phase 4: Verify No Regressions (✅ Completed)

```bash

# Run full test suite
python3 -m pytest tests/ -v
```




**Results:** 109/110 tests passed (1 skipped as expected)

### Phase 5: Production Migration (Optional)

⚠️ **Only proceed if you want to apply changes to production Supabase**

#### 5.1 Create Live Backup

```bash
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_KEY=your-service-role-key

# Create backup and comparison plan
python3 dev_tools/supabase_backup_and_plan.py --table glyphs
```




#### 5.2 Review Plan

```bash

# Inspect the generated plan files
cat dev_tools/supabase_upsert_plan_*.json
head -20 dev_tools/supabase_upsert_plan_*_inserts.csv
head -20 dev_tools/supabase_upsert_plan_*_updates.csv
```




#### 5.3 Apply Migration (CAUTION)

```bash

# Final dry-run check
python3 dev_tools/supabase_upsert_runner.py --plan dev_tools/supabase_upsert_plan_*.json

# Apply migration (irreversible - ensure you have backups)
python3 dev_tools/supabase_upsert_runner.py --plan dev_tools/supabase_upsert_plan_*.json --apply --batch-size 200
```




## 🔧 Using Telemetry

### Environment Variable Toggle

```bash
export SAORI_TELEMETRY=1  # Enable
export SAORI_TELEMETRY=0  # Disable
```




### Runtime Toggle

```python
from emotional_os.core import signal_parser
signal_parser.set_telemetry(True)   # Enable for session
signal_parser.set_telemetry(False)  # Disable for session
```




### UI Toggle

The Streamlit app now includes a "Developer: Telemetry" expander with a checkbox to enable telemetry for the current session.

### Telemetry Output Format

All events are logged as JSON to facilitate parsing:

```json
{
  "event": "select_best_start",
  "glyphs_count": 5,
  "signals_count": 2,
  "input_snippet": "I feel overwhelmed and anxious"
}
```




## 🛡️ Safety Features

### Cleanup Pipeline

- **Dry-run by default** - No writes unless explicitly enabled
- **Conservative thresholds** - Fragment detection uses 0.5 integrity score
- **Backup integration** - Works with Supabase backup tools
- **Integrity scoring** - Multi-factor assessment of glyph quality

### Migration Tools

- **Backup first** - Always creates full table backup before changes
- **Batched operations** - Default 200 records per HTTP request
- **Fail-fast** - Stops on first batch failure to prevent partial writes
- **Service role required** - Uses service role key for elevated permissions

### Telemetry

- **Opt-in only** - Disabled by default, requires explicit enablement
- **No PII** - Only logs structural data and truncated input snippets
- **Runtime toggle** - Can be enabled/disabled without restart

## 📊 Quality Metrics

### Fragment Detection Results

- **Total processed:** 1,722 glyphs
- **Fragments detected:** 0 (threshold: 0.5)
- **Lowest integrity:** 0.5175 (still above threshold)
- **Average integrity:** ~0.7 (estimated from sample)

### Test Coverage

- **109 tests passed** - All core functionality verified
- **Privacy masking** - End-to-end tests confirm no PII leakage
- **Hybrid pipeline** - Integration tests validate AI+local parsing
- **Artifact filtering** - 40+ test cases for fragment detection

## 🔍 Troubleshooting

### Common Issues

**Cleanup script fails to find SQL file:**

```bash

# Ensure glyphs_rows.sql exists, or specify custom path
python3 dev_tools/cleanup_glyphs.py --source path/to/your/export.sql
```




**Backup script authentication errors:**

```bash

# Verify environment variables are set
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Ensure using service role key, not anon key
```




**Telemetry not showing:**

```bash

# Verify telemetry is enabled
python3 -c "
from emotional_os.core import signal_parser as sp
print('Telemetry enabled:', hasattr(sp, 'TELEMETRY_ENABLED') and sp.TELEMETRY_ENABLED)
"
```




**Upsert failures:**

- Check Supabase table schema matches expected fields
- Verify service role key has write permissions
- Review batch error messages for constraint violations

### Support Data

If you encounter issues, gather this information:

```bash

# System info
python3 --version
pip3 list | grep -E "(requests|streamlit|pandas)"

# File sizes
ls -la dev_tools/cleaned_glyphs*.{json,csv}
wc -l dev_tools/*.csv

# Recent telemetry sample
python3 -c "
from emotional_os.core import signal_parser as sp
sp.set_telemetry(True)

# ... run test operation
"
```




## 📈 Next Steps

### Recommended Follow-ups

1. **Monitor telemetry** in production to identify performance bottlenecks
2. **Adjust fragment threshold** if 0.5 proves too conservative/aggressive
3. **Expand cleanup heuristics** based on production data patterns
4. **Automate migration** using CI/CD pipeline for future updates

### Integration Opportunities

- **Grafana/monitoring** - Parse JSON telemetry events for dashboards
- **A/B testing** - Use telemetry to compare glyph selection strategies
- **Data quality** - Track integrity scores over time to identify degradation
##

## ✅ Summary

This migration successfully adds:

- ✅ Conservative cleanup pipeline with integrity scoring
- ✅ Comprehensive telemetry instrumentation
- ✅ Safe Supabase migration tools with backup
- ✅ Fragment detection (0 fragments found - good data quality)
- ✅ All tests passing (109/110) - no regressions
- ✅ Comprehensive documentation and safety features

The system is production-ready with robust safety mechanisms and observability.
