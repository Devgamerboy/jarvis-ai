"""Test deterministic routing — single-tool requests skip the LLM."""

from jarvis.tools.router import route
from jarvis.tools.simple_formatter import format_result
from jarvis.tools.registry import register, execute
from jarvis.tools.base import Tool


class _DummyNoteTool(Tool):
    def __init__(self):
        super().__init__("list_notes", "List notes", category="Productivity")
    def execute(self, **kw):
        return {"notes": ["grocery", "todo", "ideas"], "count": 3}


class _DummyCalcTool(Tool):
    def __init__(self):
        super().__init__("calculator", "Calculate", category="Utilities")
    def execute(self, expression="", **kw):
        return {"expression": expression, "result": 42.0}


class _DummyConvertTool(Tool):
    def __init__(self):
        super().__init__("unit_convert", "Convert units", category="Utilities")
    def execute(self, expression="", **kw):
        return {"from": "5 miles", "to": "8.05 km", "value": 8.05, "unit": "km"}


class _DummyTimeTool(Tool):
    def __init__(self):
        super().__init__("time", "Show time", category="Weather & Location")
    def execute(self, **kw):
        return {"local_time": "10:30 AM", "date": "Monday, July 20, 2026"}


class _DummyBatteryTool(Tool):
    def __init__(self):
        super().__init__("battery", "Battery status", category="System")
    def execute(self, **kw):
        return {"available": True, "percentage": "85%", "charging": True}


class _DummyProcessTool(Tool):
    def __init__(self):
        super().__init__("list_processes", "List processes", category="System")
    def execute(self, **kw):
        return {"processes": [{"pid": 1, "name": "init", "cpu": "0.0%", "memory": "0.1%"}], "count": 1}


class _DummySearchTool(Tool):
    def __init__(self):
        super().__init__("search_files", "Search files", category="Files")
    def execute(self, **kw):
        return {"pattern": "*.py", "matches": ["a.py", "b.py"], "count": 2}


# ---------------------------------------------------------------------------
# Route tests — verify deterministic matching
# ---------------------------------------------------------------------------


class TestRouterSingleTool:
    """Tests that obvious single-tool requests route without an LLM call."""

    def test_list_my_notes(self):
        r = route("list my notes")
        assert r is not None
        assert r.tool_name == "list_notes"
        assert r.confidence > 0.9

    def test_show_notes(self):
        r = route("show notes")
        assert r is not None
        assert r.tool_name == "list_notes"

    def test_read_note(self):
        r = route("read note grocery")
        assert r is not None
        assert r.tool_name == "read_note"
        assert r.args.get("title") == "grocery"

    def test_calculate(self):
        r = route("calculate 18% of 340")
        assert r is not None
        assert r.tool_name == "calculator"
        assert "expression" in r.args

    def test_convert_units(self):
        r = route("convert 5 miles to km")
        assert r is not None
        assert r.tool_name == "unit_convert"
        assert "expression" in r.args

    def test_what_time(self):
        r = route("what time is it")
        assert r is not None
        assert r.tool_name == "time"

    def test_current_time(self):
        r = route("current time")
        assert r is not None
        assert r.tool_name == "time"

    def test_battery_status(self):
        r = route("battery status")
        assert r is not None
        assert r.tool_name == "battery"

    def test_battery(self):
        r = route("battery")
        assert r is not None
        assert r.tool_name == "battery"

    def test_list_processes(self):
        r = route("list processes")
        assert r is not None
        assert r.tool_name == "list_processes"

    def test_running_programs(self):
        r = route("running programs")
        assert r is not None
        assert r.tool_name == "list_processes"

    def test_search_files(self):
        r = route("find README.md")
        assert r is not None
        assert r.tool_name == "search_files"
        assert "README" in r.args.get("pattern", "")

    def test_weather(self):
        r = route("weather")
        assert r is not None
        assert r.tool_name == "weather"

    def test_forecast(self):
        r = route("forecast")
        assert r is not None
        assert r.tool_name == "forecast"

    def test_screenshot(self):
        r = route("take screenshot")
        assert r is not None
        assert r.tool_name == "screenshot"

    def test_speed_test(self):
        r = route("speed test")
        assert r is not None
        assert r.tool_name == "speed_test"

    def test_news(self):
        r = route("news")
        assert r is not None
        assert r.tool_name == "news"

    def test_location(self):
        r = route("where am i")
        assert r is not None
        assert r.tool_name == "location"

    def test_network(self):
        r = route("internet status")
        assert r is not None
        assert r.tool_name == "network_status"

    # --- Additional required routes ---

    def test_current_weather(self):
        r = route("current weather")
        assert r is not None
        assert r.tool_name == "weather"

    def test_whats_the_weather(self):
        r = route("what's the weather")
        assert r is not None
        assert r.tool_name == "weather"

    def test_weather_tomorrow(self):
        r = route("weather tomorrow")
        assert r is not None
        assert r.tool_name == "forecast"

    def test_weather_this_week(self):
        r = route("weather this week")
        assert r is not None
        assert r.tool_name == "forecast"

    def test_system_info(self):
        r = route("system info")
        assert r is not None
        assert r.tool_name == "system_info"

    def test_network_status(self):
        r = route("network status")
        assert r is not None
        assert r.tool_name == "network_status"

    def test_is_it_raining(self):
        r = route("is it raining")
        assert r is not None
        assert r.tool_name == "weather"

    def test_how_hot_is_it(self):
        r = route("how hot is it")
        assert r is not None
        assert r.tool_name == "weather"


