"""Calculator tool — safe arithmetic without eval."""

import ast
import math
import operator

from .base import Tool


_SAFE_OP = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_SAFE_FUNCS = {
    "sqrt": math.sqrt,
    "abs": abs,
    "round": round,
    "floor": math.floor,
    "ceil": math.ceil,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
}


def _safe_eval(expr: str) -> float:
    """Evaluate a mathematical expression using a safe AST walker."""
    tree = ast.parse(expr.strip(), mode="eval")
    return _walk(tree.body)


def _walk(node) -> float:
    if isinstance(node, ast.Expression):
        return _walk(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"Unsupported constant: {node.value}")
    if isinstance(node, ast.UnaryOp):
        op = _SAFE_OP.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        return op(_walk(node.operand))
    if isinstance(node, ast.BinOp):
        op = _SAFE_OP.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        return op(_walk(node.left), _walk(node.right))
    if isinstance(node, ast.Call):
        func_name = node.func.id if isinstance(node.func, ast.Name) else None
        if func_name not in _SAFE_FUNCS:
            raise ValueError(f"Unsupported function: {func_name}")
        args = [_walk(a) for a in node.args]
        return _SAFE_FUNCS[func_name](*args)
    raise ValueError(f"Unsupported syntax: {type(node).__name__}")


class CalculatorTool(Tool):
    """Safe calculator supporting arithmetic, percentages, powers, and sqrt."""

    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations: arithmetic, percentages, powers, square roots, and parentheses.",
            category="Utilities",
            risk="safe",
        )

    def execute(self, expression: str) -> dict:
        try:
            cleaned = expression.replace("×", "*").replace("÷", "/").replace("^", "**")

            pct_match = __import__("re").search(r'([\d.]+)\s*%\s*of\s*([\d.]+)', cleaned)
            if pct_match:
                pct = float(pct_match.group(1))
                total = float(pct_match.group(2))
                value = (pct / 100.0) * total
                return {
                    "expression": expression,
                    "result": value,
                    "interpretation": f"{pct}% of {total}",
                }

            result = _safe_eval(cleaned)
            return {"expression": expression, "result": result}
        except Exception as e:
            return {"error": f"Calculation failed: {e}"}
