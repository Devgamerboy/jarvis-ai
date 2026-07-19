"""Test registry behavior."""

import pytest
from jarvis.tools.base import Tool
from jarvis.tools.registry import register, get, list_all, execute, list_by_category


class _DummyTool(Tool):
    def __init__(self):
        super().__init__("dummy", "A test tool", category="Tests")

    def execute(self, **kwargs) -> dict:
        return {"result": "ok"}


class TestRegistry:
    def test_register_and_get(self):
        tool = _DummyTool()
        register(tool)
        assert get("dummy") is tool

    def test_get_unknown(self):
        assert get("nope") is None

    def test_list_all(self):
        register(_DummyTool())
        specs = list_all()
        assert len(specs) == 1
        assert specs[0]["name"] == "dummy"

    def test_execute_unknown(self):
        result = execute("nope")
        assert result["success"] is False
        assert "Unknown" in result["error"]

    def test_execute_success(self):
        register(_DummyTool())
        result = execute("dummy")
        assert result["success"] is True
        assert result["result"]["result"] == "ok"

    def test_execute_raises_exception(self):
        class _BrokenTool(Tool):
            def __init__(self):
                super().__init__("broken", "Broken tool")
            def execute(self, **kwargs):
                raise ValueError("something broke")

        register(_BrokenTool())
        result = execute("broken")
        assert result["success"] is False
        assert "something broke" in result["error"]

    def test_list_by_category(self):
        register(_DummyTool())
        cats = list_by_category()
        assert "Tests" in cats
        assert cats["Tests"][0]["name"] == "dummy"
