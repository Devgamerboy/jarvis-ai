"""Notes tool — create, list, read, update, delete, and search notes."""

import json
import os
import re

from .base import Tool
from ..config import NOTES_DIR


def _sanitize(name: str) -> str:
    safe = re.sub(r'[^\w\- ]', '', name).strip()
    return safe or "untitled"


def _path(name: str) -> str:
    return os.path.join(NOTES_DIR, _sanitize(name) + ".json")


def _ensure_dir():
    os.makedirs(NOTES_DIR, exist_ok=True)


def _load(note_name: str) -> dict | None:
    p = _path(note_name)
    if not os.path.isfile(p):
        return None
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(note_name: str, data: dict):
    _ensure_dir()
    with open(_path(note_name), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _list_all() -> list[str]:
    _ensure_dir()
    files = os.listdir(NOTES_DIR)
    names = []
    for f in files:
        if f.endswith(".json"):
            names.append(f[:-5])
    return sorted(names)


class CreateNoteTool(Tool):
    def __init__(self):
        super().__init__("create_note", "Create a new note with a title and content.", category="Productivity", risk="write")

    def execute(self, title: str = "", content: str = "") -> dict:
        if not title:
            return {"error": "Note title is required."}
        safe_title = _sanitize(title)
        if _load(safe_title):
            return {"error": f"Note '{safe_title}' already exists. Use update_note to modify it."}
        _save(safe_title, {"title": safe_title, "content": content, "created": True})
        return {"title": safe_title, "message": f"Note '{safe_title}' created."}


class ListNotesTool(Tool):
    def __init__(self):
        super().__init__("list_notes", "List all saved notes.", category="Productivity")

    def execute(self) -> dict:
        notes = _list_all()
        return {"notes": notes, "count": len(notes)}


class ReadNoteTool(Tool):
    def __init__(self):
        super().__init__("read_note", "Read the content of a saved note.", category="Productivity")

    def execute(self, title: str = "") -> dict:
        if not title:
            return {"error": "Note title is required."}
        safe_title = _sanitize(title)
        data = _load(safe_title)
        if data is None:
            return {"error": f"Note '{safe_title}' not found."}
        return {"title": safe_title, "content": data.get("content", "")}


class UpdateNoteTool(Tool):
    def __init__(self):
        super().__init__("update_note", "Update the content of an existing note.", category="Productivity", risk="write")

    def execute(self, title: str = "", content: str = "") -> dict:
        if not title:
            return {"error": "Note title is required."}
        safe_title = _sanitize(title)
        if not _load(safe_title):
            return {"error": f"Note '{safe_title}' not found. Use create_note first."}
        _save(safe_title, {"title": safe_title, "content": content, "updated": True})
        return {"title": safe_title, "message": f"Note '{safe_title}' updated."}


class DeleteNoteTool(Tool):
    def __init__(self):
        super().__init__("delete_note", "Delete a saved note. Requires confirmation.", category="Productivity", risk="destructive")

    def execute(self, title: str = "") -> dict:
        if not title:
            return {"error": "Note title is required."}
        safe_title = _sanitize(title)
        p = _path(safe_title)
        if not os.path.isfile(p):
            return {"error": f"Note '{safe_title}' not found."}
        os.remove(p)
        return {"title": safe_title, "message": f"Note '{safe_title}' deleted."}


class SearchNotesTool(Tool):
    def __init__(self):
        super().__init__("search_notes", "Search notes by keyword in title or content.", category="Productivity")

    def execute(self, keyword: str = "") -> dict:
        if not keyword:
            return {"error": "Search keyword is required."}
        kw = keyword.lower()
        results = []
        for name in _list_all():
            data = _load(name)
            if data is None:
                continue
            if kw in name.lower() or kw in data.get("content", "").lower():
                results.append(name)
        return {"keyword": keyword, "matches": results, "count": len(results)}
