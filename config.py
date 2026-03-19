from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ALLOWED_FILES = {"sample.txt", "help.txt"}
ALLOWED_ACTIONS = {
    "status": ["/bin/echo", "status"],
    "version": ["/bin/echo", "version"],
}
