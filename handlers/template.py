from services.render_service import render_preview


def preview_template(request):
    template_text = request.args.get("tpl", "Hello {{ user }}")
    return {
        "preview": render_preview(template_text, {"user": "guest", "value": "demo"})
    }
