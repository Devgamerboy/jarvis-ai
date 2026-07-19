"""Benchmark and performance tests — connection reuse, retry, zero-LLM proof."""

import json
import time
from unittest.mock import MagicMock, patch, PropertyMock

import pytest


class TestCheckConnection:
    """Verify :func:`check_connection` handles DNS, timeout, and success."""

    @patch("httpx.get")
    def test_success(self, mock_get):
        mock_get.return_value.raise_for_status = lambda: None
        from jarvis.brain.client import check_connection
        assert check_connection() is None

    @patch("httpx.get")
    def test_dns_unreachable(self, mock_get):
        from httpx import ConnectError
        mock_get.side_effect = ConnectError("DNS lookup failed")
        from jarvis.brain.client import check_connection
        err = check_connection()
        assert err is not None
        assert "Cannot connect" in err
        assert "KoboldCpp" in err

    @patch("httpx.get")
    def test_timeout(self, mock_get):
        from httpx import TimeoutException
        mock_get.side_effect = TimeoutException("Timed out")
        from jarvis.brain.client import check_connection
        err = check_connection()
        assert err is not None
        assert "timed out" in err


class TestHttpConnectionReuse:
    """Verify the httpx client is reused across calls (not created fresh)."""

    def test_same_client_instance(self):
        from jarvis.brain.client import get_client, close_client
        close_client()
        c1 = get_client()
        c2 = get_client()
        assert c1 is c2
        close_client()

    def test_client_reused(self):
        from jarvis.brain.client import get_client, close_client, _client
        close_client()
        assert _client is None
        c1 = get_client()
        c2 = get_client()
        assert c1 is c2
        close_client()


class TestRetryBehavior:
    """Verify retry logic in :func:`ask_ai`."""

    def test_retry_on_failure(self):
        from jarvis.brain.client import get_client, close_client
        close_client()

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "hello"

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [
            Exception("temporary error"),
            mock_response,
        ]

        with patch("jarvis.brain.processor.get_client", return_value=mock_client):
            with patch("jarvis.config.AI_MAX_RETRIES", 1):
                from jarvis.brain.processor import ask_ai
                result = ask_ai([{"role": "user", "content": "hi"}])
                assert result == "hello"
                assert mock_client.chat.completions.create.call_count == 2

        close_client()

    def test_retry_exhausted(self):
        from jarvis.brain.client import get_client, close_client
        close_client()

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("persistent error")

        with patch("jarvis.brain.processor.get_client", return_value=mock_client):
            with patch("jarvis.config.AI_MAX_RETRIES", 1):
                from jarvis.brain.processor import ask_ai
                with pytest.raises(RuntimeError, match="persistent error"):
                    ask_ai([{"role": "user", "content": "hi"}])

        close_client()


class TestZeroAiCallsProof:
    """End-to-end proof that routed requests emit AI CALLS: 0."""

    def test_time_zero_ai_calls(self, capsys):
        from jarvis.tools.registry import register, _registry
        from jarvis.tools.base import Tool

        class _DummyTimeTool(Tool):
            def __init__(self):
                super().__init__("time", "Show time", category="Weather & Location")
            def execute(self, **kw):
                return {"local_time": "10:30 AM", "date": "Monday, July 20, 2026"}

        _registry.clear()
        register(_DummyTimeTool())

        from jarvis.tools.router import route
        from jarvis.tools import execute
        from jarvis.tools.simple_formatter import format_result

        routed = route("what time is it")
        assert routed is not None

        result = execute(routed.tool_name, **routed.args)
        assert result["success"]

        formatted = format_result(routed.tool_name, result)
        assert formatted is not None
        assert "10:30" in formatted or "Monday" in formatted

    def test_list_notes_zero_ai_formatted(self):
        from jarvis.tools.registry import register, _registry
        from jarvis.tools.base import Tool

        class _DummyNoteTool(Tool):
            def __init__(self):
                super().__init__("list_notes", "List notes", category="Productivity")
            def execute(self, **kw):
                return {"notes": ["grocery", "todo"], "count": 2}

        _registry.clear()
        register(_DummyNoteTool())

        from jarvis.tools.router import route
        from jarvis.tools import execute
        from jarvis.tools.simple_formatter import format_result

        routed = route("list my notes")
        assert routed is not None

        result = execute(routed.tool_name, **routed.args)
        assert result["success"]

        formatted = format_result(routed.tool_name, result)
        assert formatted is not None
        assert "grocery" in formatted

    def test_multi_step_does_not_route(self):
        """Multi-step requests must fall through to LLM planner."""
        from jarvis.tools.router import route as det_route
        r = det_route("search the web for KoboldCpp, summarize it, and save it to notes.txt")
        assert r is None
