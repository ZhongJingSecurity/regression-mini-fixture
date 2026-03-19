from auth import get_current_user
from auth import is_admin_from_query
from auth import require_admin


def delete_user(request):
    user_id = (request.get_json(silent=True) or {}).get("user_id", "unknown")
    if not is_admin_from_query(request):
        return {"deleted": False, "reason": "not admin"}
    return {"deleted": True, "user_id": user_id}


def safe_delete_user(request):
    current_user = get_current_user(request)
    require_admin(current_user)
    user_id = (request.get_json(silent=True) or {}).get("user_id", "unknown")
    return {"deleted": True, "user_id": user_id, "actor": current_user["id"]}
