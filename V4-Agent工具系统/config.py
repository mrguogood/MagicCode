"""
config.py

项目配置文件

负责：
1. 读取 API Key
2. 创建客户端
3. 配置模型名称
"""

import os
from openai import OpenAI
from constants import (
    DEFAULT_MODEL,
    API_KEY,
    BASE_URL
)

# ============================
# API Key
# ============================

API_KEY = os.getenv(API_KEY)

if not API_KEY:
    raise ValueError(
        "请先设置 API_KEY。"
    )

# ============================
# 模型名称
# ============================

MODEL = DEFAULT_MODEL

# ============================
# 创建客户端
# ============================

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)