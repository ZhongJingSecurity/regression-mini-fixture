from jinja2 import Template


def render_preview(user_template: str, context: dict) -> str:
    return Template(user_template).render(**context)
