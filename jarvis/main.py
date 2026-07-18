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
)
from .config import (
    AI_BASE_URL,
    AI_MODEL,
    ASSISTANT_NAME,
    ENABLE_COLORS,
    ENABLE_STREAMING,
    ENABLE_TOOLS,
    LOG_DIR,
    MAX_CONTEXT_TURNS,
)
from .brain.client import get_client
from .memory.memory import add_entry, load_memory
from .memory.facts import set_fact


def _color(code, text):
    if not ENABLE_COLORS:
        return text
    return f"\033[{code}m{text}\033[0m"


def cyan(text):
    return _color("36", text)


def green(text):
    return _color("32", text)


def red(text):
    return _color("31", text)


def yellow(text):
    return _color("33", text)


def blue(text):
    return _color("34", text)


def grey(text):
    return _color("90", text)


def now():
    return datetime.now().strftime("%H:%M:%S")


def ts(text):
    return grey(f"[{now()}] ") + text


def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(LOG_DIR, "errors.log"),
        level=logging.ERROR,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def log_tool_use(tool_name: str, duration: float, error: str = ""):
    log_line = f"TOOL:{tool_name} duration:{duration:.2f}s"
    if error:
        log_line += f" error:{error}"
    print(ts(grey(log_line)))


def print_banner():
    banner = f"""
{'=' * 38}
  {green(ASSISTANT_NAME + ' v1.3.0')}
  {green('Desktop AI Assistant')}
  {yellow(f'Model: {AI_MODEL}')}
{'=' * 38}
"""
    print(banner)


def check_ai():
    try:
        get_client().models.list()
    except Exception as e:
        logging.error(f"AI server unreachable at {AI_BASE_URL}: {e}")
        print(ts(red(f"Gemma AI server unavailable at {AI_BASE_URL}")))
        return False
    return True


def handle_command(cmd: str) -> bool:
    parts = cmd.strip().split(maxsplit=1)
    verb = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""

    if verb == "/help":
        print(ts(yellow("Commands:")))
        print(ts(cyan("  /help                  ") + yellow("Show this help")))
        print(ts(cyan("  /tools                 ") + yellow("List available tools")))
        print(ts(cyan("  /tool <name> <json>    ") + yellow("Run a tool directly")))
        print(ts(cyan("  /clear                 ") + yellow("Clear conversation history")))
        print(ts(cyan("  /status                ") + yellow("Show system information")))
        print(ts(cyan("  /set location <loc>    ") + yellow("Save your location")))
        print(ts(cyan("  exit / quit            ") + yellow("Exit JARVIS")))
        return True

    if verb == "/tools":
        from .tools import list_all
        tools = list_all()
        if not tools:
            print(ts(yellow("No tools registered.")))
        else:
            print(ts(green(f"Available tools ({len(tools)}):")))
            for t in tools:
                print(ts(cyan(f"  {t['name']}") + grey(f" — {t['description']}")))
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
                print(ts(red("Arguments must be valid JSON (e.g. /tool read_file {\"path\": \"/tmp/test\"})")))
                return True
        from .tools import execute
        start = time.time()
        result = execute(tool_name, **tool_args)
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
        result = tool_execute("system_info")
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

    return False


_TOOL_KEYWORDS = {
    "system_info": ["system", "os ", "operating system", "cpu", "processor", "memory", "ram", "hardware", "computer spec", "machine", "platform", "specs", "hostname", "kernel", "gpu", "uptime", "how fast", "how much ram"],
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
    "read_file": ["read", "open file", "show file", "view file", "cat ", "content of", "print file"],
    "write_file": ["write", "create", "save", "make file", "store", "new file"],
    "list_files": ["list", "show files", "show directory", "what files", "ls ", "dir ", "browse", "contents of"],
}

