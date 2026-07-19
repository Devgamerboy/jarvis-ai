import json
import logging
import os
import sys
import time
from datetime import datetime

from .brain.processor import (
    ask_ai,
    ask_ai_stream,
    build_messages,
    parse_tool_calls,
    select_tools_for_query,
)
from .config import (
    AI_BASE_URL,
    AI_MODEL,
    ASSISTANT_NAME,
    AUTO_CONFIRM_WRITE,
    ENABLE_COLORS,
    ENABLE_DETERMINISTIC_ROUTING,
    ENABLE_STREAMING,
    ENABLE_TOOLS,
    LOG_DIR,
    LOG_LEVEL,
    MAX_CONTEXT_TURNS,
    MAX_HISTORY_MESSAGES,
    MAX_PROMPT_CHARS,
    MAX_TOOL_ROUNDS,
    PERFORMANCE_LOGGING,
)
from .brain.client import get_client
from .memory.memory import add_entry, load_memory
from .memory.facts import set_fact, get_fact

# ---------------------------------------------------------------------------
# Colouring helpers
# ---------------------------------------------------------------------------

def _color(code, text):
    if not ENABLE_COLORS:
        return text
    return f"\033[{code}m{text}\033[0m"

def cyan(text):   return _color("36", text)
def green(text):  return _color("32", text)
def red(text):    return _color("31", text)
def yellow(text): return _color("33", text)
def blue(text):   return _color("34", text)
def grey(text):   return _color("90", text)

def now():
    return datetime.now().strftime("%H:%M:%S")

def ts(text):
    return grey(f"[{now()}] ") + text

# ---------------------------------------------------------------------------
# Timing
# ---------------------------------------------------------------------------

_timings: dict[str, float] = {}
_ai_calls: int = 0
_log_tool = logging.getLogger("jarvis.tool")
_log_sec = logging.getLogger("jarvis.security")
_log_err = logging.getLogger("jarvis")


def _reset_ai_calls():
    global _ai_calls
    _ai_calls = 0


def _inc_ai_calls():
    global _ai_calls
    _ai_calls += 1

def _timer_start(label: str):
    _timings[label] = time.time()

def _timer_end(label: str) -> float:
    elapsed = time.time() - _timings.pop(label, time.time())
    return elapsed

def _report_timing(label: str, elapsed: float):
    _print_timing(label, elapsed)

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s")

    err_handler = logging.FileHandler(os.path.join(LOG_DIR, "errors.log"))
    err_handler.setLevel(logging.WARNING)
    err_handler.setFormatter(fmt)

    tool_handler = logging.FileHandler(os.path.join(LOG_DIR, "tools.log"))
    tool_handler.setLevel(logging.INFO)
    tool_handler.setFormatter(fmt)

    sec_handler = logging.FileHandler(os.path.join(LOG_DIR, "security.log"))
    sec_handler.setLevel(logging.INFO)
    sec_handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(err_handler)

    _log_tool.setLevel(logging.INFO)
    _log_tool.addHandler(tool_handler)

    _log_sec.setLevel(logging.INFO)
    _log_sec.addHandler(sec_handler)

def log_tool_use(tool_name: str, duration: float, error: str = ""):
    line = f"TOOL:{tool_name} duration:{duration:.2f}s"
    if error:
        line += f" error:{error}"
    print(ts(grey(line)))
    _log_tool.info("Tool '%s' executed in %.2fs%s", tool_name, duration,
                   f" — {error}" if error else "")


def _print_timing(label: str, seconds: float, ai_calls: int | None = None):
    if not PERFORMANCE_LOGGING:
        return
    label_part = label.upper() if ":" not in label else label
    parts = [f"{label_part} duration:{seconds:.2f}s"]
    if ai_calls is not None:
        parts.append(f"AI CALLS: {ai_calls}")
    print(ts(grey(" ".join(parts))))

# ---------------------------------------------------------------------------
# Banner & health
# ---------------------------------------------------------------------------

VERSION = "1.4.1"

def print_banner():
    banner = f"""
{'=' * 38}
  {green(ASSISTANT_NAME + f' v{VERSION}')}
  {green('Desktop AI Assistant')}
  {yellow(f'Model: {AI_MODEL}')}
{'=' * 38}
"""
    print(banner)

