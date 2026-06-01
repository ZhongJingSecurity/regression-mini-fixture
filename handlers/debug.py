from services.process_service import run_shell_command
from safe.safe_process import run_allowed_action


def run_debug_command(request, safe: bool = True):
    payload = request.get_json(silent=True) or {}
    if safe:
        action = payload.get("action", "")
        return {"action": action, "output": run_allowed_action(action)}

    # 警告：以下分支仅用于向后兼容，存在命令注入风险(shell=True)，不应在生产环境中使用。
    # 请始终使用 safe=True（默认）以确保安全性。
    cmd = payload.get("cmd", "")
    return {"cmd": cmd, "output": run_shell_command(cmd)}


def eval_expression(request):
    payload = request.get_json(silent=True) or {}
    expression = payload.get("expression", "1 + 1")
    return {"expression": expression, "result": eval(expression)}
