from services.file_service import read_user_file
from safe.safe_files import read_allowed_file


def download_file(request):
    name = request.args.get("name", "")
    return {"name": name, "content": read_user_file(name)}


def safe_download_file(request):
    name = request.args.get("name", "")
    return {"name": name, "content": read_allowed_file(name)}
