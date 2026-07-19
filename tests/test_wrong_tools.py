"""Test that wrong tool calls are rejected."""

from jarvis.main import _validate_tool_call


class TestWrongTools:
    def test_weather_not_triggered_by_greeting(self):
        assert _validate_tool_call("hi", "weather") is False

    def test_file_tool_not_triggered_by_weather_question(self):
        assert _validate_tool_call("what is the temperature", "read_file") is False

    def test_search_not_triggered_by_system_question(self):
        assert _validate_tool_call("how much ram", "web_search") is False

    def test_correct_tool_is_allowed(self):
        assert _validate_tool_call("search the web for python", "web_search") is True

    def test_unknown_tool_keywords_return_empty(self):
        assert _validate_tool_call("do something", "nonexistent_tool") is False
