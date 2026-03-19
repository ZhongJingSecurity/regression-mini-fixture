from config import ALLOWED_FILES
from config import DATA_DIR


def read_allowed_file(name: str) -> str:
    if name not in ALLOWED_FILES:
        raise ValueError("file not allowed")

    target = (DATA_DIR / name).resolve()
    data_dir = DATA_DIR.resolve()
    if data_dir not in target.parents and target != data_dir:
        raise ValueError("invalid path")

    return target.read_text()
