"""
console.py

统一管理 Rich 输出
"""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from constants import APP_TITLE

class UI:

    def __init__(self):

        self.console = Console()

    def banner(self, model):

        self.console.print(
            Panel(
                "[bold cyan]MagicCode[/]\n\n"
                "终端 AI 编程助手\n\n"
                "exit 退出\n"
                "clear 清空历史",
                border_style="cyan",
                padding=(1, 2),
            )
        )

        self.console.print(
            f"[dim]模型：{model}[/]"
        )

    def markdown(self, text):

        self.console.print(
            Panel(
                Markdown(text),
                title=APP_TITLE,
                border_style="blue",
                padding=(1, 2),
            )
        )

    def tool_call(self, index, name, args):

        self.console.print(
            f"[yellow][{index}] {name}[/]"
            f" [dim]{args}[/]"
        )

    def tool_done(self, text):

        self.console.print(
            f"[green]Done[/] [dim]{text}[/]"
        )

    def input(self):

        return self.console.input(
            "[bold green]You > [/]"
        )

    def println(self):

        self.console.print()

    def info(self, text):

        self.console.print(
            f"[cyan]{text}[/]"
        )

    def error(self, text):

        self.console.print(
            f"[red]{text}[/]"
        )