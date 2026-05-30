import shlex
import subprocess


def run_shell_command(cmd: str) -> str:
    args = shlex.split(cmd)
    result = subprocess.run(args, shell=False, capture_output=True, text=True)
    return result.stdout or result.stderr
