# mypy: disable-error-code=import-not-found
from abc import ABC, abstractmethod
from queue import Queue
from typing import Any, Dict, Optional, TypeVar, Union, cast

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.util.logging.logging_util import LOGGER
from pydantic import BaseModel, ConfigDict, Field

from writeworld.core.agent.event_stream_base_agent import EventStreamBaseAgent
from writeworld.core.events.stream_events import (
    ErrorEvent,
    StreamEvent,
    TranslationStage,
)

T = TypeVar("T")


class StreamingTranslationAgent(EventStreamBaseAgent, ABC):
    """Base class for streaming translation agents with event-based output"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    output_stream: Optional[Queue[Dict[str, Any]]] = Field(default=None, exclude=True)
    agent_info: Dict[str, str] = Field(default_factory=lambda: {"type": "translation"}, exclude=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        output_stream = kwargs.pop("output_stream", None)
        super().__init__(*args, **kwargs)
        self.output_stream = output_stream
        self.agent_info["name"] = self.__class__.__name__

    def emit_event(self, event: StreamEvent) -> None:
        """Emit a stream event to the output queue"""
        if self.output_stream:
            self.output_stream.put(event.to_stream_data())

    def emit_error(self, error: Exception, stage: Optional[int] = None) -> None:
        """Emit an error event"""
        self.emit_event(ErrorEvent(agent_info=self.agent_info, error=error, stage=TranslationStage.ERROR))

    def execute_with_events(
        self, input_object: InputObject, stage: int, agent_name: str, agent_input: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute an agent with event handling"""
        # 如果 self.output_stream 为空，使用 input_object 中的 output_stream
        if not self.output_stream:
            self.output_stream = input_object.get_data("output_stream")
        try:
            result = self.execute_agent(input_object, agent_name, agent_input)
            if result:
                # Handle both OutputObject and dict results
                result_dict = result.to_dict() if hasattr(result, "to_dict") else result
                if not isinstance(result_dict, dict):
                    LOGGER.error(f"Unexpected result type from agent {agent_name}: {type(result_dict)}")
                    return None
                return result_dict
            return None
        except Exception as e:
            LOGGER.error(f"Error executing agent {agent_name}: {str(e)}")
            self.emit_error(e, stage)
            return None

    @staticmethod
    def execute_agent(
        input_object: InputObject, agent_name: str, agent_input: Dict[str, Any]
    ) -> Optional[Union[OutputObject, Dict[str, Any]]]:
        """Execute a single agent"""
        agent = cast(Agent, AgentManager().get_instance_obj(agent_name))
        return agent.execute(input_object, agent_input)