def check_ai():
    from .brain.client import check_connection
    err = check_connection()
    if err:
        _log_err.error("AI server unreachable at %s: %s", AI_BASE_URL, err)
        print(ts(red(err)))
        return False
    return True

# ---------------------------------------------------------------------------
# Slash commands
# ---------------------------------------------------------------------------

def handle_command(cmd: str) -> bool:
    parts = cmd.strip().split(maxsplit=1)
    verb = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""

    if verb == "/help":
        print(ts(yellow("Commands:")))
        for cmd, desc in [
            ("/help", "Show this help"),
            ("/tools", "List available tools by category"),
            ("/tool <name> <json>", "Run a tool directly"),
            ("/clear", "Clear conversation history"),
            ("/status", "Show system information"),
            ("/set location <loc>", "Save your location"),
            ("/memory", "List stored memories"),
            ("/forget <key>", "Forget a stored fact"),
            ("/remember <key> <value>", "Store a fact"),
            ("/notes", "List saved notes"),
            ("/debug-prompt", "Show prompt debug info"),
        ]:
            print(ts(cyan(f"  {cmd:<30}") + yellow(desc)))
        return True

    if verb == "/tools":
        from .tools import list_by_category
        by_cat = list_by_category()
        if not by_cat:
            print(ts(yellow("No tools registered.")))
        else:
            cats = ["Web", "Weather & Location", "System", "Network", "Files",
                    "Desktop", "Productivity", "Utilities", "Plugins"]
            print(ts(green("Available tools:")))
            for cat in cats:
                specs = by_cat.get(cat)
                if not specs:
                    continue
                print(ts(cyan(f"\n  [{cat}]")))
                for s in specs:
                    risk_mark = ""
                    r = s.get("risk", "safe")
                    if r != "safe":
                        risk_mark = f" [{r}]"
                    print(ts(f"    {s['name']}{risk_mark}"))
                    print(ts(grey(f"      {s['description']}")))
        return True

    if verb == "/tool":
        tool_parts = rest.split(maxsplit=1)
        if not tool_parts:
            print(ts(red("Usage: /tool <name> [json-args]")))
            return True
        tool_name = tool_parts[0]
        tool_args = {}
        if len(tool_parts) > 1:
            try:
                tool_args = json.loads(tool_parts[1])
            except json.JSONDecodeError:
                print(ts(red("Arguments must be valid JSON.")))
                return True
        from .tools import execute
        start = time.time()
        result = execute(tool_name, auto_confirm_write=AUTO_CONFIRM_WRITE, **tool_args)
        duration = time.time() - start
        log_tool_use(tool_name, duration)
        if result["success"]:
            print(ts(green("Result:")))
            print(json.dumps(result["result"], indent=2, default=str))
        else:
            print(ts(red(f"Error: {result['error']}")))
        return True

    if verb == "/clear":
        from .memory.conversations import clear
        clear()
        print(ts(green("Conversation history cleared.")))
        return True

    if verb == "/status":
        from .tools import execute as tool_execute
        result = tool_execute("system_info", auto_confirm_write=AUTO_CONFIRM_WRITE)
        if result["success"]:
            print(ts(cyan("System Information:")))
            for k, v in result["result"].items():
                if isinstance(v, dict):
                    print(ts(f"  {k.replace('_', ' ').title()}:"))
                    for sk, sv in v.items():
                        print(ts(f"    {sk.replace('_', ' ').title()}: {sv}"))
                else:
                    label = k.replace("_", " ").title()
                    print(ts(f"  {label}: {v}"))
        else:
            print(ts(red(f"Error: {result['error']}")))
        return True

    if verb == "/set" and rest.startswith("location"):
        loc_value = rest[len("location "):].strip()
        if loc_value:
            set_fact("location", loc_value)
            print(ts(green(f"Location saved: {loc_value}")))
        else:
            print(ts(red("Usage: /set location <city, state>")))
        return True

    if verb == "/memory":
        from .memory.facts import get_all as get_all_facts
        from .memory.preferences import get_all as get_all_prefs
        facts = get_all_facts()
        prefs = get_all_prefs()
        if facts:
            print(ts(green("Facts:")))
            for k, v in facts.items():
                print(ts(f"  {k}: {v}"))
        else:
            print(ts(yellow("No facts stored.")))
        if prefs:
            print(ts(green("Preferences:")))
            for k, v in prefs.items():
                print(ts(f"  {k}: {v}"))
        return True

    if verb == "/forget":
        key = rest.strip()
        if key:
            from .memory.facts import set_fact as sf
            sf(key, None)
            from .memory.facts import save, load
            data = load()
            data.pop(key, None)
            save(data)
            print(ts(green(f"Forgot '{key}'.")))
        else:
            print(ts(red("Usage: /forget <key>")))
        return True

    if verb == "/remember":
        kv = rest.split(maxsplit=1)
        if len(kv) == 2:
            set_fact(kv[0], kv[1])
            print(ts(green(f"Remembered: {kv[0]} = {kv[1]}")))
        else:
            print(ts(red("Usage: /remember <key> <value>")))
        return True

    if verb == "/notes":
        from .tools import execute as tool_execute
        result = tool_execute("list_notes", auto_confirm_write=AUTO_CONFIRM_WRITE)
        if result["success"]:
            notes = result["result"].get("notes", [])
            if notes:
                print(ts(green("Notes:")))
                for n in notes:
                    print(ts(f"  - {n}"))
            else:
                print(ts(yellow("No notes saved.")))
        else:
            print(ts(red(f"Error: {result['error']}")))
        return True

    if verb == "/debug-prompt":
        _show_debug_prompt()
        return True

    return False


