import json
from concurrent.futures import Future
from queue import Queue
from typing import Any, Dict, Generator, Optional

from flask import g

from writeworld.core.events.stream_events import CompleteEvent, ErrorEvent, StreamEvent
from writeworld.core.task.request_task import RequestTask

EOF_SIGNAL = "EOF"


class StreamServiceRequestTask(RequestTask):
    """Task for handling streaming service requests"""

    def __init__(self, service_run_queue: Queue[Any], saved: bool = False, **kwargs: Any) -> None:
        super().__init__(service_run_queue, saved, **kwargs)
        self.event_queue: Queue[Any] = Queue()
        self.thread: Optional[Future[Any]] = None

    def stream_run(self) -> Generator[str, None, None]:
        """Run the service in streaming mode"""
        self.thread = self.submit_task()

        try:
            while True:
                event = self.event_queue.get()
                if event is None or event == EOF_SIGNAL:
                    break

                if isinstance(event, dict):  # Direct stream data
                    yield f"data: {json.dumps(event)}\n\n"
                elif isinstance(event, StreamEvent):  # StreamEvent instance
                    stream_data = event.to_stream_data()
                    yield f"data: {json.dumps(stream_data)}\n\n"

            # Get final result
            if self.thread:
                result = self.thread.result()
                if result:
                    if isinstance(result, dict):
                        complete_event = CompleteEvent(agent_info={"name": "StreamService"}, final_result=result)
                        yield f"data: {json.dumps(complete_event.to_stream_data())}\n\n"
        except Exception as e:
            error_event = ErrorEvent(agent_info={"name": "StreamService"}, error=e)
            yield f"data: {json.dumps(error_event.to_stream_data())}\n\n"

    def get_output_queue(self) -> Queue[Any]:
        """Get the event queue for streaming output"""
        return self.event_queue
