# mypy: disable-error-code=import-not-found
# mypy: disable-error-code=import-untyped
# mypy: disable-error-code=import-not-found
from queue import Queue
from typing import Any, Dict, List, Optional, TypeVar, cast

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from langchain_text_splitters import RecursiveCharacterTextSplitter

from writeworld.core.agent.translation_agent_case.streaming_translation_agent import (
    StreamingTranslationAgent,
)


def calculate_chunk_size(token_count: int, token_limit: int) -> int:
    if token_count <= token_limit:
        return token_count

    num_chunks = (token_count + token_limit - 1) // token_limit
    chunk_size = token_count // num_chunks

    remaining_tokens = token_count % token_limit
    if remaining_tokens > 0:
        chunk_size += remaining_tokens // num_chunks

    return chunk_size


class TranslationAgent(StreamingTranslationAgent):
    def input_keys(self) -> List[str]:
        keys = self.agent_model.profile.get("input_keys", [])
        return cast(List[str], keys)

    def output_keys(self) -> List[str]:
        keys = self.agent_model.profile.get("output_keys", [])
        return cast(List[str], keys)

    def parse_result(self, planner_result: Dict[str, Any]) -> Dict[str, Any]:
        return planner_result

    def execute_agents(self, input_object: InputObject, planner_input: Dict[str, Any]) -> Dict[str, Any]:
        work_agent = "translation_work_agent"
        reflection_agent = "translation_reflection_agent"
        improve_agent = "translation_improve_agent"

        init_agent_result = self.execute_with_events(1, work_agent, planner_input)
        LOGGER.info(f"init_agent_result: {init_agent_result}")
        if not init_agent_result:
            return {"output": ""}

        planner_input["init_agent_result"] = init_agent_result.get("output", "")

        reflection_result = self.execute_with_events(2, reflection_agent, planner_input)
        LOGGER.info(f"reflection_result: {reflection_result}")
        if not reflection_result:
            return {"output": init_agent_result.get("output", "")}

        planner_input["reflection_agent_result"] = reflection_result.get("output", "")

        improve_result = self.execute_with_events(3, improve_agent, planner_input)
        LOGGER.info(f"improve_agent_result: {improve_result}")
        if not improve_result:
            return {"output": reflection_result.get("output", "")}

        return improve_result

    def execute(self, input_object: InputObject, agent_input: Dict[str, Any]) -> Dict[str, Any]:
        llm_name = cast(str, self.agent_model.profile.get("llm_model", {}).get("name"))
        llm: LLM = LLMManager().get_instance_obj(llm_name)
        source_text = cast(str, agent_input.get("source_text", ""))
        text_tokens = len(source_text)
        # 这里使用最大输入token，因为必须要保证有足够的token输出翻译结果
        if text_tokens < llm.max_tokens:
            return self.execute_agents(input_object, agent_input)

        agent_input["execute_type"] = "multi"
        chunk_result: List[str] = []
        chunk_size = calculate_chunk_size(text_tokens, llm.max_tokens)
        source_text_chunks = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0).split_text(
            source_text
        )

        for i in range(len(source_text_chunks)):
            tagged_text = (
                "".join(source_text_chunks[0:i])
                + "<TRANSLATE_THIS>"
                + source_text_chunks[i]
                + "</TRANSLATE_THIS>"
                + "".join(source_text_chunks[i + 1 :])
            )
            agent_input["chunk_to_translate"] = source_text_chunks[i]
            agent_input["tagged_text"] = tagged_text
            result = self.execute_agents(input_object, agent_input)
            if result and result.get("output"):
                chunk_result.append(cast(str, result.get("output")))

        return {"output": "".join(chunk_result)}
