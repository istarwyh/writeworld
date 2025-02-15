# 流式翻译服务技术方案

## 1. 背景与目标

### 1.1 背景
- 当前翻译服务使用多 Agent 协作完成翻译任务
- LLM 已支持 token 级别的流式输出
- 需要提升用户体验，实现打字机效果

### 1.2 目标
- 实现真正的 token 级别流式输出
- 提供统一的消息格式
- 支持进度展示
- 为未来扩展提供灵活性

## 2. 系统设计

### 2.1 数据结构设计
```json
{
  "type": "translation_stream",
  "data": {
    "event": string,     // 事件类型，如 "token_generate", "error", "complete" 等
    "agent": string,     // Agent 名称，如 "translation_work_agent"
    "stage": number,     // 处理阶段，用于前端展示和状态管理
    "status": "start" | "in_progress" | "complete" | "error",
    "content": {
      "text": string,      // token 或完整文本
      "index": number,     // token 在当前内容中的位置
      "isComplete": boolean // 是否是当前事件的最后一个 token
    },
    "metadata": {
      "progress": number,  // 预估进度 0-100
      "total_tokens": number, // 预估总 token 数
      "current_tokens": number // 当前处理的 token 数
    }
  }
}
```

### 2.2 事件类型定义
- token_generate: token 生成事件
- agent_start: Agent 开始执行
- agent_complete: Agent 执行完成
- agent_result: Agent 中间结果（替代原有的 output_middle_result）
- error: 错误事件
- complete: 整体任务完成

### 2.3 进度计算方法
```python
progress = (current_tokens / total_tokens * 0.9) if not complete else 100
```

## 3. 实现方案

### 3.1 事件系统设计
#### 3.1.1 事件基类
```python
class StreamEvent:
    def __init__(self, agent_info: dict):
        self.agent_info = agent_info
        
    def to_stream_data(self) -> dict:
        """转换为统一的流式数据格式"""
        return {
            "type": "translation_stream",
            "data": {
                "event": self.get_event_type(),
                "agent": self.agent_info.get('name'),
                "stage": self.get_stage(),
                "status": self.get_status(),
                "content": self.get_content(),
                "metadata": self.get_metadata()
            }
        }
```

#### 3.1.2 具体事件实现
```python
class TokenGenerateEvent(StreamEvent):
    def __init__(self, agent_info: dict, token: str, index: int, total_tokens: int):
        super().__init__(agent_info)
        self.token = token
        self.index = index
        self.total_tokens = total_tokens
    
    def get_event_type(self) -> str:
        return "token_generate"

class AgentResultEvent(StreamEvent):
    """替代原有的 output_middle_result"""
    def __init__(self, agent_info: dict, result: dict):
        super().__init__(agent_info)
        self.result = result
    
    def get_event_type(self) -> str:
        return "agent_result"
    
    def get_content(self) -> dict:
        return self.result
```

### 3.2 核心组件实现

#### 3.2.1 Agent 实现
```python
class TranslationAgent(Agent):
    def execute_agents(self, input_object: InputObject, planner_input: dict) -> dict:
        work_agent = "translation_work_agent"
        reflection_agent = "translation_reflection_agent"
        improve_agent = "translation_improve_agent"

        output_stream = input_object.get_data('output_stream')
        
        # 工作 agent
        init_agent_result = self.execute_agent(work_agent, planner_input, input_object)
        # 发送 agent 结果事件（替代 output_middle_result）
        result_event = AgentResultEvent(
            self.agent_model.info,
            {"init_agent_result": init_agent_result.get_data("output")}
        )
        output_stream.put(result_event)
        
        # 其他 agent 类似处理...
        return improve_result.to_dict()

    def invoke_chain(self, chain: RunnableSerializable[Any, str], 
                    agent_input: dict, input_object: InputObject, **kwargs):
        output_stream = input_object.get_data('output_stream')
        if not output_stream:
            return chain.invoke(input=agent_input, config=self.get_run_config())
            
        # 发送 agent 开始事件
        start_event = AgentStartEvent(self.agent_model.info)
        output_stream.put(start_event)
        
        result = []
        for i, token in enumerate(chain.stream(input=agent_input, 
                                             config=self.get_run_config())):
            token_event = TokenGenerateEvent(
                self.agent_model.info,
                token,
                i,
                self.total_tokens
            )
            output_stream.put(token_event)
            result.append(token)
        
        # 发送 agent 完成事件
        complete_event = AgentCompleteEvent(
            self.agent_model.info,
            "".join(result)
        )
        output_stream.put(complete_event)
        return "".join(result)
```

#### 3.2.2 RequestTask 实现
```python
class StreamServiceRequestTask(RequestTask):
    def receive_steps(self):
        """处理流式事件"""
        while True:
            event = self.queue.get()
            if event is None or event == EOF_SIGNAL:
                break
                
            if isinstance(event, StreamEvent):
                stream_data = event.to_stream_data()
                yield "data:" + json.dumps(stream_data) + "\n\n"
            
        try:
            result = self.thread.result()
            if isinstance(result, OutputObject):
                result = result.to_dict()
            complete_event = CompleteEvent(result)
            yield "data:" + json.dumps(complete_event.to_stream_data()) + "\n\n"
        except Exception as e:
            error_event = ErrorEvent(str(e))
            yield "data:" + json.dumps(error_event.to_stream_data()) + "\n\n"
```

#### 3.2.3 Flask 路由实现
```python
@app.route("/stream_service", methods=['POST'])
@request_param
def stream_service(service_id: str, params: dict, saved: bool = False):
    params = {} if params is None else params
    params['service_id'] = service_id
    task = StreamServiceRequestTask(service_run_queue, saved, **params)
    response = Response(
        timed_generator(task.stream_run(), g.start_time),
        mimetype="text/event-stream"
    )
    response.headers['X-Request-ID'] = task.request_id
    return response
```

### 3.3 事件系统扩展
```python
class EventHandler:
    def __init__(self):
        self.handlers = {}
    
    def register(self, event_type: str, handler: Callable):
        self.handlers[event_type] = handler
    
    def handle(self, event: StreamEvent):
        handler = self.handlers.get(event.get_event_type())
        if handler:
            handler(event)
```

## 4. 后续优化

### 4.1 短期优化
- 优化 token 数量估算算法
- 添加更多事件类型支持
- 完善错误处理机制

### 4.2 长期规划
- 支持更多类型的 Agent
- 提供可配置的事件系统
- 添加监控和统计功能