def _show_debug_prompt():
    """Print debug info about the current prompt configuration."""
    from .tools import list_all, list_names
    from .brain.processor import _build_prompt

    tools = list_all()
    full_prompt = _build_prompt(None)

    print(ts(green("Prompt Debug Info:")))
    print(ts(f"  Tools registered: {len(tools)}"))
    print(ts(f"  Tool names: {', '.join(list_names())}"))
    print(ts(f"  Full prompt length: {len(full_prompt)} chars"))
    print(ts(f"  Estimated prompt tokens: ~{len(full_prompt) // 4}"))
    print(ts(f"  MAX_HISTORY_MESSAGES: {MAX_HISTORY_MESSAGES}"))
    print(ts(f"  MAX_PROMPT_CHARS: {MAX_PROMPT_CHARS}"))
    print(ts(f"  MAX_CONTEXT_TURNS: {MAX_CONTEXT_TURNS}"))
    print(ts(f"  MAX_TOOL_ROUNDS: {MAX_TOOL_ROUNDS}"))
    print(ts(f"  Deterministic routing: {'ON' if ENABLE_DETERMINISTIC_ROUTING else 'OFF'}"))

# ---------------------------------------------------------------------------
# Casual speech detection
# ---------------------------------------------------------------------------

_CASUAL = {"hello", "hi", "hey", "sup", "howdy", "yo", "thanks", "thank you", "thx", "goodbye", "bye", "see you", "good day", "good night"}
_CASUAL_PHRASES = ["good morning", "good afternoon", "good evening", "how are you", "how's it going", "what's up", "whats up", "nice to meet"]

def _is_casual(text):
    t = text.strip().lower().rstrip("?!.,;:")
    if t in _CASUAL or any(t.startswith(p) for p in _CASUAL_PHRASES):
        return True
    first = t.split()[0] if t.split() else ""
    if first in {"hello", "hi", "hey", "sup", "howdy", "yo", "thanks", "bye"}:
        return True
    return False

# ---------------------------------------------------------------------------
# Intent validation (keyword guard)
# ---------------------------------------------------------------------------

