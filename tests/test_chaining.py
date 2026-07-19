"""Test tool chaining limits."""

import pytest
from jarvis.tools.chaining import ChainPlan, build_chain, execute_chain
from jarvis.tools.registry import register, execute
from jarvis.tools.base import Tool


class _OkTool(Tool):
    def __init__(self):
        super().__init__("ok_tool", "Always succeeds")
    def execute(self, **kwargs):
        return {"status": "done"}


class TestChaining:
    def setup_method(self):
        register(_OkTool())

    def test_build_chain_from_calls(self):
        calls = [("ok_tool", {})]
        chain = build_chain(calls, "do something")
        assert chain is not None
        assert chain.total_steps == 1

    def test_empty_calls(self):
        assert build_chain([], "hi") is None

    def test_chain_summary(self):
        calls = [("ok_tool", {}), ("ok_tool", {})]
        chain = build_chain(calls, "do two things")
        summary = execute_chain(chain, execute)
        assert "Completed all steps" in summary

    def test_chain_step_limit(self, monkeypatch):
        monkeypatch.setattr("jarvis.tools.chaining.MAX_CHAIN_STEPS", 2)
        calls = [("ok_tool", {}) for _ in range(5)]
        chain = build_chain(calls, "too many steps")
        summary = execute_chain(chain, execute)
        assert "max" in summary.lower()
        assert chain.failed
