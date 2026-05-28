import ast

from services.process_service import run_shell_command
from safe.safe_process import run_allowed_action


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
    try:
        # 使用 ast.literal_eval 替代 eval，仅安全解析字面量，防止任意代码执行
        result = ast.literal_eval(expression)
    except (ValueError, SyntaxError):
        result = "Invalid expression"
    return {"expression": expression, "result": result}