_TOOL_KEYWORDS = {
    "system_info": ["system", "os", "operating system", "cpu", "processor", "memory", "ram", "hardware", "computer spec", "machine", "platform", "specs", "hostname", "kernel", "gpu", "uptime", "how fast", "how much ram"],
    "battery": ["battery", "charge", "power", "battery level", "battery percentage"],
    "weather": ["weather", "temperature", "outside", "hot", "cold", "rain", "humidity", "wind", "forecast", "umbrella", "what is it like"],
    "forecast": ["forecast", "3-day", "weekend", "this week", "coming days"],
    "sunrise_sunset": ["sunrise", "sunset", "daylight", "sun", "dusk", "dawn"],
    "location": ["where am i", "my location", "current location", "what city", "what country", "where are we"],
    "time": ["what time", "current time", "what is the date", "what day", "today's date", "what's the date"],
    "network_status": ["internet", "network", "connectivity", "ping", "dns", "gateway", "connection", "online", "wifi"],
    "speed_test": ["speed test", "internet speed", "download speed", "upload speed", "bandwidth"],
    "web_search": ["search", "look up", "find online", "google", "duckduckgo", "search the web", "find on the internet", "what is", "who is"],
    "web_fetch": ["fetch", "get url", "open url", "visit", "download page", "http", "https://", "website content"],
    "read_file": ["read", "open file", "show file", "view file", "cat", "content of", "print file"],
    "write_file": ["write", "create", "save", "make file", "store", "new file"],
    "list_files": ["list", "show files", "show directory", "what files", "ls", "dir", "browse", "contents of"],
    "calculate": ["calculate", "compute", "what is", "math", "arithmetic", "plus", "minus", "times", "divided", "percent", "square root", "sqrt", "power"],
    "convert": ["convert", "conversion", "to", "in", "miles", "kilometers", "feet", "meters", "cups", "milliliters", "fahrenheit", "celsius", "pounds", "kilograms", "inches", "centimeters"],
    "currency_convert": ["currency", "exchange rate", "usd", "eur", "gbp", "convert money", "$", "€", "£"],
    "news": ["news", "headlines", "what's happening", "latest", "current events", "top stories"],
    "create_note": ["note", "remember", "write down", "save this"],
    "list_notes": ["list notes", "show notes", "my notes"],
    "read_note": ["read note", "open note", "show note"],
    "update_note": ["update note", "edit note", "change note"],
    "delete_note": ["delete note", "remove note"],
    "search_notes": ["search notes", "find note"],
    "clipboard_read": ["clipboard", "what's copied", "clipboard content"],
    "clipboard_copy": ["copy", "clipboard copy"],
    "clipboard_clear": ["clear clipboard"],
    "screenshot": ["screenshot", "capture screen", "take screenshot"],
    "create_dir": ["create directory", "mkdir", "make directory", "create folder"],
    "copy_file": ["copy file", "copy", "duplicate file"],
    "move_file": ["move file", "move", "rename file", "rename"],
    "search_files": ["search file", "find file", "locate file"],
    "search_content": ["search content", "find text", "search in files"],
    "delete_file": ["delete file", "remove file"],
    "open_file": ["open file", "open folder", "open directory", "launch file explorer"],
    "list_processes": ["processes", "running programs", "task manager", "ps"],
    "search_processes": ["find process", "search process"],
    "terminate_process": ["kill process", "terminate", "stop process"],
    "launch_app": ["open app", "launch", "start application", "open program"],
    "open_url": ["open url", "open website", "browse to"],
    "calculator": ["calculate", "compute", "math", "arithmetic", "plus", "minus", "times", "divided", "percent", "square root", "sqrt", "power"],
    "unit_convert": ["convert", "conversion", "miles to", "km to", "fahrenheit to", "celsius to", "pounds to", "kg to"],
}

def _validate_tool_call(user_input: str, tool_name: str) -> bool:
    if _is_casual(user_input):
        return False
    lowered = user_input.lower()
    keywords = _TOOL_KEYWORDS.get(tool_name, [])
    return any(kw in lowered for kw in keywords)

# ---------------------------------------------------------------------------
# Tool execution helpers
# ---------------------------------------------------------------------------

def _strip_tool_calls(text: str) -> str:
    lines = [l for l in text.split("\n") if "TOOL_CALL:" not in l]
    cleaned = "\n".join(l for l in lines if l.strip()).strip()
    if cleaned:
        return cleaned
    return "I understood your request and processed it."

# ---------------------------------------------------------------------------
# Deterministic routing
# ---------------------------------------------------------------------------

