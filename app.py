from flask import Flask, request

from handlers.admin import delete_user
from handlers.admin import safe_delete_user
from handlers.debug import eval_expression
from handlers.debug import run_debug_command
from handlers.fetch import fetch_url
from handlers.files import download_file
from handlers.files import safe_download_file
from handlers.template import preview_template


app = Flask(__name__)


@app.get("/download")
def download():
    return download_file(request)


@app.post("/admin/run")
def admin_run():
    return run_debug_command(request, safe=True)


@app.post("/debug/eval")
def debug_eval():
    return eval_expression(request)


@app.get("/preview")
def preview():
    return preview_template(request)


@app.get("/fetch")
def fetch():
    return fetch_url(request)


@app.post("/admin/users/delete")
def admin_delete():
    return delete_user(request)


@app.get("/safe/download")
def safe_download():
    return safe_download_file(request)


@app.post("/safe/run")
def safe_run():
    return run_debug_command(request, safe=True)


@app.post("/safe/admin/users/delete")
def safe_admin_delete():
    return safe_delete_user(request)


if __name__ == "__main__":
    app.run(debug=True)
