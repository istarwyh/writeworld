import copy
from typing import Any, Dict, List, Optional, cast

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.base.util.agent_util import (
    assemble_memory_input,
    assemble_memory_output,
)
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt

from writeworld.core.agent.event_stream_base_agent import EventStreamBaseAgent


class TranslationAgent(EventStreamBaseAgent):
    def input_keys(self) -> List[str]:
        keys: List[str] = self.agent_model.profile.get("input_keys", [])
        return keys

    def output_keys(self) -> List[str]:
        keys: List[str] = self.agent_model.profile.get("output_keys", [])
        return keys

    def parse_input(self, input_object: InputObject, agent_input: Dict[str, Any]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key in input_object.to_dict():
            result[key] = input_object.get_data(key)
        return result

    def parse_result(self, planner_result: Dict[str, Any]) -> Dict[str, Any]:
        return planner_result

    def execute(self, input_object: InputObject, agent_input: Dict[str, Any]) -> Dict[str, Any]:
        agent_model = copy.deepcopy(self.agent_model)
        translation_type = input_object.get_data("execute_type")
        if translation_type == "multi":
            agent_model.profile["prompt_version"] = translation_type + "_" + agent_model.profile["prompt_version"]
        if input_object.get_data("country") and self.agent_model.info.get("name") == "translation_reflection_agent":
            agent_model.profile["prompt_version"] = "country_" + agent_model.profile["prompt_version"]
        memory: Memory = self.process_memory(agent_input, **input_object.to_dict())
        llm: LLM = self.process_llm(**input_object.to_dict())
        prompt: Prompt = self.process_prompt(agent_input, **input_object.to_dict())
        result: Dict[str, Any] = self.customized_execute(
            input_object, agent_input, memory, llm, prompt, **input_object.to_dict()
        )
        return result
