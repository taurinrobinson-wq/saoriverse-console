# Emotional OS - Privacy-Preserving Emotional Intelligence System

A revolutionary emotional processing system that combines privacy-first glyph encryption with AI-enhanced conversational capabilities.

## 🌟 Features

- **Privacy-First Architecture**: Emotional content converted to symbolic glyphs for security
- **Hybrid Processing**: Choose between local-only, AI-enhanced, or intelligent hybrid modes
- **Rich Emotional Taxonomy**: Sophisticated emotional tag system with persona selection
- **Conversational Interface**: Modern chat-like UI with conversation management
- **Secure AI Integration**: Supabase edge function integration with encrypted processing
- **Learning System**: Pattern recognition without compromising user privacy

## 🚀 Quick Start

### Local Mode (No Setup Required)
```bash
pip install streamlit requests
streamlit run emotional_os_ui_v2.py
```
Select "Local" mode in the sidebar for privacy-first processing.

### AI-Enhanced Mode (Supabase Integration)
1. Copy `.env.example` to `.env`
2. Add your Supabase credentials
3. Select "Hybrid" or "Supabase" mode in the sidebar

## 🔧 Configuration

See [SETUP.md](SETUP.md) for detailed configuration instructions.

## 🏗️ Architecture

- **Frontend**: Streamlit chat interface
- **Processing Engine**: Glyph-based emotional pattern recognition
- **Backend**: Optional Supabase integration with edge functions
- **Privacy Layer**: Symbolic encryption of emotional content
- **AI Enhancement**: OpenAI integration via privacy-preserving edge function

## 📁 Project Structure

```
Emotional OS/
├── emotional_os_ui_v2.py          # Main Streamlit interface
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