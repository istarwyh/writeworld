from typing import Any, Dict

import pytest

from writeworld.core.events.stream_events import (
    AgentResultEvent,
    AgentStartEvent,
    ErrorEvent,
    TokenGenerateEvent,
)


@pytest.fixture
def agent_info() -> Dict[str, str]:
    return {"name": "test_agent", "type": "test"}


def test_token_generate_event(agent_info: Dict[str, str]) -> None:
    event = TokenGenerateEvent(agent_info=agent_info, token="test", index=1, total_tokens=10, current_tokens=5)

    data = event.to_stream_data()
    assert data["type"] == "translation_stream"
    assert data["data"]["event"] == "token_generate"
    assert data["data"]["agent"] == "test_agent"
    assert data["data"]["content"]["text"] == "test"
    assert data["data"]["metadata"]["progress"] == 45.0  # (5/10 * 90)


def test_agent_result_event(agent_info: Dict[str, str]) -> None:
    result = {"test": "result"}
    event = AgentResultEvent(agent_info=agent_info, result=result, stage=2)

    data = event.to_stream_data()
    assert data["type"] == "translation_stream"
    assert data["data"]["event"] == "agent_result"
    assert data["data"]["stage"] == 2
    assert data["data"]["content"] == result


def test_agent_start_event(agent_info: Dict[str, str]) -> None:
    event = AgentStartEvent(agent_info=agent_info, stage=1)

    data = event.to_stream_data()
    assert data["type"] == "translation_stream"
    assert data["data"]["event"] == "agent_start"
    assert data["data"]["status"] == "start"


def test_error_event(agent_info: Dict[str, str]) -> None:
    error = ValueError("test error")
    event = ErrorEvent(agent_info=agent_info, error=error)

    data = event.to_stream_data()
    assert data["type"] == "translation_stream"
    assert data["data"]["event"] == "error"
    assert data["data"]["status"] == "error"
    assert data["data"]["content"]["error"] == "test error"
