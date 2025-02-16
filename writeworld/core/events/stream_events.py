"""用于处理基于token级别的流式翻译输出的事件系统模块。

本模块实现了一个完整的流式翻译服务事件系统，用于实现前端打字机效果的Agent执行过程展示。
每个字段的前端应用说明：
- event: 用于前端判断当前事件类型，决定不同的UI渲染策略
- agent: 显示当前正在执行的Agent名称，用于用户了解翻译进度
- stage: 控制进度条和UI状态切换，对应翻译的不同阶段
- status: 控制动画效果和UI状态，如打字机开始、暂停、完成等
- content: 包含实际展示内容，如token文本、位置等
- metadata: 提供进度信息，用于进度条显示和动画控制

事件流程说明：
1. AgentStartEvent: 初始化UI组件，准备接收数据
2. TokenGenerateEvent: 逐个显示token，实现打字机效果
3. AgentResultEvent: 完成当前阶段，准备下一阶段
4. CompleteEvent: 结束所有动画，显示最终结果
5. ErrorEvent: 显示错误信息，中断动画

使用示例：
```typescript
// 前端事件处理示例
interface StreamEventData {
    event: EventType;
    agent: string;
    stage: TranslationStage;
    status: EventStatus;
    content: EventContent;
    metadata: EventMetadata;
}

// 打字机效果实现
function handleTokenGenerate(data: StreamEventData) {
    const { content, metadata } = data;
    // 根据token位置插入文本
    insertTokenAtPosition(content.text, content.index);
    // 更新进度条
    updateProgress(metadata.progress);
    // 控制打字速度
    setTypingDelay(calculateDelay(metadata.current_tokens));
}
```
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Literal, Optional, TypedDict


class EventType(Enum):
    """事件类型枚举，用于前端判断处理策略"""

    TOKEN_GENERATION = "token_generation"  # 生成单个token
    RELATE_QUESTION = "relate_question"  # 相关问题
    RELATE_ACTION = "relate_action"  # 相关动作
    ANSWER = "answer"  # 答案
    COMPLETE = "complete"  # 整体完成
    ERROR = "error"  # 错误


class EventStatus(Enum):
    """事件状态枚举，控制前端动画状态"""

    START = "start"  # 初始化，准备开始
    IN_PROGRESS = "in_progress"  # 正在执行，显示动画
    COMPLETE = "complete"  # 完成，结束动画
    ERROR = "error"  # 错误，中断动画


class TranslationStage(Enum):
    """翻译阶段枚举，控制进度展示"""

    INITIALIZATION = 0  # 初始化阶段
    REFLECTION = 20  # 反思阶段
    IMPROVE = 30  # 优化阶段
    PLANNING = 40  # 策划阶段
    EXECUTING = 50  # 执行阶段
    EXPRESSING = 60  # 表达阶段
    REVIEWING = 70  # 反思阶段
    FINAL = 999  # 最终阶段
    ERROR = 998  # 错误阶段


class EventContent(TypedDict, total=False):
    """事件内容类型定义"""

    text: str  # token文本或结果文本
    index: int  # token在序列中的位置
    isComplete: bool  # 是否完成
    error: Optional[str]  # 错误信息


class EventMetadata(TypedDict, total=False):
    """事件元数据类型定义"""

    progress: float  # 进度百分比
    current_tokens: int  # 当前token数
    total_tokens: int  # 总token数
    timestamp: float  # 时间戳，用于动画控制


@dataclass
class StreamEvent(ABC):
    """流式事件基类"""

    agent_info: Dict[str, Any]
    _validation_rules: List[str] = field(default_factory=list, init=False)
    _created_at: datetime = field(default_factory=datetime.now, init=False)

    def to_stream_data(self) -> Dict[str, Any]:
        """转换为前端所需的统一数据格式"""
        if not self.validate():
            raise ValueError(f"事件验证失败: {self._validation_rules}")

        return {
            "type": "translation_stream",
            "data": {
                "event": self.get_event_type().value,
                "agent": self.agent_info.get("name"),
                "stage": self.get_stage().value,
                "status": self.get_status().value,
                "content": self.get_content(),
                "metadata": self.get_metadata() | {"timestamp": self._created_at.timestamp()},
            },
        }

    def validate(self) -> bool:
        """验证事件数据的有效性"""
        self._validation_rules.clear()

        if not self.agent_info.get("name"):
            self._validation_rules.append("agent_info必须包含name字段")

        if not isinstance(self.get_stage(), TranslationStage):
            self._validation_rules.append("stage必须是TranslationStage枚举值")

        if not isinstance(self.get_status(), EventStatus):
            self._validation_rules.append("status必须是EventStatus枚举值")

        return len(self._validation_rules) == 0

    @abstractmethod
    def get_event_type(self) -> EventType:
        """获取事件类型"""
        pass

    @abstractmethod
    def get_stage(self) -> TranslationStage:
        """获取处理阶段"""
        pass

    @abstractmethod
    def get_status(self) -> EventStatus:
        """获取事件状态"""
        pass

    @abstractmethod
    def get_content(self) -> EventContent:
        """获取事件内容"""
        pass

    @abstractmethod
    def get_metadata(self) -> EventMetadata:
        """获取事件元数据"""
        pass


@dataclass
class TokenGenerateEvent(StreamEvent):
    """流中单个token生成的事件"""

    token: str
    index: int
    total_tokens: int
    current_tokens: int
    is_complete: bool = False

    def get_event_type(self) -> EventType:
        return EventType.TOKEN_GENERATION

    def get_stage(self) -> TranslationStage:
        if TranslationStage.REFLECTION.name.lower() in self.agent_info.get("name", ""):
            return TranslationStage.REFLECTION
        elif TranslationStage.IMPROVE.name.lower() in self.agent_info.get("name", ""):
            return TranslationStage.IMPROVE
        elif "work" in self.agent_info.get("name", ""):
            return TranslationStage.INITIALIZATION
        return TranslationStage.FINAL

    def get_status(self) -> EventStatus:
        return EventStatus.IN_PROGRESS

    def get_content(self) -> EventContent:
        return {"text": self.token, "index": self.index, "isComplete": self.total_tokens == self.current_tokens}

    def get_metadata(self) -> EventMetadata:
        if self.total_tokens > 0:
            progress = self.index / self.total_tokens * 90
        else:
            progress = max((self.total_tokens == self.current_tokens) * 100, (1 - 1 / (self.index + 1)) * 90)
        return {"progress": progress, "current_tokens": self.index + 1, "total_tokens": self.total_tokens}


@dataclass
class CompleteEvent(StreamEvent):
    """标识整个任务完成的事件"""

    final_result: Dict[str, Any]

    def get_event_type(self) -> EventType:
        return EventType.COMPLETE

    def get_stage(self) -> TranslationStage:
        return TranslationStage.FINAL

    def get_status(self) -> EventStatus:
        return EventStatus.COMPLETE

    def get_content(self) -> EventContent:
        return {"text": str(self.final_result), "isComplete": True}

    def get_metadata(self) -> EventMetadata:
        return {"progress": 100}


@dataclass
class ErrorEvent(StreamEvent):
    """翻译过程中的错误事件"""

    error: Exception
    stage: Optional[TranslationStage] = None

    def get_event_type(self) -> EventType:
        return EventType.ERROR

    def get_stage(self) -> TranslationStage:
        return self.stage if self.stage else TranslationStage.INITIALIZATION

    def get_status(self) -> EventStatus:
        return EventStatus.ERROR

    def get_content(self) -> EventContent:
        return {"error": str(self.error)}

    def get_metadata(self) -> EventMetadata:
        return {}
