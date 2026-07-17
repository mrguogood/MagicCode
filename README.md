# 用 Python 从零构建 AI 编程 Agent（完整实战教程）

用 Python 从零构建 AI 编程 Agent：代码实现 Agentic Loop + Function Calling，带读写文件、执行命令、搜索代码等 6 个工具。从 20 行的基础对话到完整 Agent 分四个版本递进，不用框架，理解 Claude Code 们的底层架构。

每一款 AI 编程工具——[Claude Code](https://www.heyuan110.com/zh/posts/ai/2026-02-28-claude-code-complete-guide/)、Cursor、Copilot——底层跑的都是同一套架构。这篇教程带你亲手搭建这套架构：一个终端 AI 编程 Agent，从零开始，能读文件、写代码、跑命令、自主做多步决策。

不用框架，不加抽象层，只有 Python 和对 AI Agent 运行原理的透彻理解。

## 我们要做什么

教程结束时，你会得到一个名为 **MagicCode** 的 AI 编程 Agent，它能：

- 读写项目中的文件
- 执行 Shell 命令并观察结果
- 在代码库中搜索模式
- 对现有文件做精确编辑
- 自主串联多个操作来完成复杂任务

我们分四个版本逐步构建：

| 版本 | 功能              |  核心概念                        |
| :--- | :---------------- | :------------------------------ |
| V1   | 基础对话          |Chat Completions API            |
| V2   | 流式输出          |Token 流式传输                  |
| V3   | 富文本终端        |Markdown 渲染                   |
| V4   | 完整 Agent + 工具 |Agentic Loop + Function Calling |

每个版本都能独立运行，随时可以停下来，手里都有一个可用的东西。

## 为什么要从零构建 AI Agent？

用 AI 编程工具是一回事，理解它怎么工作是另一回事。

当你理解了架构，就能定制它、扩展它、调试它，或者在同样的基础上造出全新的东西。本教程要讲的三个概念——**Agentic Loop**、**工具调用（Function Calling）**和**消息协议**——正是当今市面上每一款 AI 编程 Agent 的核心。

这也是一次**上下文工程**的实战练习——设计 AI 接收什么信息、以何种方式接收。你在本教程中编写的系统提示词、工具定义和对话历史，都是直接影响 Agent 质量的上下文工程决策。

## 架构解析：Agent 和聊天机器人的本质区别

动手写代码之前，先回答一个根本问题：**AI Agent 和普通聊天机器人到底差在哪？**

### 聊天机器人 vs. Agent

聊天机器人回复消息，Agent 采取行动。

```fallback
聊天机器人：
  你："写个 hello world 程序。"
  AI："代码如下：print('hello world')"
  你：（手动复制粘贴、保存、运行）

Agent：
  你："写个 hello world 程序。"
  AI：（创建 hello.py → 写入代码 → 运行 → 报告结果）
```

区别就在于**工具调用**。Agent 拥有工具——读文件、写文件、执行命令——并且自主决定何时、如何使用它们。

### Agentic Loop

实现自主行为的核心模式叫做 **Agentic Loop**：

```fallback
┌─────────────────────────────────────────────┐
│                                             │
│   用户发送消息                                │
│       ↓                                     │
│   LLM 接收消息 + 工具定义                     │
│       ↓                                     │
│   LLM 决策：回复文本还是调用工具？              │
│       ↓                                     │
│   ┌─ 文本回复 → 返回给用户                    │
│   │                                         │
│   └─ 工具调用 → 执行工具                      │
│          ↓                                  │
│      将结果发回 LLM                           │
│          ↓                                  │
│      LLM 再次决策（循环）──────────┐           │
│                                   │         │
│      （重复直到任务完成）  ◄────────┘          │
│                                             │
└─────────────────────────────────────────────┘
```
这就是多步推理的实现方式。AI 不是给你一个一次性答案，而是像开发者一样工作：看代码、思考要做什么、做修改、验证结果、重复。

### Function Calling 的工作原理

OpenAI 和 Anthropic 的 API 都原生支持工具调用（OpenAI 称之为 “Function Calling”）：

1. **你定义工具**——名称、描述、参数 Schema——传给 API
2. **LLM 选择**在回复中调用一个或多个工具
3. **你的代码执行**工具，将结果以 `role: "tool"` 消息的形式发回
4. **LLM 继续**基于结果进行推理

关键洞察：**AI 从不亲自执行工具。** 它只决定调用*哪个*工具、传递*什么参数*。实际执行全由你的 Python 代码负责。这就是安全基础——执行边界完全在你掌控之中。

## 环境准备

你需要三样东西：

- **Python 3.10+**（推荐 3.12+）
- **AGENT_API_KEY**，// 该教程使用阿里云百炼模型，阿里云百炼提供的免费额度对初学者而言够用了
- **一个终端**（任何终端都行）

### 项目初始化

```bash
mkdir MagicCode && cd MagicCode

// Python 中创建虚拟环境的标准命令，用于隔离不同项目的依赖包 .venv虚拟环境的文件夹名称（可以改成任意名字，如 .venv、myenv）
python -m venv .venv 
source .venv/bin/activate  # Windows: .venv\Scripts\activate

// openai 只是一个 Python 客户端 SDK。由于阿里云百炼提供了 OpenAI Compatible API（兼容 OpenAI 接口），因此可以直接复用这个SDK，只需要将 base_url 改为百炼的地址，并使用 AGENT_API_KEY 即可。
// 百炼客户端 SDK: pip install dashscope rich prompt_toolkit
pip install openai rich prompt_toolkit   
```

三个依赖：

| 库               | 用途                                |
| :--------------- | :---------------------------------- |
| `openai`         | API 调用，原生支持 Function Calling |
| `rich`           | Markdown 渲染、语法高亮、面板       |
| `prompt_toolkit` | 增强终端输入，支持历史记录          |

### 配置 API Key

为了方便程序读取 API Key，我们将其保存到环境变量中。不同操作系统的设置方法如下：

```bash
Windows
$env:AGENT_API_KEY="你的APIKey"

Windows（永久生效）
setx AGENT_API_KEY "你的APIKey"

Linux/macOS
export AGENT_API_KEY="你的APIKey"
```

如果希望每次打开终端都自动生效，可以把上面的 `export` 命令添加到用户主目录下的 `~/.bashrc`（Bash）或 `~/.zshrc`（Zsh）配置文件中。如果文件不存在，可以自行创建。

## V1：打地基
从最简单的开始。V1 就是一个朴素的对话循环——没有流式输出、没有工具、没有 UI。验证 API 调用能跑通。

### 运行

```bash
python v1_basic.py
```

### 总结
v1 能跑——但它只会*说*，不会*做*。就像一个能制定作战计划、却没有军队的参谋。

### V1 的关键概念
**`history` 列表**就是对话记忆。每条用户消息和 AI 回复都被追加进去，整个列表随每次 API 调用一起发送。没有什么神奇的持久化机制——就是一个不断增长的消息数组。这也是为什么长对话会撞上 Token 限制，而且费用越来越高。

**`system` 消息**定义了 AI 的角色和行为规则。它的作用和 Claude Code 中的 [CLAUDE.md 文件](https://www.heyuan110.com/zh/posts/ai/2026-02-28-claude-code-claudemd-guide/)一样——告诉模型自己是谁、该怎么做。

## V2：流式输出——打字机效果
V1 有一个体验问题：在生成长回复时，你得盯着空白终端干等，等模型生成完毕后所有文字一股脑出现。流式输出解决了这个问题——Token 生成一个、显示一个。

### 与V1相比
改动只有一处：设置 `stream=True`，然后遍历 chunk，逐个打印 `delta.content`。

`flush=True` 参数比你想象的更重要。没有它，Python 会缓冲输出，你看到的就不是流畅的逐字符显示，而是一阵一阵的文字突然蹦出来。

## V3：Rich 富文本终端 + Markdown 渲染
终端不一定非得丑。用 `rich` 库，你能在终端里实现 Markdown 渲染、语法高亮、彩色面板和漂亮的排版。

`Rich.Live` 组件在新内容流入时持续重新渲染面板。你可以看着 Markdown 表格、代码块和格式化文本在终端里实时成型。