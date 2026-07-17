import json
import os
from config import MEMORY_DIR, MAX_MEMORY_LINES

_FILE = os.path.join(MEMORY_DIR, "conversations.json")


def load():
    if not os.path.exists(_FILE):
        return []
    with open(_FILE, "r") as f:
        return json.load(f)


def save(log):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    with open(_FILE, "w") as f:
        json.dump(log, f, indent=2)


def add_entry(user_text, assistant_text):
    log = load()
    log.append({"user": user_text, "assistant": assistant_text})
    if len(log) > MAX_MEMORY_LINES:
        log = log[-MAX_MEMORY_LINES:]
    save(log)


def clear():
    save([])
