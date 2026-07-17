"""
utils.py

公共工具
"""

import json


def json_string(data):

    """
    转成 JSON 字符串
    """

    return json.dumps(
        data,
        ensure_ascii=False
    )


def preview(text, length=100):

    """
    截断字符串
    """

    if text is None:

        return ""

    text = text.replace("\n", " ")

    if len(text) <= length:

        return text

    return text[:length] + "..."