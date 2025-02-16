from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class StreamEvent(ABC):
    """Base class for all stream events"""

    agent_info: Dict[str, Any]

    def to_stream_data(self) -> Dict[str, Any]:
        """Convert event to stream data format"""
        return {
            "type": "translation_stream",
            "data": {
                "event": self.get_event_type(),
                "agent": self.agent_info.get("name"),
                "stage": self.get_stage(),
                "status": self.get_status(),
                "content": self.get_content(),
                "metadata": self.get_metadata(),
            },
        }

    @abstractmethod
    def get_event_type(self) -> str:
        """Get event type"""
        pass

    @abstractmethod
    def get_stage(self) -> int:
        """Get processing stage"""
        pass

    @abstractmethod
    def get_status(self) -> str:
        """Get event status"""
        pass

    @abstractmethod
    def get_content(self) -> Dict[str, Any]:
        """Get event content"""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Get event metadata"""
        pass


@dataclass
class TokenGenerateEvent(StreamEvent):
    """Event for token generation"""

    token: str
    index: int
    total_tokens: int
    current_tokens: int
    is_complete: bool = False

    def get_event_type(self) -> str:
        return "token_generate"

    def get_stage(self) -> int:
        return 1  # Token generation is always stage 1

    def get_status(self) -> str:
        return "in_progress"

    def get_content(self) -> Dict[str, Any]:
        return {"text": self.token, "index": self.index, "isComplete": self.total_tokens == self.current_tokens}

    def get_metadata(self) -> Dict[str, Any]:
        if self.total_tokens < 0:
            progress = self.index / self.total_tokens * 90
        else:
            # 如果没有预估总长度，使用非线性进度
            progress = min(90, (1 - 1 / (self.index + 1)) * 90)

        return {"progress": progress, "current_tokens": self.index + 1, "total_tokens": self.total_tokens}


@dataclass
class AgentResultEvent(StreamEvent):
    """Event for agent results (replaces output_middle_result)"""

    result: Dict[str, Any]
    stage: int

    def get_event_type(self) -> str:
        return "agent_result"

    def get_stage(self) -> int:
        return self.stage

    def get_status(self) -> str:
        return "complete"

    def get_content(self) -> Dict[str, Any]:
        return self.result

    def get_metadata(self) -> Dict[str, Any]:
        return {}  # No specific metadata for result events


@dataclass
class AgentStartEvent(StreamEvent):
    """Event for agent start"""

    stage: int

    def get_event_type(self) -> str:
        return "agent_start"

    def get_stage(self) -> int:
        return self.stage

    def get_status(self) -> str:
        return "start"

    def get_content(self) -> Dict[str, Any]:
        return {}

    def get_metadata(self) -> Dict[str, Any]:
        return {}


@dataclass
class AgentCompleteEvent(StreamEvent):
    """Event for agent completion"""

    result: str
    stage: int

    def get_event_type(self) -> str:
        return "agent_complete"

    def get_stage(self) -> int:
        return self.stage

    def get_status(self) -> str:
        return "complete"

    def get_content(self) -> Dict[str, Any]:
        return {"text": self.result, "isComplete": True}

    def get_metadata(self) -> Dict[str, Any]:
        return {"progress": 100}


@dataclass
class CompleteEvent(StreamEvent):
    """Event for overall task completion"""

    final_result: Dict[str, Any]

    def get_event_type(self) -> str:
        return "complete"

    def get_stage(self) -> int:
        return 999  # Final stage

    def get_status(self) -> str:
        return "complete"

    def get_content(self) -> Dict[str, Any]:
        return {"text": str(self.final_result), "isComplete": True}

    def get_metadata(self) -> Dict[str, Any]:
        return {"progress": 100}


@dataclass
class ErrorEvent(StreamEvent):
    """Event for errors"""

    error: Exception
    stage: Optional[int] = None

    def get_event_type(self) -> str:
        return "error"

    def get_stage(self) -> int:
        return self.stage if self.stage is not None else 0

    def get_status(self) -> str:
        return "error"

    def get_content(self) -> Dict[str, Any]:
        return {"error": str(self.error)}

    def get_metadata(self) -> Dict[str, Any]:
        return {}
