from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type

from writeworld.core.events.stream_events import StreamEvent


class EventHandler(ABC):
    """Base class for event handlers"""

    @abstractmethod
    def can_handle(self, event: StreamEvent) -> bool:
        """Check if this handler can process the event"""
        pass

    @abstractmethod
    def handle(self, event: StreamEvent) -> None:
        """Process the event"""
        pass


class EventManager:
    """Manager for event handlers"""

    def __init__(self) -> None:
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._global_handlers: List[EventHandler] = []

    def register_handler(self, event_type: str, handler: EventHandler) -> None:
        """Register a handler for a specific event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def register_global_handler(self, handler: EventHandler) -> None:
        """Register a handler for all event types"""
        self._global_handlers.append(handler)

    def handle_event(self, event: StreamEvent) -> None:
        """Process an event with all registered handlers"""
        event_type = event.get_event_type()

        # Process with type-specific handlers
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                if handler.can_handle(event):
                    handler.handle(event)

        # Process with global handlers
        for handler in self._global_handlers:
            if handler.can_handle(event):
                handler.handle(event)


class LoggingEventHandler(EventHandler):
    """Handler for logging events"""

    def can_handle(self, event: StreamEvent) -> bool:
        return True

    def handle(self, event: StreamEvent) -> None:
        # Log event details
        print(f"Event: {event.get_event_type()}, Stage: {event.get_stage()}, Status: {event.get_status()}")


class ProgressEventHandler(EventHandler):
    """Handler for tracking progress"""

    def __init__(self, progress_callback: Callable[[float], None]) -> None:
        self.progress_callback = progress_callback

    def can_handle(self, event: StreamEvent) -> bool:
        return "progress" in event.get_metadata()

    def handle(self, event: StreamEvent) -> None:
        progress = event.get_metadata().get("progress", 0)
        self.progress_callback(progress)


class ErrorEventHandler(EventHandler):
    """Handler for error events"""

    def __init__(self, error_callback: Callable[[Exception], None]) -> None:
        self.error_callback = error_callback

    def can_handle(self, event: StreamEvent) -> bool:
        return event.get_event_type() == "error"

    def handle(self, event: StreamEvent) -> None:
        error = event.get_content().get("error")
        if error:
            self.error_callback(error)
