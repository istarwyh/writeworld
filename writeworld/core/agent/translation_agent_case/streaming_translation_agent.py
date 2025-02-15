# mypy: disable-error-code=import-not-found
from queue import Queue
from typing import Any, Dict, Optional, TypeVar, Union, cast

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.util.logging.logging_util import LOGGER
from pydantic import BaseModel, ConfigDict, Field

from writeworld.core.events.stream_events import (
    AgentResultEvent,
    AgentStartEvent,
    ErrorEvent,
    StreamEvent,
    TokenGenerateEvent,
)

T = TypeVar("T")


class StreamingTranslationAgent(Agent):  # type: ignore[misc]
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

    def start_agent(self, stage: int) -> None:
        """Signal the start of an agent's processing"""
        self.emit_event(AgentStartEvent(agent_info=self.agent_info, stage=stage))

    def emit_token(self, token: str, index: int, total_tokens: int, current_tokens: int) -> None:
        """Emit a token generation event"""
        self.emit_event(
            TokenGenerateEvent(
                agent_info=self.agent_info,
                token=token,
                index=index,
                total_tokens=total_tokens,
                current_tokens=current_tokens,
            )
        )

    def emit_result(self, result: Dict[str, Any], stage: int) -> None:
        """Emit an agent result event"""
        self.emit_event(AgentResultEvent(agent_info=self.agent_info, result=result, stage=stage))

    def emit_error(self, error: Exception, stage: Optional[int] = None) -> None:
        """Emit an error event"""
        self.emit_event(ErrorEvent(agent_info=self.agent_info, error=error, stage=stage))

    def parse_input(self, input_object: InputObject, agent_input: Dict[str, Any]) -> Dict[str, Any]:
        """Parse input and set up output stream"""
        for key in self.input_keys():
            agent_input[key] = input_object.get_data(key)
        return agent_input

    def execute_with_events(self, stage: int, agent_name: str, agent_input: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute an agent with event handling"""
        try:
            self.start_agent(stage)
            result = self.execute_agent(agent_name, agent_input)
            if result:
                result_dict = cast(Dict[str, Any], result.to_dict())
                self.emit_result(result_dict, stage)
                return result_dict
            return None
        except Exception as e:
            LOGGER.error(f"Error executing agent {agent_name}: {str(e)}")
            self.emit_error(e, stage)
            return None

    @staticmethod
    def execute_agent(agent_name: str, agent_input: Dict[str, Any]) -> Optional[OutputObject]:
        """Execute a single agent"""
        agent = cast(Agent, AgentManager().get_instance_obj(agent_name))
        return agent.execute(agent_input)
