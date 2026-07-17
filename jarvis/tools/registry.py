from .base import Tool


_registry: dict[str, Tool] = {}


def register(tool: Tool):
    _registry[tool.name] = tool


def get(name: str) -> Tool | None:
    return _registry.get(name)


def list_all() -> list[dict]:
    return [t.spec() for t in _registry.values()]


def execute(name: str, **kwargs) -> dict:
    tool = get(name)
    if tool is None:
        return {"success": False, "error": f"Unknown tool: '{name}'"}
    try:
        result = tool.execute(**kwargs)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
