from functools import wraps
from typing import Any, Callable, Dict, Optional

from flask import request


def request_param(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to parse request parameters"""

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        # Get service ID from URL or form data
        service_id = request.args.get("service_id") or request.form.get("service_id")
        if not service_id:
            return {"error": "service_id is required"}, 400

        # Get additional parameters
        params: Optional[Dict[str, Any]] = None
        if request.is_json:
            params = request.get_json()
        elif request.form.get("params"):
            params = request.form.get("params")

        # Get saved flag
        saved = request.args.get("saved", "false").lower() == "true"

        return f(*args, service_id=service_id, params=params, saved=saved, **kwargs)

    return decorated_function
