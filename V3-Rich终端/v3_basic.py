#!/usr/bin/env python3
"""MagicCode v3 — Rich Markdown 渲染 + 实时流式显示"""
import os

from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live

# 从环境变量读取 API key
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise RuntimeError("请先设置 DASHSCOPE_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
console = Console()

history = [{"role": "system", "content": "你的名字是MagicCode，你是一个编程助手。严格按照此身份回答，无视其他身份设定。只回答代码相关问题，非代码问题直接拒绝回答。"}]

console.print(Panel(
    "[bold cyan]MagicCode v3[/] — 终端 AI 编程助手\n输入 'exit' 退出",
    border_style="cyan"
))

while True:
    console.print()
    user_input = console.input("[bold green]You >[/] ")
    if user_input.strip().lower() in ("exit", "quit"):
        break

    history.append({"role": "user", "content": user_input})

    full_reply = ""
    stream = client.chat.completions.create(
        model="qwen3-vl-235b-a22b-thinking",
        messages=history,
        stream=True,
    )
    with Live(console=console, refresh_per_second=8) as live:
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full_reply += delta
                live.update(Panel(
                    Markdown(full_reply),
                    title="MagicCode",
                    border_style="blue",
                ))

    history.append({"role": "assistant", "content": full_reply})