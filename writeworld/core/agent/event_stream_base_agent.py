# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/12 19:36
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: agent.py
from abc import ABC, abstractmethod
from datetime import datetime
from queue import Queue
from threading import Thread
from typing import Any, Dict, List, Optional, TypeVar, Union, cast

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.memory_manager import MemoryManager
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.agent.plan.planner.planner_manager import PlannerManager
from agentuniverse.agent.plan.planner.react_planner.stream_callback import (
    InvokeCallbackHandler,
)
from agentuniverse.base.annotation.trace import trace_agent
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import (
    ApplicationConfigManager,
)
from agentuniverse.base.config.component_configer.configers.agent_configer import (
    AgentConfiger,
)
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.memory_util import generate_messages, get_memory_string
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel
from langchain_core.runnables import RunnableConfig, RunnableSerializable
from langchain_core.utils.json import parse_json_markdown
from pydantic import BaseModel, ConfigDict, Field

from writeworld.core.events.stream_events import StreamEvent, TokenGenerateEvent

T = TypeVar("T")


class EventStreamBaseAgent(Agent, ABC):
    """The parent class of all agent models, containing only attributes."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    output_stream: Optional[Queue[Dict[str, Any]]] = Field(default=None, exclude=True)

    def emit_event(self, event: StreamEvent) -> None:
        """Emit a stream event to the output queue"""
        if self.output_stream:
            self.output_stream.put(event.to_stream_data())

    def emit_token(self, token: str, index: int, total_tokens: int, current_tokens: int) -> None:
        """Emit a token generation event"""
        self.emit_event(
            TokenGenerateEvent(
                agent_info=self.agent_info,
                token=token,
                index=index,
                total_tokens=total_tokens,
                current_tokens=current_tokens,
            )
        )

    def invoke_chain(
        self, chain: RunnableSerializable[Any, str], agent_input: dict, input_object: InputObject, **kwargs: Any
    ) -> str:
        # 如果 self.output_stream 为空，使用 input_object 中的 output_stream
        if not self.output_stream:
            self.output_stream = input_object.get_data("output_stream")

        if not self.output_stream:
            res = chain.invoke(input=agent_input, config=self.get_run_config())
            return res

        result = []
        for i, token in enumerate(chain.stream(input=agent_input, config=self.get_run_config())):
            self.emit_token(token=token, index=i, total_tokens=-1, current_tokens=i + 1)  # 流式输出时无法知道总长度
        result.append(token)
        # 最后发送一个空白字符作为结束标志
        self.emit_token(token="", index=len(result), total_tokens=len(result) + 1, current_tokens=len(result) + 1)
        result.append("")

        return "".join(result)
