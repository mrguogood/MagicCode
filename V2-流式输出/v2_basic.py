#!/usr/bin/env python3
"""MagicCode v2 — 带流式输出"""
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

print("MagicCode v2（流式输出）— 输入 'exit' 退出")
while True:
    user_input = input("\nYou > ")
    if user_input.strip().lower() in ("exit", "quit"):
        break

    history.append({"role": "user", "content": user_input})

    print("\nAI: ", end="", flush=True)
    full_reply = ""

    stream = client.chat.completions.create(
        model="qwen3-vl-235b-a22b-thinking",
        messages=history,
        stream=True,  # 关键改动
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
            full_reply += delta

    print()  # 回复结束后换行
    history.append({"role": "assistant", "content": full_reply})