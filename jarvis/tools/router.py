"""Deterministic tool router — matches user input to tools before calling the LLM.

Reduces latency for obvious single-tool requests by skipping LLM planning entirely.
"""

import re
from typing import NamedTuple


class RouteResult(NamedTuple):
    """Result of deterministic routing."""

    tool_name: str
    args: dict
    confidence: float  # 0.0–1.0
    route_name: str = ""


_PATTERNS: list[tuple[re.Pattern, str, callable, float, str]] = []


def _register(pattern: str, tool_name: str, arg_extractor: callable,
              confidence: float = 0.95, route_name: str = ""):
    _PATTERNS.append((
        re.compile(pattern, re.IGNORECASE),
        tool_name,
        arg_extractor,
        confidence,
        route_name or tool_name,
    ))


def _exact(text: str) -> dict:
    return {}


def _capture_to_arg(arg_name: str = "expression"):
    def extract(m: re.Match) -> dict:
        return {arg_name: m.group(1).strip()}
    return extract


def _capture_to_title(m: re.Match) -> dict:
    return {"title": m.group(1).strip()}


# ---------------------------------------------------------------------------
# Pattern registration — priority order (first match wins)
# ---------------------------------------------------------------------------

# Time
_register(r'^what\s+time\s+(is\s+it\s*)?(\?)?$', 'time', _exact, 0.98, 'time')
_register(r'^current\s+time\s*(\?)?$', 'time', _exact, 0.98, 'time')
_register(r'^what(\'s| is)\s+the\s+(date|time)\s*(\?)?$', 'time', _exact, 0.95, 'time')
_register(r'^what\s+day\s+(is\s+it\s*)?(\?)?$', 'time', _exact, 0.95, 'time')

# Battery
_register(r'^(battery|battery\s+status|battery\s+level|battery\s+percentage)\s*(\?)?$',
          'battery', _exact, 0.99, 'battery')

# System info
_register(r'^(system\s+info|system\s+information|computer\s+specs?|hardware\s+info)\s*(\?)?$',
          'system_info', _exact, 0.98, 'system_info')

# Weather — handle "weather", "current weather", "what's the weather"
_register(r'^((current\s+)?weather|what(\'s| is)\s+the\s+weather|what(\'s| is)\s+it\s+like\s+outside)\s*(\?)?$',
          'weather', _exact, 0.98, 'weather')
_register(r'^(is\s+it\s+(hot|cold|raining|rainy|sunny|warm|cool|windy|cloudy)|how\s+(hot|cold|warm)\s+is\s+it)\s*(\?)?$',
          'weather', _exact, 0.90, 'weather')

# Forecast — handle "forecast", "weather tomorrow", "weather this week", "weather next <day>"
_register(r'^(forecast|weather\s+forecast|what(\'s| is)\s+the\s+forecast)\s*(\?)?$',
          'forecast', _exact, 0.98, 'forecast')
_register(r'^weather\s+(tomorrow|this\s+week|next\s+\w+|for\s+(tomorrow|this\s+week|next\s+\w+))\s*(\?)?$',
          'forecast', _exact, 0.95, 'forecast_weather')

# Location
_register(r'^(where\s+am\s+i|my\s+location|what(\'s| is)\s+my\s+location|what\s+city|what\s+country)\s*(\?)?$',
          'location', _exact, 0.98, 'location')

# Network status
_register(r'^(internet\s+(status|connectivity|up|down|working)|network\s+(status|connectivity|up|down)'
          r'|is\s+the\s+internet\s+working)\s*(\?)?$',
          'network_status', _exact, 0.95, 'network_status')

# Speed test
_register(r'^(speed\s+test|internet\s+speed\s+test|run\s+a\s+speed\s+test)\s*(\?)?$',
          'speed_test', _exact, 0.95, 'speed_test')

# Sunrise / sunset
_register(r'^(sunrise|sunset|sunrise\s+time|sunset\s+time|daylight\s+hours)\s*(\?)?$',
          'sunrise_sunset', _exact, 0.95, 'sunrise_sunset')

# Notes
_register(r'^list\s+(my\s+)?notes\s*(\?)?$', 'list_notes', _exact, 0.99, 'list_notes')
_register(r'^(show|view)\s+(my\s+)?notes\s*(\?)?$', 'list_notes', _exact, 0.99, 'list_notes')
_register(r'^read\s+note\s+(.+)$', 'read_note', _capture_to_title, 0.97, 'read_note')
_register(r'^open\s+note\s+(.+)$', 'read_note', _capture_to_title, 0.95, 'read_note')
_register(r'^create\s+note\s+(.+)$', 'create_note', _capture_to_title, 0.95, 'create_note')
_register(r'^delete\s+note\s+(.+)$', 'delete_note', _capture_to_title, 0.95, 'delete_note')
_register(r'^search\s+notes?\s+(?:for\s+)?(.+)$', 'search_notes', _capture_to_arg("keyword"), 0.95, 'search_notes')