def _try_deterministic_route(user_input: str):
    """Attempt deterministic routing.

    Returns ``(formatted_result, was_routed, routed_tool_name)``.
    ``was_routed`` is ``True`` if a route matched (tool may or may not have
    a formatter). ``formatted`` is ``None`` when no formatter is available.
    """
    from .tools.router import route as det_route
    from .tools import execute
    from .tools.simple_formatter import format_result

    routed = det_route(user_input)
    if routed is None:
        return None, False, None

    _print_timing(f"ROUTE:{routed.route_name}", 0.0)

    _timer_start(f"TOOL:{routed.tool_name}")
    result = execute(routed.tool_name, auto_confirm_write=AUTO_CONFIRM_WRITE, **routed.args)
    exec_time = _timer_end(f"TOOL:{routed.tool_name}")
    log_tool_use(routed.tool_name, exec_time)

    if not result["success"]:
        return None, True, routed.tool_name

    formatted = format_result(routed.tool_name, result)
    if formatted is not None:
        return formatted, True, routed.tool_name
    return None, True, routed.tool_name

# ---------------------------------------------------------------------------
# LLM-based tool chaining
# ---------------------------------------------------------------------------

def process_tool_calls(messages, initial_response, user_input):
    from .tools import execute

    text = initial_response
    for _round in range(MAX_TOOL_ROUNDS):
        calls = parse_tool_calls(text)
        if not calls:
            return text

        valid = [(n, a) for n, a in calls if _validate_tool_call(user_input, n)]
        if not valid:
            return text

        messages.append({"role": "assistant", "content": text})

        for name, args in valid:
            print(ts(yellow(f"  Using tool: {name}...")))
            _timer_start(f"tool:{name}")
            result = execute(name, auto_confirm_write=AUTO_CONFIRM_WRITE, **args)
            duration = _timer_end(f"tool:{name}")
            if result["success"]:
                log_tool_use(name, duration)
            else:
                log_tool_use(name, duration, result.get("error", "unknown"))
                if result.get("error") == "Permission denied by user":
                    messages.append({
                        "role": "user",
                        "content": f"Tool '{name}' was not executed because you denied permission."
                    })
                    continue
            messages.append({
                "role": "user",
                "content": f"Tool '{name}' returned: {json.dumps(result, indent=2, default=str)}"
            })

        _timer_start("ai_reask")
        _inc_ai_calls()
        text = ask_ai(messages)
        _print_timing("AI", _timer_end("ai_reask"))

    return text

# ---------------------------------------------------------------------------
# Streaming
# ---------------------------------------------------------------------------

def stream_response(messages):
    full_reply = ""
    print(ts(green(f"{ASSISTANT_NAME}: ")), end="", flush=True)
    _inc_ai_calls()
    for chunk in ask_ai_stream(messages):
        content = chunk["message"]["content"]
        if content:
            print(content, end="", flush=True)
            full_reply += content
    print()
    return full_reply

# ---------------------------------------------------------------------------
# Personality helpers
# ---------------------------------------------------------------------------

