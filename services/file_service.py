from config import DATA_DIR


def read_user_file(user_supplied_name: str) -> str:
    target = DATA_DIR / user_supplied_name
    return target.read_text()
