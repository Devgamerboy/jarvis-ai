"""Test notes tool."""

import pytest
from jarvis.tools.notes_tool import (
    CreateNoteTool,
    ListNotesTool,
    ReadNoteTool,
    UpdateNoteTool,
    DeleteNoteTool,
    SearchNotesTool,
)


@pytest.fixture
def notes(tmp_path, monkeypatch):
    monkeypatch.setattr("jarvis.tools.notes_tool.NOTES_DIR", str(tmp_path / "notes"))
    return {
        "create": CreateNoteTool(),
        "list": ListNotesTool(),
        "read": ReadNoteTool(),
        "update": UpdateNoteTool(),
        "delete": DeleteNoteTool(),
        "search": SearchNotesTool(),
    }


class TestNotes:
    def test_create_and_list(self, notes):
        r = notes["create"].execute(title="Test Note", content="Hello")
        assert r.get("message", "")
        r = notes["list"].execute()
        assert "Test Note" in r["notes"]

    def test_create_duplicate(self, notes):
        notes["create"].execute(title="Test", content="A")
        r = notes["create"].execute(title="Test", content="B")
        assert "already exists" in r.get("error", "")

    def test_read(self, notes):
        notes["create"].execute(title="My Note", content="Some content")
        r = notes["read"].execute(title="My Note")
        assert r["content"] == "Some content"

    def test_read_not_found(self, notes):
        r = notes["read"].execute(title="Nope")
        assert "not found" in r.get("error", "")

    def test_update(self, notes):
        notes["create"].execute(title="Updatable", content="Old")
        r = notes["update"].execute(title="Updatable", content="New")
        assert "updated" in r.get("message", "")
        r = notes["read"].execute(title="Updatable")
        assert r["content"] == "New"

    def test_delete(self, notes):
        notes["create"].execute(title="Delete Me", content="Bye")
        r = notes["delete"].execute(title="Delete Me")
        assert "deleted" in r.get("message", "")
        r = notes["list"].execute()
        assert "Delete Me" not in r["notes"]

    def test_search(self, notes):
        notes["create"].execute(title="Alpha", content="apple banana")
        notes["create"].execute(title="Beta", content="banana cherry")
        r = notes["search"].execute(keyword="banana")
        assert r["count"] >= 2
