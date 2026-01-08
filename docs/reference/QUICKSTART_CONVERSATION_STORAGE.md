# Quick Start: Persistent Conversation Storage

## What's New ✨

Your conversations now **automatically save** and **persist across page refreshes**. Just like
Microsoft Copilot!

## Getting Started

### 1. Deploy the Database Schema

Run this SQL in your Supabase dashboard:

**Path**: `sql/conversations_table.sql`

1. Go to Supabase Console → **SQL Editor** 2. Click **New Query** 3. Copy the entire contents of
`sql/conversations_table.sql` 4. Paste it and click **Run**

This creates:

- `conversations` table (stores your full conversations)
- `conversation_metadata` table (tracks changes)
- Automatic timestamp updates

### 2. Verify Your Supabase Configuration

Make sure `.streamlit/secrets.toml` has:

```toml
[supabase]
url = "https://your-project.supabase.co"
```text

```text
```


### 3. Restart Your App

```bash

```text

```

## Using the New Features

### Sidebar Conversation List

On the left sidebar, you'll see:

```

📚 Previous Conversations
├── 💬 "Feeling anxious about work"    ← Click to load
│   ├── ✏️                             ← Click to rename
│   └── 🗑️                             ← Click to delete
├── 💬 "Weekend plans"

```text
```text

```

### Saving Conversations

Check the **"💾 Save my chats"** box in the sidebar to:

- ✅ Automatically save all conversations
- ✅ Persist across page refreshes
- ✅ Remember this preference next time you log in

### Auto-Naming

When you start a new conversation, the first message is used to auto-generate a title:

```


You: "I've been feeling really overwhelmed lately" ↓

```text
```


You can rename it anytime by clicking ✏️

## Key Behaviors

| Action | Result |
|--------|--------|
| Type first message | Auto-named conversation |
| Continue chatting | Messages keep accumulating |
| Refresh browser | Conversation preserved! |
| Click other convo | Switch conversations |
| Click ➕ New | Start blank conversation |
| Turn OFF toggle | Only local storage (session-only) |

## Data Structure

Each conversation stores:

- All messages (user + assistant)
- Processing time
- Mode used (hybrid/ai/local)
- Timestamps
- Emotional context (for future features)

Example:

```json
{
  "id": "abc123...",
  "title": "Work anxiety",
  "messages": [
    {
      "user": "I'm feeling anxious",
      "assistant": "Tell me more...",
      "processing_time": "0.45s",
      "mode": "hybrid",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
```text

```text
```


## Troubleshooting

### Q: Sidebar not showing previous conversations?

**A:**

1. Check "💾 Save my chats" is toggled ON 2. Refresh the page 3. Wait a moment for sidebar to load

### Q: Conversations disappeared after refresh?

**A:**

1. Make sure "💾 Save my chats" is checked 2. Verify Supabase credentials in secrets.toml 3. Check
browser console (F12) for errors 4. Verify `sql/conversations_table.sql` was run

### Q: Auto-name shows "New Conversation" instead of smart title?

**A:**

1. Make sure first message is not empty 2. Try restarting the app 3. Check logs for NLP errors

### Q: Can I rename a conversation?

**A:** Yes! Click the ✏️ pencil icon next to any conversation in the sidebar.

### Q: Can I delete a conversation?

**A:** Yes! Click the 🗑️ trash icon. This is permanent.

## For Developers

### Testing the Feature

```bash


# 1. Create test user

# 2. Start conversation, check "Save my chats"

# 3. Send a message

# 4. Refresh page (F5)

# 5. Verify conversation appears in sidebar

# Check Supabase:

```text

```

### Monitoring

Check Supabase dashboard:

- **Conversations table** → See all saved conversations
- **Conversation metadata** → Audit trail of changes

### API Usage

```python

from emotional_os.deploy.modules.conversation_manager import ConversationManager

manager = ConversationManager(user_id="user123")

# List all conversations
convs = manager.load_conversations() print(convs)

# Load specific conversation
conv = manager.load_conversation("conv-uuid") print(conv['messages'])

# Rename
success, msg = manager.rename_conversation("conv-uuid", "New Title")

# Delete

```text
```text

```

## Documentation

For more details, see:

- **`CONVERSATION_STORAGE.md`** - Complete setup & API guide
- **`IMPLEMENTATION_SUMMARY.md`** - Technical architecture
- **`sql/conversations_table.sql`** - Database schema

## Commit Reference

These features are in commit `4b1c501`:

```


feat: implement persistent conversation storage with auto-naming

- ConversationManager for Supabase persistence
- Auto-naming from first message
- Sidebar with load/rename/delete
- Database schema with metadata
- Integrated into UI

```

## What Changed

### New Files

- `emotional_os/deploy/modules/conversation_manager.py` - Main implementation
- `sql/conversations_table.sql` - Database schema
- `CONVERSATION_STORAGE.md` - Setup guide
- `IMPLEMENTATION_SUMMARY.md` - Architecture

### Modified Files

- `emotional_os/deploy/modules/ui.py` - Added sidebar, persistence

## Next Steps

1. ✅ Run `sql/conversations_table.sql` in Supabase
2. ✅ Restart your app
3. ✅ Check "Save my chats" in sidebar
4. ✅ Start a conversation
5. ✅ Refresh browser
6. ✅ See your conversation preserved!

Enjoy your persistent conversations! 🎉
