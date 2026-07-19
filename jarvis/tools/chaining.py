"""Multi-step tool chaining — executes an ordered plan of tool calls."""

import json
import logging
from typing import Any

from ..config import MAX_CHAIN_STEPS

logger = logging.getLogger("jarvis.chaining")


class ChainPlan:
    """A bounded execution plan consisting of ordered tool steps."""

    def __init__(self, steps: list[dict], user_intent: str):
        self.steps = steps
        self.user_intent = user_intent.lower()
        self.results: list[dict] = []
        self.current_step = 0
        self.failed = False

    @property
    def is_complete(self) -> bool:
        return self.current_step >= len(self.steps) or self.failed

    @property
    def total_steps(self) -> int:
        return len(self.steps)


def build_chain(tool_calls: list[tuple[str, dict]], user_input: str) -> ChainPlan | None:
    """Build a ChainPlan from parsed tool calls.

    Returns ``None`` if no calls are provided.
    """
    if not tool_calls:
        return None

    steps = []
    for name, args in tool_calls:
        steps.append({"tool": name, "args": args})

    return ChainPlan(steps, user_input)


def execute_chain(
    chain: ChainPlan,
    execute_fn,
    print_fn=None,
    auto_confirm_write: bool = True,
) -> str:
    """Execute a ChainPlan step by step.

    * ``execute_fn`` — callable ``(name, **kwargs) -> dict`` that runs a tool.
    * ``print_fn`` — optional callable to emit progress messages.
    * ``auto_confirm_write`` — passed through to ``registry.execute``.

    Returns a human-readable summary string.
    """
    from ..main import ts, yellow, green, red
    if print_fn is None:
        print_fn = print

    chain.results = []
    chain.current_step = 0
    chain.failed = False

    if chain.total_steps > MAX_CHAIN_STEPS:
        msg = f"Request requires {chain.total_steps} steps (max: {MAX_CHAIN_STEPS}). Aborting."
        print_fn(ts(red(msg)))
        chain.failed = True
        return msg

    for i, step in enumerate(chain.steps):
        if chain.failed:
            break

        chain.current_step = i
        name = step["tool"]
        args = step["args"]
        print_fn(ts(yellow(f"  Step {i+1}/{chain.total_steps}: {name}...")))

        try:
            result = execute_fn(name, auto_confirm_write=auto_confirm_write, **args)
        except Exception as exc:
            result = {"success": False, "error": str(exc)}

        chain.results.append({"step": i, "tool": name, "result": result})

        if not result.get("success"):
            err = result.get("error", "Unknown error")
            print_fn(ts(red(f"  Step {i+1} failed: {err}")))
            chain.failed = True
            break

    # Build summary
    if chain.failed:
        summary_parts = [f"Chain failed at step {chain.current_step + 1}."]
        for r in chain.results:
            status = "✓" if r["result"].get("success") else "✗"
            summary_parts.append(f"  {status} {r['tool']}")
        return "\n".join(summary_parts)

    summary_parts = ["Completed all steps:"]
    for r in chain.results:
        summary_parts.append(f"  ✓ {r['tool']}")

    return "\n".join(summary_parts)