def _welcome_message():
    name = get_fact("name") or get_fact("preferred_name") or ""
    if name:
        return f"Welcome back, {name}! How can I help you today?"
    return "Welcome! How can I help you today?"

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    setup_logging()

    if ENABLE_TOOLS:
        _timer_start("discovery")
        from .tools import register_all
        register_all()
        _print_timing("DISCOVERY", _timer_end("discovery"))

    print_banner()

    if ENABLE_TOOLS:
        from .tools import list_all
        tools = list_all()
        if tools:
            print(ts(grey(f"Tools loaded: {', '.join(t['name'] for t in tools)}")))

    if not check_ai():
        sys.exit(1)

    print(ts(yellow(_welcome_message())))
    print(ts(yellow("Type /help for commands, 'exit' to quit.\n")))

    while True:
        try:
            user_input = input(ts(cyan("You: "))).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            print(ts(green("Goodbye.")))
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print(ts(green("Goodbye.")))
            break

        if user_input.startswith("/"):
            if handle_command(user_input):
                continue
            print(ts(red(f"Unknown command: {user_input}")))
            print(ts(yellow("Type /help for available commands.")))
            continue

        _timer_start("total_request")
        _reset_ai_calls()

        # -- Special inline commands --
        if user_input.lower().startswith("my location is"):
            loc = user_input[len("my location is"):].strip()
            if loc:
                set_fact("location", loc)
                print(ts(green(f"Got it! I'll remember your location as: {loc}")))
            _print_timing("TOTAL", _timer_end("total_request"), _ai_calls)
            continue

        if user_input.lower().startswith("my name is"):
            name = user_input[len("my name is"):].strip()
            if name:
                set_fact("name", name)
                print(ts(green(f"Nice to meet you, {name}!")))
            _print_timing("TOTAL", _timer_end("total_request"), _ai_calls)
            continue

        # -- Casual greeting fast path (no tools) --
        if _is_casual(user_input):
            _timer_start("prompt_construction")
            memory = load_memory()
            messages = build_messages(user_input, memory, MAX_CONTEXT_TURNS)
            _print_timing("prompt_construction", _timer_end("prompt_construction"))

            _timer_start("ai")
            _inc_ai_calls()
            full_reply = ask_ai(messages)
            _print_timing("AI", _timer_end("ai"))

            cleaned = _strip_tool_calls(full_reply)
            print(ts(green(f"{ASSISTANT_NAME}: {cleaned}")))
            add_entry(user_input, full_reply)
            _print_timing("TOTAL", _timer_end("total_request"), _ai_calls)
            continue

        # -- Tool-enabled path: route BEFORE any AI call --
        if ENABLE_TOOLS:
            # 1. Deterministic routing — zero AI calls for obvious single-tool requests
            if ENABLE_DETERMINISTIC_ROUTING:
                formatted, was_routed, routed_name = _try_deterministic_route(user_input)
                if was_routed and formatted is not None:
                    print(ts(green(f"{ASSISTANT_NAME}: {formatted}")))
                    add_entry(user_input, formatted)
                    _print_timing("TOTAL", _timer_end("total_request"), _ai_calls)
                    continue
                if was_routed and formatted is None and routed_name:
                    # Tool executed but no formatter — fall through to AI with the result
                    pass

            # 2. Build selective prompt (only relevant tools, not all 40)
            _timer_start("prompt_construction")
            relevant_tools = select_tools_for_query(user_input)
            memory = load_memory()
            messages = build_messages(user_input, memory, MAX_CONTEXT_TURNS,
                                      tool_names=relevant_tools)
            _print_timing("prompt_construction", _timer_end("prompt_construction"))

            try:
                # 3. Ask LLM for tool plan (only for multi-step or unclear requests)
                _timer_start("AI")
                _inc_ai_calls()
                full_reply = ask_ai(messages)
                _print_timing("AI", _timer_end("AI"))

                # 4. Execute any tool calls the LLM requested
                calls = parse_tool_calls(full_reply)
                valid_calls = [(n, a) for n, a in calls if _validate_tool_call(user_input, n)]
                if valid_calls:
                    full_reply = process_tool_calls(messages, full_reply, user_input)

                cleaned = _strip_tool_calls(full_reply)
                print(ts(green(f"{ASSISTANT_NAME}: {cleaned}")))

            except Exception as e:
                msg = str(e).strip() or type(e).__name__
                print(ts(red(f"Error: {msg}")))
                _log_err.error("Request failed: %s", msg)
                _print_timing("TOTAL", _timer_end("total_request"), _ai_calls)
                continue

        else:
            # No tools mode
            _timer_start("prompt_construction")
            memory = load_memory()
            messages = build_messages(user_input, memory, MAX_CONTEXT_TURNS)
            _print_timing("prompt_construction", _timer_end("prompt_construction"))

            try:
                if ENABLE_STREAMING:
                    _timer_start("ai")
                    full_reply = stream_response(messages)
                    _print_timing("AI", _timer_end("ai"))
                else:
                    _timer_start("ai")
                    _inc_ai_calls()
                    full_reply = ask_ai(messages)
                    _print_timing("AI", _timer_end("ai"))
                    print(ts(green(f"{ASSISTANT_NAME}: {full_reply}")))
            except Exception as e:
                msg = str(e).strip() or type(e).__name__
                print(ts(red(f"Error: {msg}")))
                _log_err.error("Request failed: %s", msg)
                _print_timing("TOTAL", _timer_end("total_request"), _ai_calls)
                continue

        add_entry(user_input, full_reply)
        _print_timing("TOTAL", _timer_end("total_request"), _ai_calls)


if __name__ == "__main__":
    main()
