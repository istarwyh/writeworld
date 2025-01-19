import pytest
import requests
import json
from typing import Dict, Any, List
import sseclient

@pytest.fixture
def service_url() -> str:
    return "http://127.0.0.1:8888/service_run_stream"

@pytest.fixture
def headers() -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }

def parse_sse_response(response: requests.Response) -> List[Dict[str, Any]]:
    """Parse Server-Sent Events response into a list of events."""
    client = sseclient.SSEClient(response)
    events = []
    for event in client.events():
        if event.data:
            events.append(json.loads(event.data))
    return events

def test_chinese_to_english_translation(service_url: str, headers: Dict[str, str]):
    """Test Chinese to English translation with a classical Chinese poem line."""
    
    # Arrange
    payload = {
        "service_id": "translation_service",
        "params": {
            "source_lang": "中文",
            "target_lang": "英文",
            "source_text": "台前一点绿，也学牡丹开"
        }
    }
    
    # Act
    response = requests.post(
        url=service_url,
        headers=headers,
        json=payload,
        stream=True  # Important for SSE
    )
    
    # Assert
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    
    events = parse_sse_response(response)
    assert len(events) > 0, "Expected at least one SSE event"
    
    # Check the final event for the complete translation
    final_event = events[-1]
    assert "result" in final_event, "Response should contain result data"
    
    result_data = json.loads(final_event["result"])
    assert "output" in result_data, "Result should contain output field"
    assert isinstance(result_data["output"], str), "Output should be a string"
    assert len(result_data["output"]) > 0, "Output should not be empty"
    
    # Verify the translation contains key elements from the source text
    translation = result_data["output"].lower()
    assert any(word in translation for word in ["stage", "green", "peony", "bloom"]), (
        "Translation should contain key elements from the source text"
    )

def test_translation_service_error_handling(service_url: str, headers: Dict[str, str]):
    """Test error handling with invalid input."""
    
    # Arrange
    invalid_payload = {
        "service_id": "translation_service",
        "params": {
            "source_lang": "中文",
            "target_lang": "英文",
            # Missing source_text to test error handling
        }
    }
    
    # Act
    response = requests.post(
        url=service_url,
        headers=headers,
        json=invalid_payload,
        stream=True
    )
    
    # Assert
    events = parse_sse_response(response)
    assert len(events) > 0, "Expected at least one SSE event"
    
    # Check if any event contains error information
    has_error = any(
        "error" in event or 
        ("result" in event and isinstance(event["result"], str) and "error" in event["result"].lower())
        for event in events
    )
    assert has_error, "Expected an error message in the response"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
