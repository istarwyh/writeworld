# mypy: disable-error-code=import-not-found
import unittest
import warnings
from pathlib import Path
from typing import ClassVar

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.agentuniverse import AgentUniverse


class TranslationAgentTest(unittest.TestCase):
    """
    Test cases for the translation agent.
    Tests both short and long text translation from English to Chinese.
    """

    agent_instance: ClassVar[Agent]
    data_dir: ClassVar[Path]

    @classmethod
    def setUpClass(cls) -> None:
        """Initialize the agent universe and get the translation agent instance."""
        AgentUniverse().start(config_path="config/config.toml")
        cls.agent_instance = AgentManager().get_instance_obj("translation_by_token_agent")
        cls.data_dir = Path("tests/fixtures/translation_data")

    def _translate_and_save(self, input_file: str, output_file: str) -> str:
        """
        Helper method to translate text from a file and save the result.

        Args:
            input_file: Name of the input file containing source text
            output_file: Name of the output file to save translation

        Returns:
            str: The translated text
        """
        with open(self.data_dir / input_file, "r") as f:
            source_text = f.read()

        output_object: OutputObject = self.agent_instance.run(
            source_lang="英文", target_lang="中文", source_text=source_text
        )

        translation = output_object.get_data("output")
        result = f"\nRag agent execution result is :\n{translation}"

        with open(self.data_dir / output_file, "w") as f:
            f.write(result)

        return result

    def test_short_text_translation(self) -> None:
        """Test translation of a short text."""
        result = self._translate_and_save("short_text.txt", "short_text_output.txt")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_long_text_translation(self) -> None:
        """Test translation of a long text."""
        result = self._translate_and_save("long_text.txt", "long_text_output.txt")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


if __name__ == "__main__":
    unittest.main()
