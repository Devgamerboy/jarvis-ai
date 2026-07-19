"""Deterministic result formatting for single-tool requests.

Returns a human-readable string without an LLM call.
"""

from datetime import datetime


def format_result(tool_name: str, result: dict) -> str | None:
    """Return a formatted string for *result* of *tool_name*, or ``None``
    if no simple formatter is available (caller falls back to LLM)."""
    formatter = _FORMATTERS.get(tool_name)
    if formatter is None:
        return None
    if not result.get("success"):
        return f"I ran into a problem: {result.get('error', 'unknown error')}"
    return formatter(result["result"])


# ---------------------------------------------------------------------------
# Individual formatters
# ---------------------------------------------------------------------------

def _fmt_time(data: dict) -> str:
    loc = f" in {data['location']}" if data.get("location") else ""
    return f"It's {data['local_time']} on {data['date']}{loc}."


def _fmt_battery(data: dict) -> str:
    if not data.get("available"):
        return data.get("message", "No battery detected.")
    parts = [f"Battery is at {data['percentage']}"]
    parts.append("(charging)" if data.get("charging") else "(on battery)")
    if data.get("remaining") and data["remaining"] != "N/A":
        parts.append(f"— {data['remaining']} remaining")
    return " ".join(parts)


def _fmt_system_info(data: dict) -> str:
    mem = data.get("memory", {})
    disk = data.get("disk", {})
    lines = [
        f"OS: {data.get('os', 'N/A')}",
        f"CPU: {data.get('cpu', 'N/A')} ({data.get('cpu_cores', '?')} cores, {data.get('cpu_usage', '?')} used)",
        f"RAM: {mem.get('used', '?')} / {mem.get('total', '?')} ({mem.get('usage', '?')})",
        f"Disk: {disk.get('used', '?')} / {disk.get('total', '?')} ({disk.get('usage', '?')})",
        f"Host: {data.get('hostname', 'N/A')} ({data.get('ip_address', 'N/A')})",
        f"Uptime: {data.get('uptime', 'N/A')}",
    ]
    return "\n".join(lines)


def _fmt_weather(data: dict) -> str:
    if "error" in data:
        return None
    return (
        f"Weather in {data.get('location', 'your area')}: "
        f"{data.get('conditions', 'N/A')}, "
        f"{data.get('temperature', 'N/A')} "
        f"(feels like {data.get('feels_like', 'N/A')}), "
        f"humidity {data.get('humidity', 'N/A')}, "
        f"wind {data.get('wind', 'N/A')}."
    )


def _fmt_forecast(data: dict) -> str:
    if "error" in data:
        return None
    days = data.get("forecast", [])
    if not days:
        return f"No forecast available for {data.get('location', 'your area')}."
    lines = [f"Forecast for {data.get('location', 'your area')}:"]
    for d in days:
        lines.append(
            f"  {d['date']}: {d['conditions']}, "
            f"H {d.get('high', 'N/A')} / L {d.get('low', 'N/A')}, "
            f"rain {d.get('chance_of_rain', 'N/A')}"
        )
    return "\n".join(lines)


def _fmt_location(data: dict) -> str:
    if "error" in data:
        return None
    return (
        f"You're in {data.get('city', '?')}, "
        f"{data.get('region', '?')}, {data.get('country', '?')} "
        f"(timezone: {data.get('timezone', '?')})."
    )


def _fmt_network(data: dict) -> str:
    icons = {True: "✓", False: "✗"}
    return (
        f"Internet: {icons.get(data.get('internet'), '?')}, "
        f"Ping: {data.get('ping_latency', 'N/A')}, "
        f"DNS: {icons.get(data.get('dns_working'), '?')}"
    )


def _fmt_speedtest(data: dict) -> str:
    if "error" in data:
        return None
    return (
        f"Download: {data.get('download', 'N/A')}, "
        f"Upload: {data.get('upload', 'N/A')}, "
        f"Ping: {data.get('ping', 'N/A')}"
    )


