import ast
import operator


_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_ALLOWED_TYPES = (int, float, complex, str, bool, type(None))


def safe_eval_expression(expression: str) -> object:
    """Safely evaluate a mathematical/literal expression.
    
    Only allows literals (numbers, strings, booleans, None) and basic
    arithmetic operators. Disallows function calls, attribute access,
    variable names, etc.
    """
    try:
        tree = ast.parse(expression.strip(), mode="eval")
    except SyntaxError:
        raise ValueError("invalid expression syntax")
    
    return _eval_node(tree.body)


def _eval_node(node):
    if isinstance(node, ast.Constant):
        if not isinstance(node.value, _ALLOWED_TYPES):
            raise ValueError(f"unsupported constant type: {type(node.value).__name__}")
        return node.value
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPERATORS:
            raise ValueError(f"unsupported binary operator: {op_type.__name__}")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _ALLOWED_OPERATORS[op_type](left, right)
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPERATORS:
            raise ValueError(f"unsupported unary operator: {op_type.__name__}")
        operand = _eval_node(node.operand)
        return _ALLOWED_OPERATORS[op_type](operand)
    else:
        raise ValueError(f"unsupported expression node: {type(node).__name__}")