# Calculator — arithmetic, math expressions
_register(r'^calculate\s+(.+)$', 'calculator', _capture_to_arg("expression"), 0.98, 'calculator')
_register(r'^compute\s+(.+)$', 'calculator', _capture_to_arg("expression"), 0.97, 'calculator')
_register(r'^what\s+is\s+([\d\s+\-*/%().^]+)$', 'calculator', _capture_to_arg("expression"), 0.90, 'calculator')

# Unit conversion — "convert <value> <unit> to <unit>"
_register(r'^convert\s+([\d.]+\s*\w+\s+to\s+\w+)$', 'unit_convert',
          _capture_to_arg("expression"), 0.97, 'unit_convert')

# Currency conversion (checked after unit conversion to avoid conflicts)
_register(r'^convert\s+([\d.]+\s*\w+\s+to\s+\w+)$', 'currency_convert',
          lambda m: {"expression": m.group(1)} if any(
              c in m.group(1).upper() for c in ('USD', 'EUR', 'GBP', 'JPY', 'CNY'))
          else None, 0.90, 'currency_convert')

# Processes
_register(r'^(list|show)\s+(running\s+)?process(es|ors)?\s*(\?)?$',
          'list_processes', _exact, 0.98, 'list_processes')
_register(r'^(running\s+)?programs?\s*(\?)?$', 'list_processes', _exact, 0.90, 'list_processes')
_register(r'^(search|find)\s+process\s+(.+)$', 'search_processes',
          _capture_to_arg("name"), 0.95, 'search_processes')
_register(r'^(terminate|kill|stop)\s+process\s+(\d+)$', 'terminate_process',
          lambda m: {"pid": int(m.group(2))}, 0.95, 'terminate_process')

# Screenshot
_register(r'^(take\s+)?screenshot\s*(\?)?$', 'screenshot', _exact, 0.98, 'screenshot')
_register(r'^capture\s+(the\s+)?screen\s*(\?)?$', 'screenshot', _exact, 0.97, 'screenshot')

# Clipboard
_register(r'^(read|show|get)\s+(the\s+)?clipboard\s*(\?)?$', 'clipboard_read', _exact, 0.98, 'clipboard_read')
_register(r'^(clear|empty)\s+(the\s+)?clipboard\s*(\?)?$', 'clipboard_clear', _exact, 0.98, 'clipboard_clear')
_register(r'^copy\s+(.+)\s+to\s+(the\s+)?clipboard\s*(\?)?$', 'clipboard_copy',
          lambda m: {"text": m.group(1).strip()}, 0.95, 'clipboard_copy')

# Search files — specific file/directory patterns match first
_register(r'^(search|find)\s+(?:for\s+)?(.+?)\s+files?\s*$', 'search_files',
          lambda m: {"pattern": m.group(2).strip()}, 0.95, 'search_files')
_register(r'^(search|find)\s+(?:for\s+)?(.+?)\s+direc(tory|tories)\s*$', 'search_files',
          lambda m: {"pattern": m.group(2).strip()}, 0.95, 'search_files')
_register(r'^(search|find)\s+(?:for\s+)?(.+?)\s+(glob|pattern)\s*$', 'search_files',
          lambda m: {"pattern": m.group(2).strip()}, 0.95, 'search_files')
# Catch-all for short file searches: "find README.md", "search for config.json"
_register(r'^(search|find)\s+(?:for\s+|files?\s+(?:named|called|matching)\s+)?(.{1,40})$',
          'search_files', lambda m: {"pattern": m.group(2).strip()}, 0.90, 'search_files')

# Open file / folder / URL
_register(r'^open\s+(folder|directory)\s+(.+)$', 'open_file',
          lambda m: {"path": m.group(2).strip()}, 0.90, 'open_file')
_register(r'^open\s+(url|website|site)\s+(.+)$', 'open_url',
          lambda m: {"url": m.group(2).strip()}, 0.90, 'open_url')
_register(r'^(launch|open|start)\s+(.+)$', 'launch_app',
          lambda m: {"app": m.group(2).strip()}, 0.80, 'launch_app')

# News
_register(r'^(news|headlines|top\s+stories|latest\s+news)\s*(\?)?$', 'news', _exact, 0.97, 'news')
_register(r'^(tech|technology)\s+news\s*(\?)?$', 'news',
          lambda _: {"topic": "technology"}, 0.95, 'news_tech')
_register(r'^(ai|artificial\s+intelligence)\s+news\s*(\?)?$', 'news',
          lambda _: {"topic": "ai"}, 0.95, 'news_ai')
_register(r'^sports\s+news\s*(\?)?$', 'news',
          lambda _: {"topic": "sports"}, 0.95, 'news_sports')


def route(user_input: str) -> RouteResult | None:
    """Try to match *user_input* to a deterministic tool route.

    Returns a ``RouteResult`` on the first matching pattern, or ``None``
    if no pattern matched.
    """
    text = user_input.strip()
    for pattern, tool_name, extractor, confidence, route_name in _PATTERNS:
        m = pattern.match(text)
        if m:
            args = extractor(m)
            if args is None:
                continue
            return RouteResult(
                tool_name=tool_name, args=args,
                confidence=confidence, route_name=route_name,
            )
    return None