def _strip_tool_calls(text: str) -> str:
    lines = [l for l in text.split("\n") if "TOOL_CALL:" not in l]
    cleaned = "\n".join(l for l in lines if l.strip()).strip()
    if cleaned:
        return cleaned
    return "I understood your request and processed it."

_CASUAL = {"hello", "hi", "hey", "sup", "howdy", "yo", "thanks", "thank you", "thx", "goodbye", "bye", "see you", "good day"}
_CASUAL_PHRASES = ["good morning", "good afternoon", "good evening", "how are you", "how's it going", "what's up", "whats up", "nice to meet"]

def _is_casual(text):
    t = text.strip().lower().rstrip("?!.,;:")
    if t in _CASUAL or any(t.startswith(p) for p in _CASUAL_PHRASES):
        return True
    first = t.split()[0] if t.split() else ""
    if first in {"hello", "hi", "hey", "sup", "howdy", "yo", "thanks", "bye"}:
        return True
    return False

def _validate_tool_call(user_input: str, tool_name: str) -> bool:
    if _is_casual(user_input):
        return False
    lowered = user_input.lower()
    keywords = _TOOL_KEYWORDS.get(tool_name, [])
    return any(kw in lowered for kw in keywords)


def process_tool_calls(messages, initial_response, user_input):
    from .brain.processor import MAX_TOOL_ROUNDS
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
            start = time.time()
            result = execute(name, **args)
            duration = time.time() - start
            if result["success"]:
                log_tool_use(name, duration)
            else:
                log_tool_use(name, duration, result.get("error", "unknown"))
            messages.append({
                "role": "user",
                "content": f"Tool '{name}' returned: {json.dumps(result, indent=2, default=str)}"
            })

        text = ask_ai(messages)

    return text


def stream_response(messages):
    full_reply = ""
    print(ts(green(f"{ASSISTANT_NAME}: ")), end="", flush=True)
    for chunk in ask_ai_stream(messages):
        content = chunk["message"]["content"]
        if content:
            print(content, end="", flush=True)
            full_reply += content
    print()
    return full_reply


def main():
    setup_logging()

    if ENABLE_TOOLS:
        from .tools import register_all
        register_all()

    print_banner()

    if ENABLE_TOOLS:
        from .tools import list_all
        tools = list_all()
        if tools:
            print(ts(grey(f"Tools loaded: {', '.join(t['name'] for t in tools)}")))

    if not check_ai():
        sys.exit(1)

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

        if user_input.lower().startswith("my location is"):
            loc = user_input[len("my location is"):].strip()
            if loc:
                set_fact("location", loc)
                print(ts(green(f"Got it! I'll remember your location as: {loc}")))
            continue

        memory = load_memory()
        messages = build_messages(user_input, memory, MAX_CONTEXT_TURNS)

        try:
            if ENABLE_TOOLS and not _is_casual(user_input):
                full_reply = ask_ai(messages)
                calls = parse_tool_calls(full_reply)
                valid_calls = [(n, a) for n, a in calls if _validate_tool_call(user_input, n)]
                if valid_calls:
                    full_reply = process_tool_calls(messages, full_reply, user_input)
                cleaned = _strip_tool_calls(full_reply)
                print(ts(green(f"{ASSISTANT_NAME}: {cleaned}")))
            elif ENABLE_TOOLS and _is_casual(user_input):
                full_reply = ask_ai(messages)
                cleaned = _strip_tool_calls(full_reply)
                print(ts(green(f"{ASSISTANT_NAME}: {cleaned}")))
            else:
                if ENABLE_STREAMING:
                    full_reply = stream_response(messages)
                else:
                    full_reply = ask_ai(messages)
                    print(ts(green(f"{ASSISTANT_NAME}: {full_reply}")))

        except Exception as e:
            msg = str(e).strip() or type(e).__name__
            print(ts(red(f"Error: {msg}")))
            logging.error(msg)
            continue

        add_entry(user_input, full_reply)


if __name__ == "__main__":
    main()
