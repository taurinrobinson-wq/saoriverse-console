# Emotional OS - Privacy-Preserving Emotional Intelligence System

A revolutionary emotional processing system that combines privacy-first glyph encryption with AI-enhanced conversational capabilities.

## 🌟 Features

- **Privacy-First Architecture**: Emotional content converted to symbolic glyphs for security
- **Hybrid Processing**: Choose between local-only or an intelligent hybrid mode with AI enhancement
- **Rich Emotional Taxonomy**: Sophisticated emotional tag system with persona selection
- **Conversational Interface**: Modern chat-like UI with conversation management
- **Secure AI Integration**: Supabase edge function integration with encrypted processing
- **Learning System**: Pattern recognition without compromising user privacy

## 🚀 Quick Start

### Local Mode (No Setup Required)

```bash
pip install streamlit requests
streamlit run main_v2.py  # (ARCHIVED: emotional_os_ui_v2.py)
```

Select "Local" mode in the sidebar for privacy-first processing.

### AI-Enhanced Mode (Supabase Integration)

1. Copy `.env.example` to `.env`
2. Add your Supabase credentials
3. Select "Hybrid" or "Supabase" mode in the sidebar

## 🔧 Configuration

See [SETUP.md](SETUP.md) for detailed configuration instructions.

## 🏗️ Architecture

## Developer install (editable)

For contributors and local development you can install the repository into a virtual environment in "editable" mode. This makes the `emotional_os` package available for imports and lets you iterate without reinstalling:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

The editable install exposes the package name `saoriverse_console` and makes the `emotional_os` package importable (for example: `from emotional_os.supabase.supabase_integration import SupabaseIntegrator`).

The repo already includes a minimal `pyproject.toml` + `setup.cfg` to support this workflow.

- **Frontend**: Streamlit chat interface
- **Processing Engine**: Glyph-based emotional pattern recognition
- **Backend**: Optional Supabase integration with edge functions
- **Privacy Layer**: Symbolic encryption of emotional content
- **AI Enhancement**: OpenAI integration via privacy-preserving edge function

## 📁 Project Structure

```
Emotional OS/
├── main_v2.py  # (ARCHIVED: emotional_os_ui_v2.py)          # Main Streamlit interface
├── supabase_integration.py        # Hybrid processing system
├── emotional_tag_matcher.py       # Enhanced emotional processing
├── parser/
│   ├── signal_parser.py           # Core glyph processing
│   └── signal_lexicon.json        # Signal mapping definitions
├── learning/
│   └── lexicon_learner.py         # Learning system (no AI)
├── em_trace/
│   └── trace_engine.py            # Conversation tracing
├── saori_edge_function.ts         # Supabase edge function
├── emotional_tags_rows.sql        # Rich emotional taxonomy
├── glyphs.db                      # Local glyph database
└── .env.example                   # Configuration template
```

## 🔐 Privacy & Security

This system prioritizes user privacy through:

- **Glyph Encryption**: Personal content → abstract symbols
- **Local Processing**: Complete functionality without external calls
- **Encrypted API Calls**: Only symbolic patterns sent to AI services
- **No Raw Data Storage**: Emotional states stored as encrypted glyphs

## 🎯 Innovation

Emotional OS represents a new category of **encrypted emotional intelligence** that solves the core tension between AI capability and privacy protection.

## 📄 License

[Add your preferred license]

## 🤝 Contributing

[Add contribution guidelines if desired]

## CI & Unit Tests (Glyph-native behavior)

This repository now includes focused unit tests and a CI job that lock in core glyph-native behaviors:

- Unit tests added:
  - `tests/test_ui_template_usage.py` — ensures the UI selection rule prefers `response_template` when glyph debug is off and falls back to contextual responses when debug is on.
  - `tests/unit/test_multi_glyph_selection.py` — verifies `select_best_glyph_and_response` returns the modern quadruple and exposes `glyphs_selected` with `score` and `display_name`.
  - `tests/unit/test_display_name_normalizer.py` — asserts `_normalize_display_name` uses DB-provided `display_name`, extracts sensible fragments, and truncates long names safely.

- CI behavior:
  - A GitHub Actions workflow (`.github/workflows/ci.yml`) runs these unit tests on push and pull requests to `main`. The CI job is intentionally scoped to stable, DB-independent unit tests to provide a fast, reliable guardrail for future changes.

Running tests locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # or at least: pip install pytest
pytest -q tests/test_ui_template_usage.py tests/unit/test_multi_glyph_selection.py tests/unit/test_display_name_normalizer.py
```

If you want broader integration tests (DB fixtures, spaCy, TextBlob), I can add an optional CI job that prepares the environment; for now these unit tests anchor the symbolic behaviors we care about.

## Conversation history persistence (Supabase)

If you opt in to persist conversation history via the Streamlit sidebar, the app writes rows into a Supabase Postgres table named `conversation_history` and records deletion requests to `conversation_deletion_audit`.

Files included in this repo:

- `sql/create_conversation_history_tables.sql` — recommended DDL to create the tables and indices (includes `pgcrypto` enablement and an audit table).

Quick apply options

1) Supabase dashboard (recommended)

- Open your Supabase project → SQL editor → New query
- Paste the contents of `sql/create_conversation_history_tables.sql` and Run

2) psql using a service_role key (be careful; keep the key secret)

```bash
psql "postgresql://postgres:<SERVICE_ROLE_KEY>@<PROJECT_REF>.db.supabase.co:5432/postgres" -f sql/create_conversation_history_tables.sql
```

3) Supabase CLI

```bash
supabase db query < sql/create_conversation_history_tables.sql
```

Row-Level Security (recommended)

After creating the table, enable RLS and add policies so that only the owning user can read/delete their rows. Example (adjust `auth.uid()` to match your JWT `sub` mapping):

```sql
ALTER TABLE public.conversation_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Insert own rows" ON public.conversation_history
 FOR INSERT
 TO authenticated
 WITH CHECK (user_id::text = auth.uid());

CREATE POLICY "Select own rows" ON public.conversation_history
 FOR SELECT
 TO authenticated
 USING (user_id::text = auth.uid());

CREATE POLICY "Delete own rows" ON public.conversation_history
 FOR DELETE
 TO authenticated
 USING (user_id::text = auth.uid());
```

Deletion & audit

- The UI provides a "Clear Server History" flow that performs a best-effort delete via the Supabase REST API using `user_id = eq.<user_id>`.
- The DDL also creates a `conversation_deletion_audit` table to record deletion requests (non-content audit). Consider wiring an audit insert whenever deletion is performed.

Privacy & consent

- Persistence is opt-in and requires an explicit confirmation. The app stores message text in your Supabase project when enabled.
- Before enabling persistence, ensure you understand the privacy implications and have configured your Supabase project's RLS policies and backups appropriately.

If you want, I can:

- Wire an audit insert into the delete flow so every deletion request is recorded (no message content), or
- Add the RLS creation SQL as a separate file under `sql/` and a short admin script to apply it safely.
