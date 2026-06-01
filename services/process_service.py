import subprocess
import warnings


def run_shell_command(cmd: str) -> str:
    """
    已废弃：此函数存在命令注入风险(shell=True)，请勿在生产环境使用。
    请使用 safe/safe_process.py 中的 run_allowed_action 替代。
    """
    warnings.warn(
        "run_shell_command is unsafe and deprecated. Use run_allowed_action instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout or result.stderr
