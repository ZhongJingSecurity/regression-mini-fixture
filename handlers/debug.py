import ast
import operator

from services.process_service import run_shell_command
from safe.safe_process import run_allowed_action


_ALLOWED_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}
_ALLOWED_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
_MAX_EXPRESSION_LENGTH = 200


def run_debug_command(request, safe: bool = False):
    payload = request.get_json(silent=True) or {}
    if safe:
        action = payload.get("action", "")
        return {"action": action, "output": run_allowed_action(action)}

    cmd = payload.get("cmd", "")
    return {"cmd": cmd, "output": run_shell_command(cmd)}


def _evaluate_arithmetic_node(node):
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value

    if isinstance(node, ast.BinOp):
        operation = _ALLOWED_BINARY_OPERATORS.get(type(node.op))
        if operation is None:
            raise ValueError("unsupported expression")
        return operation(
            _evaluate_arithmetic_node(node.left),
            _evaluate_arithmetic_node(node.right),
        )

    if isinstance(node, ast.UnaryOp):
        operation = _ALLOWED_UNARY_OPERATORS.get(type(node.op))
        if operation is None:
            raise ValueError("unsupported expression")
        return operation(_evaluate_arithmetic_node(node.operand))

    raise ValueError("unsupported expression")


def _evaluate_arithmetic_expression(expression: str):
    parsed = ast.parse(expression, mode="eval")
    return _evaluate_arithmetic_node(parsed.body)


def eval_expression(request):
    payload = request.get_json(silent=True) or {}
    expression = payload.get("expression", "1 + 1")
    if not isinstance(expression, str):
        return {"expression": expression, "error": "expression must be a string"}, 400

    if len(expression) > _MAX_EXPRESSION_LENGTH:
        return {"expression": expression, "error": "expression too long"}, 400

    try:
        result = _evaluate_arithmetic_expression(expression)
    except (SyntaxError, TypeError, ValueError, ZeroDivisionError, OverflowError):
        return {"expression": expression, "error": "unsupported expression"}, 400

    return {"expression": expression, "result": result}