def _fmt_calculator(data: dict) -> str:
    if "error" in data:
        return None
    expr = data.get("expression", "")
    result = data.get("result", "")
    interpretation = data.get("interpretation")
    if interpretation:
        return f"{interpretation} = {result}"
    return f"{expr} = {result}"


def _fmt_unit_convert(data: dict) -> str:
    if "error" in data:
        return None
    return f"{data.get('from', '')} = {data.get('to', '')}"


def _fmt_currency(data: dict) -> str:
    if "error" in data:
        return None
    return f"{data.get('from', '')} = {data.get('to', '')}"


def _fmt_notes_list(data: dict) -> str:
    notes = data.get("notes", [])
    if not notes:
        return "You have no saved notes."
    return "Your notes:\n" + "\n".join(f"  - {n}" for n in notes)


def _fmt_note_read(data: dict) -> str:
    return f"**{data.get('title', 'Note')}**\n{data.get('content', '')}"


def _fmt_create_note(data: dict) -> str:
    return f"Note '{data.get('title', '')}' created."


def _fmt_delete_note(data: dict) -> str:
    return f"Note '{data.get('title', '')}' deleted."


def _fmt_search_notes(data: dict) -> str:
    matches = data.get("matches", [])
    if not matches:
        return f"No notes matched '{data.get('keyword', '')}'."
    return f"Found {data.get('count', 0)} notes:\n" + "\n".join(f"  - {m}" for m in matches)


def _fmt_clipboard_read(data: dict) -> str:
    if "error" in data:
        return None
    content = data.get("content", "")
    if not content:
        return "Clipboard is empty."
    return f"Clipboard ({data.get('length', 0)} chars):\n{content[:500]}"


def _fmt_clipboard_copy(data: dict) -> str:
    return f"Copied {data.get('length', 0)} characters to clipboard."


def _fmt_clipboard_clear(data: dict) -> str:
    return "Clipboard cleared."


def _fmt_screenshot(data: dict) -> str:
    if "error" in data:
        return None
    return f"Screenshot saved: {data.get('path', '')} ({data.get('size_kb', '?')} KB)"


def _fmt_processes(data: dict) -> str:
    if "error" in data:
        return None
    procs = data.get("processes", [])
    if not procs:
        return "No processes found."
    lines = [f"Processes ({data.get('count', len(procs))} shown):"]
    for p in procs[:20]:
        lines.append(f"  {p['pid']:>6}  {p.get('cpu', '?'):>6}  {p.get('memory', '?'):>6}  {p['name']}")
    return "\n".join(lines)


def _fmt_search_processes(data: dict) -> str:
    if "error" in data:
        return None
    procs = data.get("processes", [])
    if not procs:
        return f"No processes found matching '{data.get('query', '')}'."
    lines = [f"Found {data.get('count', len(procs))} process(es):"]
    for p in procs:
        lines.append(f"  {p['pid']:>6}  {p.get('cpu', '?'):>6}  {p.get('memory', '?'):>6}  {p['name']}")
    return "\n".join(lines)


def _fmt_list_files(data: dict) -> str:
    if "error" in data:
        return None
    dirs = data.get("directories", [])
    files = data.get("files", [])
    lines = [f"Contents of {data.get('path', '.')}:"]
    if dirs:
        lines.append("  Directories: " + ", ".join(dirs))
    if files:
        lines.append("  Files: " + ", ".join(files))
    return "\n".join(lines)


def _fmt_read_file(data: dict) -> str:
    if "error" in data:
        return None
    content = data.get("content", "")
    if len(content) > 1000:
        content = content[:1000] + "\n... [truncated]"
    return f"File ({data.get('size', 0)} bytes):\n{content}"


def _fmt_write_file(data: dict) -> str:
    return f"Wrote {data.get('written', 0)} bytes to {data.get('path', '')}."


