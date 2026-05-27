from services.process_service import run_shell_command
from safe.safe_eval import safe_eval_expression
from safe.safe_process import run_allowed_action


def run_debug_command(request, safe: bool = False):
    payload = request.get_json(silent=True) or {}
    if safe:
        action = payload.get("action", "")
        return {"action": action, "output": run_allowed_action(action)}

    cmd = payload.get("cmd", "")
    return {"cmd": cmd, "output": run_shell_command(cmd)}


def eval_expression(request, safe: bool = False):
    payload = request.get_json(silent=True) or {}
    expression = payload.get("expression", "1 + 1")
    if safe:
        return {"expression": expression, "result": safe_eval_expression(expression)}
    return {"expression": expression, "result": eval(expression)}
