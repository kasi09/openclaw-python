"""Math Skill - Mathematical evaluation, unit conversion, and statistics for OpenClaw."""

import ast
import math
import operator
import statistics as stats_mod
from typing import Any

from openclaw_python_skill.skill import Skill

# Allowed binary operators for safe expression evaluation
_BINARY_OPS: dict[type, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

# Allowed unary operators
_UNARY_OPS: dict[type, Any] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

# Allowed math functions and constants
_MATH_NAMES: dict[str, Any] = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "abs": abs,
    "round": round,
    "ceil": math.ceil,
    "floor": math.floor,
    "pi": math.pi,
    "e": math.e,
}

# Unit conversion tables: unit -> (category, factor_to_base)
# Base units: meter (length), gram (weight), second (time)
_UNIT_TABLE: dict[str, tuple[str, float]] = {
    # Length (base: meter)
    "m": ("length", 1.0),
    "km": ("length", 1000.0),
    "cm": ("length", 0.01),
    "mm": ("length", 0.001),
    "mi": ("length", 1609.344),
    "ft": ("length", 0.3048),
    "in": ("length", 0.0254),
    # Weight (base: gram)
    "kg": ("weight", 1000.0),
    "g": ("weight", 1.0),
    "mg": ("weight", 0.001),
    "lb": ("weight", 453.59237),
    "oz": ("weight", 28.349523125),
    # Time (base: second)
    "s": ("time", 1.0),
    "min": ("time", 60.0),
    "h": ("time", 3600.0),
    "d": ("time", 86400.0),
}

# Temperature units need special handling (non-linear)
_TEMP_UNITS = {"C", "F", "K"}


def _safe_eval(expression: str) -> float:
    """Safely evaluate a mathematical expression using AST parsing."""
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as err:
        raise ValueError(f"Invalid expression: {expression}") from err
    return _eval_node(tree.body)


def _eval_node(node: ast.expr) -> float:
    """Recursively evaluate an AST node."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)

    if isinstance(node, ast.Name):
        if node.id in _MATH_NAMES:
            val = _MATH_NAMES[node.id]
            if isinstance(val, float):
                return val
        raise ValueError(f"Unknown name: {node.id}")

    if isinstance(node, ast.BinOp):
        op_func = _BINARY_OPS.get(type(node.op))
        if op_func is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        return float(op_func(_eval_node(node.left), _eval_node(node.right)))

    if isinstance(node, ast.UnaryOp):
        op_func = _UNARY_OPS.get(type(node.op))
        if op_func is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        return float(op_func(_eval_node(node.operand)))

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function calls are allowed")
        func_name = node.func.id
        if func_name not in _MATH_NAMES:
            raise ValueError(f"Unknown function: {func_name}")
        func = _MATH_NAMES[func_name]
        if not callable(func):
            raise ValueError(f"{func_name} is not a function")
        args = [_eval_node(arg) for arg in node.args]
        return float(func(*args))

    raise ValueError(f"Unsupported expression element: {type(node).__name__}")


def _convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Convert between temperature units (C, F, K)."""
    # Convert to Celsius first
    if from_unit == "C":
        celsius = value
    elif from_unit == "F":
        celsius = (value - 32) * 5 / 9
    else:  # K
        celsius = value - 273.15

    # Convert from Celsius to target
    if to_unit == "C":
        return celsius
    elif to_unit == "F":
        return celsius * 9 / 5 + 32
    else:  # K
        return celsius + 273.15


class MathSkill(Skill):
    """Evaluate math expressions, convert units, and compute statistics.

    Provides actions for:
    - evaluate: Safely evaluate mathematical expressions
    - convert_units: Convert between units (length, weight, temperature, time)
    - statistics: Compute statistical measures on a list of numbers
    """

    def __init__(self) -> None:
        super().__init__(name="math", version="1.0.0")

    def process(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if action == "evaluate":
            return self._evaluate(parameters)
        elif action == "convert_units":
            return self._convert_units(parameters)
        elif action == "statistics":
            return self._statistics(parameters)
        else:
            raise ValueError(f"Unknown action: {action}")

    def _evaluate(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Safely evaluate a mathematical expression."""
        expression = parameters.get("expression")
        if not expression:
            raise ValueError("Missing required parameter: expression")

        result = _safe_eval(str(expression))
        return {"expression": str(expression), "result": result}

    def _convert_units(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Convert a value between units."""
        value = parameters.get("value")
        if value is None:
            raise ValueError("Missing required parameter: value")
        from_unit = parameters.get("from_unit")
        if not from_unit:
            raise ValueError("Missing required parameter: from_unit")
        to_unit = parameters.get("to_unit")
        if not to_unit:
            raise ValueError("Missing required parameter: to_unit")

        value = float(value)

        # Temperature special case
        if from_unit in _TEMP_UNITS and to_unit in _TEMP_UNITS:
            result = _convert_temperature(value, from_unit, to_unit)
            return {
                "value": value,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "result": round(result, 6),
            }

        # Standard unit conversion via base unit
        if from_unit not in _UNIT_TABLE:
            raise ValueError(f"Unknown unit: {from_unit}")
        if to_unit not in _UNIT_TABLE:
            raise ValueError(f"Unknown unit: {to_unit}")

        from_cat, from_factor = _UNIT_TABLE[from_unit]
        to_cat, to_factor = _UNIT_TABLE[to_unit]

        if from_cat != to_cat:
            raise ValueError(
                f"Incompatible units: {from_unit} ({from_cat}) and {to_unit} ({to_cat})"
            )

        result = value * from_factor / to_factor
        return {
            "value": value,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "result": round(result, 6),
        }

    def _statistics(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Compute statistics on a list of numbers."""
        numbers = parameters.get("numbers")
        if numbers is None:
            raise ValueError("Missing required parameter: numbers")
        if not isinstance(numbers, list) or len(numbers) == 0:
            raise ValueError("Parameter 'numbers' must be a non-empty list")

        nums = [float(n) for n in numbers]
        operation = parameters.get("operation", "summary")

        if operation == "summary":
            stdev = stats_mod.stdev(nums) if len(nums) >= 2 else 0.0
            variance = stats_mod.variance(nums) if len(nums) >= 2 else 0.0
            return {
                "numbers": nums,
                "count": len(nums),
                "mean": stats_mod.mean(nums),
                "median": stats_mod.median(nums),
                "stdev": round(stdev, 6),
                "variance": round(variance, 6),
                "min": min(nums),
                "max": max(nums),
                "sum": sum(nums),
            }

        ops: dict[str, Any] = {
            "mean": lambda: stats_mod.mean(nums),
            "median": lambda: stats_mod.median(nums),
            "stdev": lambda: stats_mod.stdev(nums) if len(nums) >= 2 else 0.0,
            "variance": lambda: stats_mod.variance(nums) if len(nums) >= 2 else 0.0,
            "min": lambda: min(nums),
            "max": lambda: max(nums),
            "sum": lambda: sum(nums),
        }

        if operation not in ops:
            raise ValueError(
                f"Unknown operation: {operation}. Supported: summary, {', '.join(sorted(ops))}"
            )

        return {
            "numbers": nums,
            "count": len(nums),
            "operation": operation,
            "result": ops[operation](),
        }
