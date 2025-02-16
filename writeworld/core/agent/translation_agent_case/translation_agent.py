import copy
from typing import Any, Dict, List, Optional, cast

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.agent.plan.planner.planner_manager import PlannerManager

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
        planner_base: Planner = PlannerManager().get_instance_obj(self.agent_model.plan.get("planner", {}).get("name"))
        agent_model = copy.deepcopy(self.agent_model)
        translation_type = input_object.get_data("execute_type")
        if translation_type == "multi":
            agent_model.profile["prompt_version"] = translation_type + "_" + agent_model.profile["prompt_version"]
        if input_object.get_data("country") and self.agent_model.info.get("name") == "translation_reflection_agent":
            agent_model.profile["prompt_version"] = "country_" + agent_model.profile["prompt_version"]
        planner_result: Dict[str, Any] = planner_base.invoke(agent_model, agent_input, input_object)
        return planner_result
