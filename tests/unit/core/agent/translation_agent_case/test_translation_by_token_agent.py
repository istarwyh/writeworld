# mypy: disable-error-code=import-not-found
from queue import Queue
from typing import Any, Dict, cast
from unittest.mock import MagicMock, patch

import pytest
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject

from writeworld.core.agent.translation_agent_case.translation_by_token_agent import (
    TranslationAgent,
    calculate_chunk_size,
)
from writeworld.core.events.stream_events import TokenGenerateEvent


@pytest.fixture
def output_queue() -> Queue[Dict[str, Any]]:
    """Return a queue for testing output events"""
    return Queue()


@pytest.fixture
def agent(output_queue: Queue[Dict[str, Any]]) -> TranslationAgent:
    """Return a TranslationAgent instance for testing"""
    agent = TranslationAgent(output_stream=output_queue)
    agent.agent_model = MagicMock()
    agent.agent_model.profile = {
        "input_keys": ["source_text", "source_lang", "target_lang"],
        "output_keys": ["output"],
        "llm_model": {"name": "test_llm", "max_tokens": 1000},
    }
    return agent


@pytest.fixture
def input_object(output_queue: Queue[Dict[str, Any]]) -> InputObject:
    """Return a mock InputObject for testing"""
    params = {
        "source_lang": "en",
        "target_lang": "zh",
        "source_text": "Hello, world!",
        "output_stream": output_queue,
    }
    return InputObject(params)


def test_calculate_chunk_size() -> None:
    # When text is shorter than limit
    assert calculate_chunk_size(500, 1000) == 500

    # When text needs to be split
    assert calculate_chunk_size(2000, 1000) == 1000


@patch("writeworld.core.agent.translation_agent_case.translation_by_token_agent.LLMManager")
@patch("writeworld.core.agent.translation_agent_case.streaming_translation_agent.AgentManager")
def test_execute_single_chunk(
    mock_agent_manager: MagicMock,
    mock_llm_manager: MagicMock,
    agent: TranslationAgent,
    input_object: InputObject,
) -> None:
    # Setup mock LLM
    mock_llm = MagicMock()
    mock_llm.max_tokens = 1000
    mock_llm_manager.return_value.get_instance_obj.return_value = mock_llm

    # Setup mock agents
    mock_work_agent = MagicMock()
    mock_reflection_agent = MagicMock()
    mock_improve_agent = MagicMock()

    mock_work_result = MagicMock(spec=OutputObject)
    mock_work_result.to_dict.return_value = {"output": "work result"}
    mock_work_result.get_data.return_value = "work result"

    mock_reflection_result = MagicMock(spec=OutputObject)
    mock_reflection_result.to_dict.return_value = {"output": "reflection result"}
    mock_reflection_result.get_data.return_value = "reflection result"

    mock_improve_result = MagicMock(spec=OutputObject)
    mock_improve_result.to_dict.return_value = {"output": "final result"}
    mock_improve_result.get_data.return_value = "final result"

    mock_work_agent.run.return_value = mock_work_result
    mock_reflection_agent.run.return_value = mock_reflection_result
    mock_improve_agent.run.return_value = mock_improve_result

    mock_agent_manager.return_value.get_instance_obj.side_effect = [
        mock_work_agent,
        mock_reflection_agent,
        mock_improve_agent,
    ]

    result = agent.execute(input_object, {"source_text": "short text"})

    # Verify the result
    assert result == {"output": "final result"}

    # Verify events were emitted in correct order
    events = []
    while not input_object.get_data("output_stream").empty():
        events.append(input_object.get_data("output_stream").get_nowait())

    assert len(events) >= 6  # At least start and result events for each agent
    assert events[0]["data"]["event"] == "agent_start"  # First work agent start
    assert events[-2]["data"]["event"] == "agent_start"  # Last improve agent start
    assert events[-1]["data"]["event"] == "agent_result"  # Last improve agent result


@patch("writeworld.core.agent.translation_agent_case.translation_by_token_agent.LLMManager")
@patch("writeworld.core.agent.translation_agent_case.streaming_translation_agent.AgentManager")
def test_execute_multiple_chunks(
    mock_agent_manager: MagicMock,
    mock_llm_manager: MagicMock,
    agent: TranslationAgent,
    input_object: InputObject,
) -> None:
    # Setup mock LLM with small max_tokens to force chunking
    mock_llm = MagicMock()
    mock_llm.max_tokens = 10
    mock_llm_manager.return_value.get_instance_obj.return_value = mock_llm

    # Setup mock agents
    mock_agent = MagicMock()
    mock_result = MagicMock(spec=OutputObject)
    mock_result.to_dict.return_value = {"output": "chunk result"}
    mock_result.get_data.return_value = "chunk result"
    mock_agent.run.return_value = mock_result

    mock_agent_manager.return_value.get_instance_obj.return_value = mock_agent

    result = agent.execute(input_object, {"source_text": "this is a long text that needs chunking"})

    # Verify multiple chunks were processed
    assert mock_agent.run.call_count > 3  # More than one set of agent calls
    assert "output" in result
    assert isinstance(result["output"], str)


@patch("writeworld.core.agent.translation_agent_case.translation_by_token_agent.LLMManager")
@patch("writeworld.core.agent.translation_agent_case.streaming_translation_agent.AgentManager")
def test_execute_error_handling(
    mock_agent_manager: MagicMock,
    mock_llm_manager: MagicMock,
    agent: TranslationAgent,
    input_object: InputObject,
) -> None:
    # Setup mock LLM
    mock_llm = MagicMock()
    mock_llm.max_tokens = 1000
    mock_llm_manager.return_value.get_instance_obj.return_value = mock_llm

    # Setup mock agent to raise an error
    mock_agent = MagicMock()
    mock_agent.run.side_effect = ValueError("Test error")
    mock_agent_manager.return_value.get_instance_obj.return_value = mock_agent

    # Execute should not raise but handle the error
    result = agent.execute(input_object, {"source_text": "test text"})
    assert result == {"output": ""}  # Should return empty string for error case

    # Verify error event was emitted
    events = []
    while not input_object.get_data("output_stream").empty():
        events.append(input_object.get_data("output_stream").get_nowait())

    error_events = [e for e in events if e["data"]["event"] == "error"]
    assert len(error_events) > 0
    assert "Test error" in error_events[0]["data"]["content"]["error"]
