import re


_PLACEHOLDER_PATTERN = re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}")


def render_preview(user_template: str, context: dict) -> str:
    def replace_placeholder(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in context:
            return match.group(0)
        return str(context[key])

    return _PLACEHOLDER_PATTERN.sub(replace_placeholder, user_template)
