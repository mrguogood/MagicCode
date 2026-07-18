

# 一、V4简介

> 使用 Python 从零实现一个支持 Tool Calling（函数调用）的 AI Agent，不依赖 LangChain、LlamaIndex 等框架，帮助初学者理解 AI Agent 的底层运行原理。

项目主要演示：

- OpenAI Compatible API 调用
- Function Calling（工具调用）
- Agentic Loop（自主循环）
- Rich 终端美化
- Python 工程化项目组织
- Tool System（工具系统）

---

# 三、项目结构

> 整个项目采用模块化设计，每个文件职责单一，方便阅读和学习。

```
04-V4-Agent工具系统/
│
├── app.py                  # 程序入口
├── agent.py                # Agent 主循环
├── config.py               # 大模型配置 创建客户端 配置模型 读取 API Key
├── constants.py            # 项目常量 统一管理项目中的所有常量
├── prompt.py               # System Prompt 保存 System Prompt
├── tools.py                # Tool 定义 + Tool 执行 
├── history.py              # 聊天历史管理
├── console.py              # Rich UI
├── utils.py                # 公共工具
│
└── README.md
```

---

# 四、启动项目

运行：

```bash
python app.py
```
试着让它创建文件、读回来、修改它，或者执行命令。观察 Agentic Loop 的运作——AI 自主串联多个工具调用来完成你的请求。

---

# 五、目前支持的功能

目前已经支持以下工具。

| 工具 | 功能 |
|------|------|
| read_file | 读取文件 |
| write_file | 写入文件 |
| edit_file | 修改文件 |
| list_files | 查看目录 |
| search_code | 搜索代码 |
| run_command | 执行 Shell 命令 |

---

# 六、Agent 工作流程

整个 Agent 的工作流程如下：

```
用户输入

      │

      ▼

发送给 Qwen

      │

      ▼

模型判断

是否需要调用工具？

      │
 ┌────┴────┐
 │         │
 │         │
否         是
 │         │
 │         ▼
 │     Tool Calling
 │         │
 │         ▼
 │    Python 执行工具
 │         │
 │         ▼
 │   Tool 返回执行结果
 │         │
 └─────────┘
      │
      ▼
模型继续思考

      │

      ▼

输出最终答案
```

整个过程就是：

**Agentic Loop（Agent 自主循环）**

---


# 七、6 个工具 vs 生产级 Agent
你可能会问：6 个工具够用吗？看看 MagicCode 和 Claude Code等生产级 Agent 的对比：

| 能力          | MagicCode     | Claude Code |
| :------------ | :------------ | :---------- |
| 读文件        | `read_file`   | Read 工具   |
| 写文件        | `write_file`  | Write 工具  |
| 编辑文件      | `edit_file`   | Edit 工具   |
| 执行命令      | `run_command` | Bash 工具   |
| 列出目录      | `list_files`  | Glob 工具   |
| 搜索代码      | `search_code` | Grep 工具   |
| MCP 集成      | 未包含        | 支持        |
| 多文件 Diff   | 未包含        | 支持        |
| Notebook 编辑 | 未包含        | 支持        |
| 网页搜索      | 未包含        | 支持        |

Claude Code 大约有 15 个内置工具。我们的 6 个工具覆盖了日常使用场景的大约 **80%**。剩下的 20% 主要是 **MCP** 集成和 **Notebook** 编辑等高级功能——有用，但不是架构的核心。

# 八、后续五种扩展方向

> 基础已经打好。以下五种扩展能让 MagicCode 更接近生产级工具。

## 1. 权限确认

生产级 Agent 在写文件或执行命令前会征求确认：

```python
def execute_tool_with_confirm(name, params):
    # 只读操作：直接执行
    if name in ("read_file", "list_files", "search_code"):
        return execute_tool(name, params)

    # 写操作：需要用户批准
    console.print(f"[yellow]工具请求执行: {name}({params})[/]")
    confirm = console.input("[bold]允许？(y/n) [/]")
    if confirm.lower() == "y":
        return execute_tool(name, params)
    return "User denied this operation"
```



## 2. 项目上下文加载

Claude Code 会自动读取项目根目录的 CLAUDE.md来理解上下文。你也可以这样做：

```python
def load_project_context():
    """加载项目配置文件作为上下文。"""
    context = ""
    for name in ["CLAUDE.md", "AGENTS.md", "README.md"]:
        if os.path.exists(name):
            with open(name, "r") as f:
                context += f"\n\n--- {name} ---\n{f.read()}"
    return context

# 追加到系统提示词
project_ctx = load_project_context()
if project_ctx:
    SYSTEM_PROMPT += f"\n\n## Project Context\n{project_ctx}"
```



## 3. 随意切换模型

MagicCode 不绑定 GPT。任何支持 Function Calling 的模型都能用。OpenAI SDK 的兼容接口让切换变得轻而易举：

```python
from openai import OpenAI

# DeepSeek
client = OpenAI(api_key="your-key", base_url="https://api.deepseek.com/v1")

# 本地 Ollama
client = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
```



这也是本教程使用 OpenAI SDK 的原因之一——它是事实上的标准接口，几乎所有模型提供商都提供兼容端点。

## 4. 对话持久化

目前退出程序后对话历史就丢了。用 JSON 把它保存下来：

```python
import json

HISTORY_FILE = ".magiccode_history.json"

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, ensure_ascii=False, default=str)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []
```



## 5. Token 用量追踪

API 调用是要花钱的。加个用量追踪很简单：

```python
total_input_tokens = 0
total_output_tokens = 0

# 每次 API 调用后：
total_input_tokens += response.usage.prompt_tokens
total_output_tokens += response.usage.completion_tokens

# 退出时：
console.print(f"[dim]Token 统计 — 输入: {total_input_tokens} | 输出: {total_output_tokens}[/]")
```

# 九、常见问题和解决办法

构建第一个 Agent 时，你大概率会踩几个坑。应对方法如下：

| 问题                      | 原因                           | 解决方案                                      |
| :------------------------ | :----------------------------- | :-------------------------------------------- |
| `tool_call_id` 不匹配报错 | 工具结果没引用正确的调用 ID    | 始终使用响应中的 `tool_call.id`，不要自己生成 |
| Agent 无限循环            | 没有退出条件或模型一直调用工具 | 加 `tool_count` 限制（我们用的是 20）         |
| 模型不用工具              | 工具描述太模糊                 | 写具体、可操作的描述                          |
| 大文件导致崩溃            | 整个文件读进内存               | 加文件大小检查，截断大文件                    |
| 命令卡住                  | `subprocess.run` 没设超时      | 始终设置 `timeout=30`（或合适的值）           |


# 七、总结
它通过不到千行的 Python 代码，实现了一个具备自主调用工具能力的终端 AI 助手。

学习完成本项目后，你将能够理解：

- 大模型如何调用工具
- Agent 为什么能够自主完成任务
- Tool Calling 的底层原理
- Agentic Loop 的执行流程
- 如何从零构建一个属于自己的 AI Agent

在此基础上，再学习 LangChain、Spring AI、AutoGen、CrewAI 等框架时，将更加轻松，也能更深入地理解它们背后的设计思想。