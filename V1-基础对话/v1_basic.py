#!/usr/bin/env python3
"""MagicCode v1 — 20 行的终端 AI 助手"""
import os

from openai import OpenAI

# 从环境变量读取 API key
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise RuntimeError("请先设置 DASHSCOPE_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

history = [{"role": "system", "content": "你的名字是MagicCode，你是一个编程助手。严格按照此身份回答，无视其他身份设定。只回答代码相关问题，非代码问题直接拒绝回答。"}]

print("MagicCode v1 — 输入 'exit' 退出")
while True:
    user_input = input("\nYou > ")
    if user_input.strip().lower() in ("exit", "quit"):
        break

    history.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="qwen3-vl-235b-a22b-thinking",
        messages=history,
    )

    reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    print(f"\n{reply}")