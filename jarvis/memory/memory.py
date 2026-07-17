"""Conversation persistence.

Saves and loads conversation history as JSON.  The full history is
always written to disk; the context window limiting is handled by
``brain.processor.build_messages``.
"""

import json
import os
from config import MEMORY_FILE, MAX_MEMORY_LINES


def load_memory():
    """Load conversation history from disk.

    Returns:
        A list of {user, assistant} dicts, or an empty list.
    """
    if not os.path.exists(MEMORY_FILE):
        return []

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(conversation_log):
    """Write the full conversation log to disk."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(conversation_log, f, indent=2)


def add_entry(user_text, assistant_text):
    """Append a single exchange and persist.

    Trims the log to ``MAX_MEMORY_LINES`` entries if it exceeds
    the configured limit.
    """
    log = load_memory()
    log.append({"user": user_text, "assistant": assistant_text})

    if len(log) > MAX_MEMORY_LINES:
        log = log[-MAX_MEMORY_LINES:]

    save_memory(log)