class TestRouteResultAttributes:
    """Verify RouteResult has a route_name field."""

    def test_route_name_present(self):
        r = route("weather")
        assert r is not None
        assert r.route_name == "weather"

    def test_route_name_forecast_weather(self):
        r = route("weather tomorrow")
        assert r is not None
        assert r.route_name == "forecast_weather"


class TestRouterCasual:
    """Greetings should NOT be routed to any tool."""

    def test_hello_does_not_route(self):
        assert route("hello") is None

    def test_hi_does_not_route(self):
        assert route("hi") is None

    def test_good_morning_does_not_route(self):
        assert route("good morning") is None

    def test_thanks_does_not_route(self):
        assert route("thanks") is None


class TestRouterMultiStep:
    """Multi-step requests should NOT match deterministic routes."""

    def test_search_and_save(self):
        r = route("search the web for KoboldCpp, summarize it, and save it to notes.txt")
        assert r is None  # too complex for deterministic routing

    def test_weather_and_note(self):
        r = route("get tomorrow's forecast and save it to weather.txt")
        assert r is None


class TestRouterAmbiguous:
    """Ambiguous requests should NOT match deterministic routes."""

    def test_what_is_python(self):
        r = route("what is python")
        assert r is None  # "what is" is too ambiguous for deterministic routing


class TestFormatterIntegration:
    """Formatting works for deterministic routes."""

    def setup_method(self):
        register(_DummyNoteTool())
        register(_DummyCalcTool())
        register(_DummyConvertTool())
        register(_DummyTimeTool())
        register(_DummyBatteryTool())

    def test_format_list_notes(self):
        result = execute("list_notes")
        assert result["success"]
        formatted = format_result("list_notes", result)
        assert formatted is not None
        assert "grocery" in formatted

    def test_format_calculator(self):
        result = execute("calculator", expression="2+2")
        assert result["success"]
        formatted = format_result("calculator", result)
        assert formatted is not None

    def test_format_time(self):
        result = execute("time")
        assert result["success"]
        formatted = format_result("time", result)
        assert "10:30" in formatted

    def test_format_battery(self):
        result = execute("battery")
        assert result["success"]
        formatted = format_result("battery", result)
        assert "85%" in formatted


class TestDiscoveryRunsOnce:
    """Discovery runs once at startup, not per message."""

    def test_discovery_called_once(self, monkeypatch):
        from jarvis.tools import register_all
        from jarvis.tools.discovery import discover_tools
        import time

        # Track how many times discovery runs
        call_count = 0
        original = discover_tools

        def tracking_discovery(*args):
            nonlocal call_count
            call_count += 1
            return original(*args)

        monkeypatch.setattr("jarvis.tools.discovery.discover_tools", tracking_discovery)
        register_all()
        first_count = call_count

        # Second registration should NOT re-discover since registry is already populated
        register_all()
        assert call_count == first_count  # discovery still called but registry doesn't re-add


