"""Risk-level constants and permission checking for JARVIS tools."""

import logging

logger = logging.getLogger("jarvis.permissions")

RISK_SAFE = "safe"
RISK_WRITE = "write"
RISK_SENSITIVE = "sensitive"
RISK_DESTRUCTIVE = "destructive"

RISK_ORDER = [RISK_SAFE, RISK_WRITE, RISK_SENSITIVE, RISK_DESTRUCTIVE]

USER_CONFIRM_PROMPT = (
    "This action requires your permission. Allow? (yes/no): "
)


def risk_level_descriptive(level: str) -> str:
    labels = {
        RISK_SAFE: "safe",
        RISK_WRITE: "write",
        RISK_SENSITIVE: "sensitive",
        RISK_DESTRUCTIVE: "destructive",
    }
    return labels.get(level, RISK_SAFE)


def requires_confirmation(level: str, auto_confirm_write: bool = True) -> bool:
    if level == RISK_SAFE:
        return False
    if level == RISK_WRITE:
        return not auto_confirm_write
    if level in (RISK_SENSITIVE, RISK_DESTRUCTIVE):
        return True
    return False


def confirm_action(tool_name: str, details: str = "") -> bool:
    import sys
    from ..main import ts, yellow, green, red

    msg = f"  Tool '{tool_name}' requires permission."
    if details:
        msg += f" {details}"
    print(ts(yellow(msg)))
    try:
        answer = input(ts(yellow(USER_CONFIRM_PROMPT))).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    granted = answer in ("yes", "y")
    if granted:
        print(ts(green("  Permission granted.")))
    else:
        print(ts(red("  Permission denied.")))
    logger.info(f"Permission {tool_name}: {'granted' if granted else 'denied'}")
    return granted
