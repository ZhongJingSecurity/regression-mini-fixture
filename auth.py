def is_admin_from_query(request) -> bool:
    """Intentionally weak authorization check for the insecure admin route."""
    return request.args.get("is_admin") == "1"


def get_current_user(request) -> dict:
    """Return a simple user object from headers for the safe control route."""
    role = request.headers.get("X-Role", "user")
    return {"id": request.headers.get("X-User", "guest"), "role": role}


def require_admin(user: dict) -> None:
    if user.get("role") != "admin":
        raise PermissionError("admin role required")
