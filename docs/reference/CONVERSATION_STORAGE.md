# Conversation Storage Implementation Guide

This document describes the new persistent conversation storage system for FirstPerson.

## Overview

The system now supports:

1. **Persistent Conversation Storage** - Conversations are saved to Supabase/database 2.
**Auto-Naming** - Conversations are automatically named based on first message context 3.
**Conversation Sidebar** - Previous conversations listed and selectable in sidebar 4.
**Rename/Delete** - Users can rename or delete conversations 5. **Session Persistence** -
Preferences like "Save my chats" are remembered across sessions

## Architecture

### Components

1. **`emotional_os/deploy/modules/conversation_manager.py`**
   - `ConversationManager` class - Handles all database operations
   - `generate_auto_name()` - Creates conversation titles from first message
   - `load_all_conversations_to_sidebar()` - Renders sidebar conversation list

2. **`emotional_os/deploy/modules/ui.py`** (modified)
   - Integrated conversation manager initialization
   - Added sidebar with conversation list and controls
   - Modified persistence logic to use conversation manager

3. **`sql/conversations_table.sql`** (new)
   - Schema for `conversations` table with full message storage
   - Schema for `conversation_metadata` table for audit trail
   - Automatic `updated_at` timestamp management

4. **Database Requirements**
   - Supabase with REST API enabled
   - API key configured in `st.secrets`

## Setup Instructions

### 1. Deploy Database Schema

Run the SQL migration in Supabase:

```bash

# Option A: Via Supabase Dashboard

# 1. Go to Supabase Console → SQL Editor

# 2. Create new query

# 3. Copy and run sql/conversations_table.sql

# Option B: Via Supabase CLI (if installed)
```text
```text
```

The schema creates:

- `conversations` table - stores full conversations with metadata
- `conversation_metadata` table - audit trail of changes
- Automatic triggers for timestamp management

### 2. Verify Configuration

Ensure `st.secrets` contains Supabase credentials:

```yaml


# .streamlit/secrets.toml
[supabase]
url = "https://your-project.supabase.co"

```text
```

### 3. Run the Application

```bash
```text
```text
```

## Features

### Auto-Naming

Conversations are automatically named from the first message:

```python

from emotional_os.deploy.modules.conversation_manager import generate_auto_name

# Example
title = generate_auto_name("I've been feeling anxious about work")

```text
```

### Managing Conversations

In the sidebar:

- 📚 **Previous Conversations** - Lists all saved conversations
- 💬 - Click to load a conversation
- ✏️ - Rename a conversation
- 🗑️ - Delete a conversation
- ➕ **New Conversation** - Start fresh conversation
- 💾 **Save my chats** - Toggle persistence (checkbox)

### Direct API Usage

```python
from emotional_os.deploy.modules.conversation_manager import ConversationManager

manager = ConversationManager(user_id="user123")

# Load all conversations
conversations = manager.load_conversations()

# Load specific conversation
conv = manager.load_conversation("conv-id-123")

# Save conversation
success, msg = manager.save_conversation(
    conversation_id="conv-id-123",
    title="Work Anxiety Discussion",
    messages=[
        {"user": "I'm anxious", "assistant": "Tell me more..."},
    ]
)

# Rename conversation
success, msg = manager.rename_conversation("conv-id-123", "New Title")

# Delete conversation
```text
```text
```

## Data Structure

### Conversation Storage Format

```json

{
  "id": "uuid",
  "user_id": "user123",
  "conversation_id": "conv-uuid",
  "title": "Work Anxiety Discussion",
  "messages": [
    {
      "user": "I feel anxious",
      "assistant": "That's understandable...",
      "processing_time": "0.45s",
      "mode": "hybrid",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "processing_mode": "hybrid",
  "message_count": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "first_message": "I feel anxious",
  "first_response": "That's understandable...",
  "emotional_context": {},
  "topics": [],
  "archived": false

```text
```

## Session State Management

Key session state variables:

- `current_conversation_id` - Active conversation UUID
- `conversation_title` - Current conversation title
- `conversation_manager` - ConversationManager instance
- `conversation_history_{user_id}` - Messages in current conversation
- `persist_history` - Boolean flag to enable/disable persistence
- `selected_conversation` - Conversation ID selected from sidebar

## Troubleshooting

### Conversations not saving

1. **Check Supabase configuration**

   ```bash
   # Verify secrets are loaded
python -c "import streamlit as st; print(st.secrets.get('supabase'))"
   ```

2. **Check network connectivity**
   - Verify Supabase is accessible
   - Check browser console for CORS errors

3. **Check database schema**
   - Verify `conversations` table exists in Supabase
   - Run `sql/conversations_table.sql` if missing

### Sidebar not showing conversations

1. **Enable persistence**: Check "Save my chats" checkbox
2. **Wait for sync**: First save may take a moment
3. **Refresh page**: `F5` to reload

### Auto-naming not working

If `generate_auto_name()` returns "New Conversation":

1. Check if first message is empty
2. Verify NLP module is available (spaCy, NLTK)
3. Check logs for errors

## Migration from Old System

To migrate existing conversation history:

```python

# This would require custom migration script

# Contact development team for migration support
```

## Performance Considerations

- Conversations are loaded on sidebar render (~50ms per request)
- Pagination recommended for users with 100+ conversations
- Consider archiving old conversations
- Message limit per conversation: ~1000 (configurable)

## Security

- All conversations are user-scoped via `user_id`
- Use Supabase Row Level Security (RLS) to enforce access control
- Supports soft-delete via `archived` flag
- Audit trail in `conversation_metadata` table

## Future Enhancements

- [ ] Conversation search/filtering in sidebar
- [ ] Bulk export of conversations
- [ ] Conversation sharing (encrypted links)
- [ ] Automatic conversation summarization
- [ ] Emotional trend analysis across conversations
- [ ] Smart conversation grouping by theme
- [ ] Conversation branching (continue from specific point)
