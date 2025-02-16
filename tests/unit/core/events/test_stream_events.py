from typing import Any, Dict

import pytest

from writeworld.core.events.stream_events import ErrorEvent, TokenGenerateEvent


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


def test_error_event(agent_info: Dict[str, str]) -> None:
    error = ValueError("test error")
    event = ErrorEvent(agent_info=agent_info, error=error)

    data = event.to_stream_data()
    assert data["type"] == "translation_stream"
    assert data["data"]["event"] == "error"
    assert data["data"]["status"] == "error"
    assert data["data"]["content"]["error"] == "test error"
