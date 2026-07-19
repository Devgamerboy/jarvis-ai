"""Test that greetings don't trigger tool calls."""

from jarvis.main import _is_casual, _validate_tool_call


class TestGreetings:
    def test_hello_is_casual(self):
        assert _is_casual("hello") is True

    def test_hi_is_casual(self):
        assert _is_casual("hi") is True

    def test_thanks_is_casual(self):
        assert _is_casual("thanks") is True

    def test_good_morning_is_casual(self):
        assert _is_casual("good morning") is True

    def test_weather_query_not_casual(self):
        assert _is_casual("what is the weather?") is False

    def test_greeting_rejects_tool_call(self):
        assert _validate_tool_call("hello", "weather") is False

    def test_system_query_allows_tool(self):
        assert _validate_tool_call("check my cpu", "system_info") is True