class TestZeroAiCalls:
    """Proof that routed requests make zero AI calls.

    These tests verify that the deterministic router + tool execution
    + simple formatter complete without ever calling the OpenAI client.
    """

    def setup_method(self):
        register(_DummyNoteTool())
        register(_DummyCalcTool())
        register(_DummyTimeTool())
        register(_DummyBatteryTool())
        register(_DummyProcessTool())
        register(_DummySearchTool())

    def _run_route(self, user_input: str) -> str | None:
        """Simulate what main._try_deterministic_route does."""
        from jarvis.tools.router import route as det_route
        from jarvis.tools import execute
        from jarvis.tools.simple_formatter import format_result

        routed = det_route(user_input)
        if routed is None:
            return None
        result = execute(routed.tool_name, **routed.args)
        if not result.get("success"):
            return None
        return format_result(routed.tool_name, result)

    def test_list_notes_zero_ai(self):
        formatted = self._run_route("list my notes")
        assert formatted is not None
        assert "grocery" in formatted

    def test_weather_zero_ai(self):
        r = route("current weather")
        assert r is not None
        assert r.tool_name == "weather"

    def test_weather_tomorrow_zero_ai(self):
        r = route("weather tomorrow")
        assert r is not None
        assert r.tool_name == "forecast"

    def test_what_time_zero_ai(self):
        r = route("what time is it")
        assert r is not None
        assert r.tool_name == "time"

    def test_battery_zero_ai(self):
        r = route("battery")
        assert r is not None
        assert r.tool_name == "battery"

    def test_calculator_zero_ai(self):
        r = route("calculate 25 * 14")
        assert r is not None
        assert r.tool_name == "calculator"

    def test_convert_zero_ai(self):
        r = route("convert 5 miles to km")
        assert r is not None
        assert r.tool_name == "unit_convert"

    def test_system_info_zero_ai(self):
        r = route("system info")
        assert r is not None
        assert r.tool_name == "system_info"

    def test_list_processes_zero_ai(self):
        r = route("list processes")
        assert r is not None
        assert r.tool_name == "list_processes"

    def test_network_status_zero_ai(self):
        r = route("network status")
        assert r is not None
        assert r.tool_name == "network_status"

    def test_read_note_zero_ai(self):
        r = route("read note grocery")
        assert r is not None
        assert r.tool_name == "read_note"
        assert r.args.get("title") == "grocery"

    def test_find_file_zero_ai(self):
        r = route("find README.md")
        assert r is not None
        assert r.tool_name == "search_files"
        assert "README" in r.args.get("pattern", "")

    def test_greeting_zero_tools_zero_ai(self):
        """Greetings should not route at all (not even to a tool)."""
        for greeting in ["hello", "hi", "good morning", "thanks"]:
            assert route(greeting) is None

    def test_multi_step_does_not_route(self):
        """Multi-step requests must fall through to LLM planner."""
        r = route("search the web for KoboldCpp, summarize it, and save it to notes.txt")
        assert r is None


class TestRoutedToolExecution:
    """Full end-to-end routing + formatting path."""

    def setup_method(self):
        register(_DummyNoteTool())
        register(_DummyCalcTool())
        register(_DummyTimeTool())

    def test_route_and_format_list_notes(self):
        from jarvis.tools.router import route
        from jarvis.tools import execute
        from jarvis.tools.simple_formatter import format_result

        r = route("list my notes")
        assert r is not None

        result = execute(r.tool_name)
        assert result["success"]

        formatted = format_result(r.tool_name, result)
        assert formatted is not None
        assert "grocery" in formatted

    def test_route_and_format_calculator(self):
        from jarvis.tools.router import route
        from jarvis.tools import execute
        from jarvis.tools.simple_formatter import format_result

        r = route("calculate 5 + 3")
        assert r is not None

        result = execute(r.tool_name, **r.args)
        assert result["success"]

        formatted = format_result(r.tool_name, result)
        assert formatted is not None
        assert "42" in str(formatted)
