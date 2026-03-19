import subprocess

from config import ALLOWED_ACTIONS


def run_allowed_action(action: str) -> str:
    if action not in ALLOWED_ACTIONS:
        raise ValueError("action not allowed")

    result = subprocess.run(ALLOWED_ACTIONS[action], capture_output=True, text=True)
    return result.stdout or result.stderr
