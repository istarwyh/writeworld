from typing import Any, Dict, Optional

from flask import Response, current_app, g
from flask.views import MethodView

from writeworld.api.decorators import request_param
from writeworld.core.task.stream_service_task import StreamServiceRequestTask
from writeworld.util.time_utils import timed_generator


class StreamServiceAPI(MethodView):
    """API endpoint for streaming translation service"""

    @request_param
    def post(self, service_id: str, params: Optional[Dict[str, Any]] = None, saved: bool = False) -> Response:
        """Handle POST request for streaming service

        Args:
            service_id: ID of the service to run
            params: Additional parameters for the service
            saved: Whether to save the result

        Returns:
            SSE response with streaming events
        """
        params = {} if params is None else params
        params["service_id"] = service_id

        # Create and configure task
        task = StreamServiceRequestTask(current_app.config["SERVICE_RUN_QUEUE"], saved, **params)

        # Create SSE response
        response = Response(timed_generator(task.stream_run(), g.start_time), mimetype="text/event-stream")

        # Add headers
        response.headers["X-Request-ID"] = task.request_id
        response.headers["Cache-Control"] = "no-cache"
        response.headers["Connection"] = "keep-alive"
        response.headers["X-Accel-Buffering"] = "no"

        return response


# Register route
def register_routes(app: Any) -> None:
    """Register stream service routes"""
    view = StreamServiceAPI.as_view("stream_service")
    app.add_url_rule("/stream_service", view_func=view, methods=["POST"])
