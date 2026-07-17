"""
history.py

聊天记录管理
"""

from prompt import SYSTEM_PROMPT


class ChatHistory:
    """
    管理聊天历史
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """
        重置聊天历史
        """

        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

    def add_user(self, text: str):
        """
        添加用户消息
        """

        self.messages.append(
            {
                "role": "user",
                "content": text
            }
        )

    def add_assistant(self, message):
        """
        添加 AI 回复
        """

        self.messages.append(message)

    def add_tool(self, tool_call_id, result):
        """
        添加 Tool 返回结果
        """

        self.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": result,
            }
        )

    def get(self):
        """
        获取全部历史
        """

        return self.messages