import warnings
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pytest
from _pytest.config import Config


def pytest_configure(config: Config) -> None:
    """Configure pytest to ignore specific warnings."""
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", message=".*pkg_resources.*")
    warnings.filterwarnings("ignore", message=".*__fields__.*")
    warnings.filterwarnings("ignore", message=".*__get_validators__.*")
    warnings.filterwarnings("ignore", message=".*class-based.*config.*")
    warnings.filterwarnings("ignore", message=".*Pydantic.*")
    warnings.filterwarnings("ignore", message=".*langchain.*")
    warnings.filterwarnings("ignore", message=".*LangChainDeprecationWarning.*")


@pytest.fixture
def mock_llm_response() -> Generator[MagicMock, None, None]:
    """Mock LLM responses for testing."""
    with patch("langchain.llms.base.BaseLLM") as mock_llm:
        mock_llm.return_value.generate.return_value = MagicMock(
            generations=[MagicMock(text="Mocked translation response")]
        )
        yield mock_llm


@pytest.fixture
def sample_text() -> str:
    """Provide sample text for translation testing."""
    return "Hello world! This is a test."


@pytest.fixture
def sample_chinese_text() -> str:
    """Provide sample Chinese text for translation testing."""
    return "你好世界！这是一个测试。"


@pytest.fixture
def temp_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary file for testing."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Test content", encoding="utf-8")
    yield file_path
    if file_path.exists():
        file_path.unlink()


@pytest.fixture
def mock_translation_config() -> dict[str, Any]:
    """Provide mock translation configuration."""
    return {
        "source_lang": "en",
        "target_lang": "zh",
        "model_name": "test-model",
        "temperature": 0.7,
    }