def _fmt_news(data: dict) -> str:
    if "error" in data:
        return None
    articles = data.get("articles", [])
    if not articles:
        return f"No news found for '{data.get('topic', 'general')}'."
    lines = [f"News — {data.get('topic', 'headlines')}:"]
    for a in articles:
        lines.append(f"  • {a.get('title', '')} ({a.get('source', '')})")
    return "\n".join(lines)


def _fmt_search_files(data: dict) -> str:
    matches = data.get("matches", [])
    if not matches:
        return f"No files matching '{data.get('pattern', '')}'."
    return f"Found {data.get('count', 0)} files:\n" + "\n".join(f"  - {m}" for m in matches)


def _fmt_sunrise(data: dict) -> str:
    if "error" in data:
        return None
    return (
        f"Sunrise: {data.get('sunrise', 'N/A')}, "
        f"Sunset: {data.get('sunset', 'N/A')}, "
        f"Daylight: {data.get('daylight_hours', 'N/A')}"
    )


def _fmt_open_file(data: dict) -> str:
    return f"Opened: {data.get('path', '')}"


def _fmt_launch_app(data: dict) -> str:
    return f"Launched {data.get('app', '')}."


def _fmt_open_url(data: dict) -> str:
    return f"Opened URL: {data.get('url', '')}"


def _fmt_create_dir(data: dict) -> str:
    return f"Directory created: {data.get('path', '')}"


def _fmt_copy_file(data: dict) -> str:
    return f"Copied to {data.get('destination', '')}"


def _fmt_move_file(data: dict) -> str:
    return f"Moved to {data.get('destination', '')}"


def _fmt_delete_file(data: dict) -> str:
    return f"Deleted: {data.get('path', '')}"


def _fmt_terminate_process(data: dict) -> str:
    return f"Process '{data.get('name', '')}' (PID {data.get('pid', '?')}) terminated."


def _fmt_web_search(data: dict) -> str:
    if "error" in data:
        return None
    results = data.get("results", [])
    if not results:
        return f"No results for '{data.get('query', '')}'."
    lines = [f"Search results for '{data.get('query', '')}':"]
    for r in results[:5]:
        lines.append(f"  • {r.get('title', '')} — {r.get('url', '')}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_FORMATTERS: dict[str, callable] = {
    "time": _fmt_time,
    "battery": _fmt_battery,
    "system_info": _fmt_system_info,
    "weather": _fmt_weather,
    "forecast": _fmt_forecast,
    "location": _fmt_location,
    "network_status": _fmt_network,
    "speed_test": _fmt_speedtest,
    "calculator": _fmt_calculator,
    "unit_convert": _fmt_unit_convert,
    "currency_convert": _fmt_currency,
    "list_notes": _fmt_notes_list,
    "read_note": _fmt_note_read,
    "create_note": _fmt_create_note,
    "delete_note": _fmt_delete_note,
    "search_notes": _fmt_search_notes,
    "clipboard_read": _fmt_clipboard_read,
    "clipboard_copy": _fmt_clipboard_copy,
    "clipboard_clear": _fmt_clipboard_clear,
    "screenshot": _fmt_screenshot,
    "list_processes": _fmt_processes,
    "search_processes": _fmt_search_processes,
    "list_files": _fmt_list_files,
    "read_file": _fmt_read_file,
    "write_file": _fmt_write_file,
    "news": _fmt_news,
    "search_files": _fmt_search_files,
    "sunrise_sunset": _fmt_sunrise,
    "open_file": _fmt_open_file,
    "launch_app": _fmt_launch_app,
    "open_url": _fmt_open_url,
    "create_dir": _fmt_create_dir,
    "copy_file": _fmt_copy_file,
    "move_file": _fmt_move_file,
    "delete_file": _fmt_delete_file,
    "terminate_process": _fmt_terminate_process,
    "web_search": _fmt_web_search,
}
