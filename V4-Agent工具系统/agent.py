"""
agent.py

MagicCode Agent

负责：

1. 接收用户输入
2. 调用大模型
3. Agentic Loop
4. Tool Calling

UI、聊天历史、公共工具均交由其它模块负责。
"""

import json

from config import client, MODEL
from tools import TOOLS, execute_tool
from history import ChatHistory
from console import UI
from utils import json_string, preview
from constants import (
    MAX_TOOL_CALL,
    ARG_PREVIEW_LENGTH,
    PREVIEW_LENGTH
)

class MagicCode:
    """
    MagicCode Agent
    """

    # 最大 Tool 调用次数
    MAX_TOOL_CALL = MAX_TOOL_CALL

    def __init__(self):
        """
        初始化 Agent
        """

        # Rich UI
        self.ui = UI()

        # 聊天历史
        self.history = ChatHistory()

    # =====================================================
    # 与 AI 对话
    # =====================================================

    def chat(self, user_input: str):
        """
        Agent 主循环
        """

        # 保存用户输入
        self.history.add_user(user_input)

        tool_count = 0

        while True:

            # 调用模型
            response = client.chat.completions.create(
                model=MODEL,
                messages=self.history.get(),
                tools=TOOLS,
            )

            message = response.choices[0].message

            # 保存 AI 回复
            self.history.add_assistant(message)

            # 输出 Markdown
            if message.content:
                self.ui.markdown(message.content)

            # 没有 Tool Calling，结束循环
            if not message.tool_calls:
                break

            # 执行 Tool Calling
            for tool_call in message.tool_calls:

                tool_count += 1

                tool_name = tool_call.function.name

                tool_args = json.loads(
                    tool_call.function.arguments
                )

                self.ui.tool_call(
                    tool_count,
                    tool_name,
                    preview(json_string(tool_args), ARG_PREVIEW_LENGTH),
                )

                # 执行工具
                result = execute_tool(
                    tool_name,
                    tool_args,
                )

                self.ui.tool_done(
                    preview(result,PREVIEW_LENGTH)
                )

                # 保存 Tool 返回结果
                self.history.add_tool(
                    tool_call.id,
                    result,
                )

            # 防止死循环
            if tool_count >= self.MAX_TOOL_CALL:

                self.ui.error(
                    f"Tool 调用次数超过 {self.MAX_TOOL_CALL} 次，停止执行。"
                )

                break

    # =====================================================
    # 启动程序
    # =====================================================

    def run(self):
        """
        启动终端
        """

        self.ui.banner(MODEL)

        while True:

            try:

                user_input = self.ui.input()

                cmd = user_input.strip().lower()

                # 空输入
                if not cmd:
                    continue

                # 退出
                if cmd in ("exit", "quit"):

                    self.ui.info("再见！")

                    break

                # 清空聊天记录
                if cmd == "clear":

                    self.history.reset()

                    self.ui.info("聊天历史已清空。")

                    continue

                # 开始聊天
                self.chat(user_input)

                self.ui.println()

            except KeyboardInterrupt:

                self.ui.info("再见！")

                break