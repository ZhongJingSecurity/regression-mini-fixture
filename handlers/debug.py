from config import ALLOWED_ACTIONS
from services.process_service import run_shell_command
from safe.safe_process import run_allowed_action


def run_debug_command(request, safe: bool = False):
    payload = request.get_json(silent=True) or {}
    if safe:
        action = payload.get("action", "")
        return {"action": action, "output": run_allowed_action(action)}

    cmd = payload.get("cmd", "")
    # 白名单校验：只允许执行预定义的命令
    cmd_name = cmd.split()[0] if cmd else ""
    allowed_commands = {"echo", "ls", "cat", "pwd", "date", "whoami", "uptime"}
    if cmd_name not in allowed_commands:
        return {"cmd": cmd, "output": "Error: command not allowed"}

    return {"cmd": cmd, "output": run_shell_command(cmd)}


def eval_expression(request):
    payload = request.get_json(silent=True) or {}
    expression = payload.get("expression", "1 + 1")
    return {"expression": expression, "result": eval(expression)}
