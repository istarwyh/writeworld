MCP 协议由一个 client 和多个 server 组成。用户发出请求后，client 会去调用 server 执行逻辑并返回给用户。client 就是用户的对话框，server 是一些我们提前写好的代码，用来完成我们想实现的系统调用。client 和 server 都可以自行开发。

本地 AI-Coding 就在 cline 基础上内置一些 MCP 和环境信息，Web 网站上就在 Nextjs 端做一下 MCP 即可。

[官方的SDK](https://modelcontextprotocol.io/quickstart/server)目前只能跑在本地，不支持远程。官方目前远程服务器。未来把 MCP Server 支持远程，就是真的数字劳工。

一个通用的MCP 数字劳工需要

### 屏幕截图解析（CV）
OmniParser V2
1）在用户界面中可靠地识别可交互图
2）理解屏幕截图中各种元素的语义
### 操作路径规划（NLP）
设计操作路径，并将预期操作准确地与屏幕上的相应区域相关联
Deepseek R1
### 模拟执行（RPA）
一个包含Windows 11的完整沙箱环境:[OmniTool](https://github.com/microsoft/OmniParser/tree/master/omnitool)
一个浏览器操作工具:Playright

考虑安全，使用OmniTool 可以在隔离容器中运行，确保系统安全。

官方demo 可以参考 OmniTool,技术实现可以参考：
<iframe width="560" height="315" src="https://www.youtube.com/embed/aBcedtGCA9I?si=k5degEHEMYJF-BtQ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>