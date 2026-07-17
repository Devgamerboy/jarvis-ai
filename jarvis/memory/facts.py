import json
import os
from config import MEMORY_DIR

_FILE = os.path.join(MEMORY_DIR, "facts.json")


def load():
    if not os.path.exists(_FILE):
        return {}
    with open(_FILE, "r") as f:
        return json.load(f)


def save(data):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    with open(_FILE, "w") as f:
        json.dump(data, f, indent=2)


def set_fact(key, value):
    data = load()
    data[key] = value
    save(data)


def get_fact(key, default=None):
    return load().get(key, default)


def get_all():
    return load()
