from concurrent.futures import Future, ThreadPoolExecutor
from queue import Queue
from typing import Any, Dict, Optional
from uuid import uuid4


class RequestTask:
    """Base class for handling service requests"""

    def __init__(self, service_run_queue: Queue[Any], saved: bool = False, **kwargs: Any) -> None:
        self.service_run_queue = service_run_queue
        self.saved = saved
        self.kwargs = kwargs
        self.request_id = str(uuid4())
        self._executor = ThreadPoolExecutor(max_workers=1)

    def submit_task(self) -> Future[Any]:
        """Submit task to execution queue"""
        return self._executor.submit(self._run_task)

    def _run_task(self) -> Optional[Dict[str, Any]]:
        """Execute the task and return result"""
        try:
            # Put task in service queue
            self.service_run_queue.put((self.request_id, self.kwargs))
            return {"status": "success", "request_id": self.request_id}
        except Exception as e:
            return {"status": "error", "error": str(e)}
