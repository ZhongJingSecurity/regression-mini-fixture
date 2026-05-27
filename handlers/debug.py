from safe.safe_process import run_allowed_action


def run_debug_command(request, safe: bool = True):
    payload = request.get_json(silent=True) or {}
    action = payload.get("action", "")
    return {"action": action, "output": run_allowed_action(action)}


def eval_expression(request):
    payload = request.get_json(silent=True) or {}
    expression = payload.get("expression", "1 + 1")
    return {"expression": expression, "result": eval(expression)}
