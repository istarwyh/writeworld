import json
from typing import Any, Dict, Generator, Iterator, List
from typing import Protocol as TypingProtocol

import pytest
import requests
import sseclient
from pytest import FixtureRequest
from requests.models import Response
from typing_extensions import Protocol


class SSEEvent(TypingProtocol):
    """Protocol defining the structure of SSE events."""

    @property
    def data(self) -> str:
        """Event data as string."""
        ...


class SSEClientProtocol(TypingProtocol):
    """Protocol defining the SSE client interface."""

    def events(self) -> Iterator[SSEEvent]:
        """Stream of SSE events."""
        ...


def response_to_generator(response: Response) -> Generator[bytes, None, None]:
    """Convert a Response object to a bytes generator for SSE."""
    for chunk in response.iter_content(chunk_size=None):
        if chunk:
            yield chunk


@pytest.fixture
def service_url() -> str:
    """Get the service URL for testing."""
    return "http://127.0.0.1:8888/service_run_stream"


@pytest.fixture
def headers() -> Dict[str, str]:
    """Get the headers for testing."""
    return {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }


def parse_sse_response(response: Response) -> List[Dict[str, Any]]:
    """
    Parse Server-Sent Events response into a list of events.

    Args:
        response: HTTP response containing SSE data

    Returns:
        List of parsed event data as dictionaries

    Raises:
        ValueError: If response is not a valid SSE stream
        json.JSONDecodeError: If event data is not valid JSON
        TypeError: If response is not a Response object
    """
    if not isinstance(response, Response):
        raise TypeError("Expected requests.Response object")

    if not response.headers.get("content-type", "").startswith("text/event-stream"):
        raise ValueError("Response is not a Server-Sent Events stream")

    # Convert response to bytes generator that SSEClient expects
    gen = response_to_generator(response)
    client = sseclient.SSEClient(gen)
    events: List[Dict[str, Any]] = []

    for event in client.events():
        if event.data:
            try:
                events.append(json.loads(event.data))
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(f"Failed to parse event data: {event.data}", e.doc, e.pos) from e

    return events


def test_chinese_to_english_translation(service_url: str, headers: Dict[str, str]) -> None:
    """
    Test Chinese to English translation with a classical Chinese poem line.

    Args:
        service_url: URL of the translation service
        headers: HTTP headers for the request

    Raises:
        AssertionError: If translation response doesn't match expected format
        requests.exceptions.RequestException: For HTTP request failures
    """
    # Arrange
    payload = {
        "service_id": "translation_service",
        "params": {
            "source_lang": "中文",
            "target_lang": "英文",
            "source_text": "台前一点绿，也学牡丹开",
        },
    }

    # Act
    try:
        response = requests.post(
            url=service_url,
            headers=headers,
            json=payload,
            stream=True,  # Important for SSE
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Request failed: {e}")

    # Assert
    events = parse_sse_response(response)
    assert len(events) > 0, "No translation events received"

    for event in events:
        assert isinstance(event, dict), f"Expected dict event, got {type(event)}"

        # Handle both old and new response formats
        translation = None
        if "result" in event:
            # New format: JSON string in result field
            result = json.loads(event["result"])
            assert isinstance(result, dict), f"Expected dict result, got {type(result)}"

            # Check for any *_agent_result field or output field
            for key in result:
                if key.endswith("_agent_result") or key == "output":
                    translation = result[key]
                    break
        elif "process" in event:
            # Old format: process field with agent results
            process = event["process"]
            assert isinstance(process, dict), f"Expected dict process, got {type(process)}"

            # Check for any *_agent_result field
            for key in process:
                if key.endswith("_agent_result"):
                    translation = process[key]
                    break

        assert translation is not None, f"No translation found in event: {event}"
        assert isinstance(translation, str), f"Translation should be string, got {type(translation)}"
        assert len(translation) > 0, "Translation should not be empty"


def test_translation_service_error_handling(service_url: str, headers: Dict[str, str]) -> None:
    """
    Test error handling with invalid input.

    Args:
        service_url: URL of the translation service
        headers: HTTP headers for the request

    Raises:
        AssertionError: If error handling doesn't work as expected
    """
    # Arrange
    invalid_payload = {
        "service_id": "translation_service",
        "params": {
            "source_lang": "invalid_language",
            "target_lang": "also_invalid",
            "source_text": "This should fail",
        },
    }

    # Act
    try:
        response = requests.post(
            url=service_url,
            headers=headers,
            json=invalid_payload,
            stream=True,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Request failed: {e}")

    # Assert
    events = parse_sse_response(response)
    assert len(events) > 0, "No events received"

    # Debug: Print all events to see what we're getting
    print("\nDebug: Events received:")
    for event in events:
        print(f"Event: {event}")

    has_error = False
    for event in events:
        if "result" in event:
            try:
                result = json.loads(event["result"])
                if isinstance(result, dict) and (
                    "error" in result
                    or any("error" in str(value).lower() for value in result.values())
                    or any(
                        "invalid" in str(value).lower() for value in result.values()
                    )  # Also check for "invalid" messages
                ):
                    has_error = True
                    break
            except json.JSONDecodeError:
                # If result is not valid JSON, check if it contains error message
                if "error" in str(event["result"]).lower() or "invalid" in str(event["result"]).lower():
                    has_error = True
                    break
        elif "process" in event:
            process = event["process"]
            if isinstance(process, dict) and (
                "error" in process
                or any("error" in str(value).lower() for value in process.values())
                or any(
                    "invalid" in str(value).lower() for value in process.values()
                )  # Also check for "invalid" messages
            ):
                has_error = True
                break
    assert has_error, "Expected error in response"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
