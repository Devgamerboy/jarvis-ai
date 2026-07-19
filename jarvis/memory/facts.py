"""User facts — lightweight key-value storage for preferences, names, and projects."""

import json
import os
from typing import Any

from ..config import MEMORY_DIR

_FACTS_FILE = os.path.join(MEMORY_DIR, "facts.json")


def _ensure():
    os.makedirs(MEMORY_DIR, exist_ok=True)


def load() -> dict:
    _ensure()
    if not os.path.isfile(_FACTS_FILE):
        return {}
    try:
        with open(_FACTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save(data: dict):
    _ensure()
    with open(_FACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def set_fact(key: str, value: Any):
    data = load()
    if value is None:
        data.pop(key, None)
    else:
        data[key] = value
    save(data)


def get_fact(key: str, default: Any = None) -> Any:
    return load().get(key, default)


def get_all() -> dict:
    return load()


def list_categories() -> dict:
    """Group stored facts by prefix category for better readability."""
    data = load()
    groups: dict[str, dict] = {}
    for k, v in data.items():
        cat = k.split("_")[0] if "_" in k else "general"
        groups.setdefault(cat, {})[k] = v
    return groups
