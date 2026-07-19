import logging

from .base import Tool
from .permissions import (
    RISK_SAFE,
    RISK_WRITE,
    RISK_SENSITIVE,
    RISK_DESTRUCTIVE,
    requires_confirmation,
    confirm_action,
)

logger = logging.getLogger("jarvis.registry")

_registry: dict[str, Tool] = {}


def register(tool: Tool):
    _registry[tool.name] = tool


def get(name: str) -> Tool | None:
    return _registry.get(name)


def list_all() -> list[dict]:
    return [t.spec() for t in _registry.values()]


def list_by_category() -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for t in _registry.values():
        spec = t.spec()
        groups.setdefault(spec["category"], []).append(spec)
    return groups


def list_names() -> list[str]:
    return list(_registry.keys())


def execute(name: str, auto_confirm_write: bool = True, **kwargs) -> dict:
    tool = get(name)
    if tool is None:
        return {"success": False, "error": f"Unknown tool: '{name}'"}

    rl = tool.risk
    if requires_confirmation(rl, auto_confirm_write):
        details = ""
        if "path" in kwargs:
            details = f"Path: {kwargs['path']}"
        elif "query" in kwargs:
            details = f"Query: {kwargs['query']}"
        if not confirm_action(name, details):
            return {"success": False, "error": "Permission denied by user"}

    try:
        result = tool.execute(**kwargs)
        logger.info("Tool '%s' executed successfully", name)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error("Tool '%s' failed: %s", name, e)
        return {"success": False, "error": str(e)}
