#!/usr/bin/env python3
"""Ingest a conversation text file and feed it to the local lexicon learner.

This script uses a conservative block-splitting heuristic to separate human
utterances from assistant responses and then calls learn_from_conversation_data
to update the learned lexicon and pattern history.

Usage: python3 scripts/ingest_conversation.py 
"""
from learning.lexicon_learner import learn_from_conversation_data, get_learning_insights
import json
import re
import sys
from pathlib import Path

# Ensure repo root is on PYTHONPATH so local modules can be imported
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# Also ensure current working directory is on path (helpful when script is run from repo root)
sys.path.insert(0, str(Path.cwd()))


CONVERSATION_PATH = Path(
    "emotional_os/deploy/Conversation archives - User Returns To Chat.txt")
OUT_DIR = Path("learning/imported_conversations")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def split_into_blocks(text: str):
    # Split on two or more newlines to get conversational blocks
    raw_blocks = re.split(r"\n\s*\n", text.strip())
    blocks = [b.strip() for b in raw_blocks if b.strip()]
    return blocks


def is_human_block(block: str) -> bool:
    """Heuristic to decide whether a block is a human (user/ex) message.

    Conservative rules:
    - If block begins with short first-person sentences (I, My, Me) treat as human
    - If it contains markers such as 'Her reply', 'My reply', 'He said', 'She said', treat as human
    - If it appears to be an analysis (contains 'Let', 'This exchange', '⚡', '🔌', 'Would you like') treat as assistant
    """
    head = block.splitlines()[0].strip()
    # markers that strongly imply assistant text
    assistant_markers = ["let ", "this exchange",
                         "would you like", "i can help", "🔌", "⚡", "metaphor"]
    lower = block.lower()
    if any(m in lower for m in assistant_markers):
        return False

    # markers that imply human utterance
    human_markers = ["her reply", "my reply", "i said", "i need",
                     "i found", "my reply:", "i offered", "her replies:", "her reply:"]
    if any(m in lower for m in human_markers):
        return True

    if head.lower().startswith(("i ", "my ", "me ", "we ", "our ", "you ")):
        # likely human
        return True

    # default to assistant for long analytical paragraphs
    if len(block.split()) > 40:
        return False

    # else treat as human
    return True


def build_messages(blocks):
    messages = []
    # We'll label human blocks as 'user' and assistant blocks as 'system'
    for b in blocks:
        role = 'user' if is_human_block(b) else 'system'
        # collapse internal newlines
        content = " ".join([line.strip()
                           for line in b.splitlines() if line.strip()])
        messages.append({'type': role, 'content': content})
    return messages


def main():
    if not CONVERSATION_PATH.exists():
        print(f"Conversation file not found: {CONVERSATION_PATH}")
        return 1

    text = CONVERSATION_PATH.read_text(encoding='utf-8')
    blocks = split_into_blocks(text)
    messages = build_messages(blocks)

    convo = {'source': str(CONVERSATION_PATH), 'messages': messages}

    # Save parsed conversation for inspection
    parsed_path = OUT_DIR / 'parsed_conversation.json'
    parsed_path.write_text(json.dumps(
        convo, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Parsed conversation saved to {parsed_path}")

    # Run learner
    learning_results = learn_from_conversation_data(convo)

    # Save learning results
    results_path = OUT_DIR / 'learning_results.json'
    results_path.write_text(json.dumps(
        learning_results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Learning results written to {results_path}")

    # Print concise insights
    insights = get_learning_insights()
    print("Learning insights:")
    print(json.dumps(insights, indent=2))

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
