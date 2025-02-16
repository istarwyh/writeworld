from queue import Queue
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest
from agentuniverse.agent.input_object import InputObject

from writeworld.core.agent.translation_agent_case.streaming_translation_agent import (
    StreamingTranslationAgent,
)


class TestStreamingAgent(StreamingTranslationAgent):
    """Test implementation of StreamingTranslationAgent"""

    def __init__(self) -> None:
        super().__init__()
        self.agent_model = MagicMock()
        self.agent_model.profile = {"input_keys": ["test_input"], "output_keys": ["test_output"]}

    def input_keys(self) -> List[str]:
        return self.agent_model.profile.get("input_keys")

    def output_keys(self) -> List[str]:
        return self.agent_model.profile.get("output_keys")

    def parse_result(self, planner_result: Dict[str, Any]) -> Dict[str, Any]:
        return planner_result


@pytest.fixture  # type: ignore[misc]
def agent() -> StreamingTranslationAgent:
    return TestStreamingAgent()


@pytest.fixture  # type: ignore[misc]
def output_queue() -> Queue:
    return Queue()


@pytest.fixture  # type: ignore[misc]
def input_object(output_queue: Queue) -> InputObject:
    params = {"test_key": "test_value", "output_stream": output_queue}
    return InputObject(params=params)


def test_parse_input(agent: StreamingTranslationAgent, input_object: InputObject) -> None:
    agent_input: Dict[str, Any] = {}
    result = agent.parse_input(input_object, agent_input)

    assert "output_stream" not in result
    assert result["test_key"] == "test_value"
    assert agent.output_stream is not None


def test_emit_result(agent: StreamingTranslationAgent, output_queue: Queue) -> None:
    agent.output_stream = output_queue
    result = {"test": "result"}
    agent.emit_result(result, 2)

    event_data = output_queue.get_nowait()
    assert event_data["type"] == "translation_stream"
    assert event_data["data"]["event"] == "agent_result"
    assert event_data["data"]["content"] == result


def test_emit_error(agent: StreamingTranslationAgent, output_queue: Queue) -> None:
    agent.output_stream = output_queue
    error = ValueError("test error")
    agent.emit_error(error, 1)

    event_data = output_queue.get_nowait()
    assert event_data["type"] == "translation_stream"
    assert event_data["data"]["event"] == "error"
    assert "test error" in event_data["data"]["content"]["error"]


@patch("writeworld.core.agent.translation_agent_case.streaming_translation_agent.AgentManager")
def test_execute_with_events(
    mock_agent_manager: MagicMock, agent: StreamingTranslationAgent, output_queue: Queue
) -> None:
    agent.output_stream = output_queue
    mock_result = MagicMock()
    mock_result.to_dict.return_value = {"test": "result"}

    mock_agent = MagicMock()
    mock_agent.run.return_value = mock_result
    mock_agent_manager.return_value.get_instance_obj.return_value = mock_agent

    result = agent.execute_with_events(1, "test_agent", {})

    # Check start event
    start_event = output_queue.get_nowait()
    assert start_event["data"]["event"] == "agent_start"

    # Check result event
    result_event = output_queue.get_nowait()
    assert result_event["data"]["event"] == "agent_result"
    assert result == {"test": "result"}
