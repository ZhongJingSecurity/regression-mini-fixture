import ast
import operator

from services.process_service import run_shell_command
from safe.safe_process import run_allowed_action


_MAX_EXPRESSION_LENGTH = 200
_ALLOWED_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
}
_ALLOWED_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _safe_eval_arithmetic(expression: str):
    parsed = ast.parse(expression, mode="eval")
    return _evaluate_ast_node(parsed.body)


def _evaluate_ast_node(node):
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value

    if isinstance(node, ast.BinOp):
        operator_fn = _ALLOWED_BINARY_OPERATORS.get(type(node.op))
        if operator_fn is None:
            raise ValueError("Only basic arithmetic expressions are allowed")

        left = _evaluate_ast_node(node.left)
        right = _evaluate_ast_node(node.right)
        return operator_fn(left, right)

    if isinstance(node, ast.UnaryOp):
        operator_fn = _ALLOWED_UNARY_OPERATORS.get(type(node.op))
        if operator_fn is None:
            raise ValueError("Only basic arithmetic expressions are allowed")

        operand = _evaluate_ast_node(node.operand)
        return operator_fn(operand)

    raise ValueError("Only basic arithmetic expressions are allowed")


def run_debug_command(request, safe: bool = False):
    payload = request.get_json(silent=True) or {}
    if safe:
        action = payload.get("action", "")
        return {"action": action, "output": run_allowed_action(action)}

    cmd = payload.get("cmd", "")
    return {"cmd": cmd, "output": run_shell_command(cmd)}


def eval_expression(request):
    payload = request.get_json(silent=True) or {}
    expression = payload.get("expression", "1 + 1")

    if not isinstance(expression, str):
        return {"expression": expression, "error": "expression must be a string"}, 400

    if len(expression) > _MAX_EXPRESSION_LENGTH:
        return {"expression": expression, "error": "expression is too long"}, 400

    try:
        result = _safe_eval_arithmetic(expression)
    except (SyntaxError, TypeError, ValueError, ZeroDivisionError):
        return {
            "expression": expression,
            "error": "Only basic arithmetic expressions are allowed",
        }, 400

    return {"expression": expression, "result": result}
