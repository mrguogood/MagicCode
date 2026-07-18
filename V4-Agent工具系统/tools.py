"""
tools.py

定义 AI 可以使用的工具，并负责真正执行工具。

本文件包含两部分内容：

1. TOOLS
   告诉 AI 有哪些工具可以调用

   Function Calling 要求工具定义遵循特定的 JSON Schema 格式。每个工具需要名称、描述和参数 Schema

   工具定义的重要性超出你的预期。模型通过阅读这些描述来决定何时、如何使用每个工具。好的工具定义有三个原则：
       - 直觉化命名：`read_file` 一目了然，`rf` 则不然
       - 具体的描述：模型靠描述来判断何时该用某个工具
       - 精确的参数 Schema：必填 vs 可选、类型和默认值都会影响模型的行为


2. execute_tool()
   AI 负责决定调用什么，你的代码负责真正干活。 这种分离是整个架构的安全基石：

   当 AI 调用工具后，由 Python 真正执行

   注意点：
    1. `read_file` 返回带行号的内容——方便 AI 后续编辑时精确定位
    2. `write_file` 自动创建目录——`os.makedirs(exist_ok=True)` 消除了目录不存在的错误
    3. `run_command` 有安全黑名单——简单但有效的危险操作防护
    4. 所有工具返回字符串——这是 API 的要求，工具结果必须是可序列化的文本
"""

import glob
import os
import subprocess

from constants import (
    COMMAND_TIMEOUT,
    MAX_DIRECTORY_DEPTH,
    MAX_FILE_COUNT,
    MAX_SEARCH_RESULT,
    DANGEROUS_COMMANDS,
    IGNORED_DIRS,
    DEFAULT_ENCODING,
)

# ======================================================
# 定义工具
# ======================================================

def build_tool(name, description, properties, required):
    """
    构造一个 Tool。

    参数说明：

    name
        工具名称

    description
        工具说明

    properties
        参数定义

    required
        必填参数
    """

    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


TOOLS = [

    # --------------------------------------------------
    # 读取文件
    # --------------------------------------------------

    build_tool(
        name="read_file",
        description="读取文件内容，并返回带行号的文本。",
        properties={
            "path": {
                "type": "string",
                "description": "文件路径"
            }
        },
        required=["path"],
    ),

    # --------------------------------------------------
    # 写文件
    # --------------------------------------------------

    build_tool(
        name="write_file",
        description="写入整个文件，如果目录不存在自动创建。",
        properties={
            "path": {
                "type": "string",
                "description": "文件路径"
            },
            "content": {
                "type": "string",
                "description": "文件内容"
            }
        },
        required=["path", "content"],
    ),

    # --------------------------------------------------
    # 编辑文件
    # --------------------------------------------------

    build_tool(
        name="edit_file",
        description="替换文件中的指定内容。",
        properties={
            "path": {
                "type": "string"
            },
            "old_text": {
                "type": "string"
            },
            "new_text": {
                "type": "string"
            }
        },
        required=["path", "old_text", "new_text"],
    ),

    # --------------------------------------------------
    # 执行命令
    # --------------------------------------------------

    build_tool(
        name="run_command",
        description="执行 Shell 命令。",
        properties={
            "command": {
                "type": "string"
            }
        },
        required=["command"],
    ),

    # --------------------------------------------------
    # 查看目录
    # --------------------------------------------------

    build_tool(
        name="list_files",
        description="查看目录结构。",
        properties={
            "path": {
                "type": "string"
            }
        },
        required=[],
    ),

    # --------------------------------------------------
    # 搜索代码
    # --------------------------------------------------

    build_tool(
        name="search_code",
        description="搜索指定字符串。",
        properties={
            "pattern": {
                "type": "string"
            },
            "path": {
                "type": "string"
            }
        },
        required=["pattern"],
    ),

]

# ======================================================
# 工具执行
# ======================================================

def execute_tool(name: str, params: dict) -> str:
    """
    执行 AI 调用的工具。

    参数：

    name
        工具名称

    params
        AI 传递的参数

    返回：

    字符串
    """

    try:

        # ==================================================
        # 读取文件
        # ==================================================

        if name == "read_file":

            with open(
                params["path"],
                "r",
                encoding=DEFAULT_ENCODING,
                errors="replace"
            ) as f:

                content = f.read()

            lines = content.split("\n")

            result = []

            for index, line in enumerate(lines):

                result.append(
                    f"{index + 1:4d} | {line}"
                )

            return "\n".join(result)

        # ==================================================
        # 写文件
        # ==================================================

        elif name == "write_file":

            path = params["path"]

            os.makedirs(
                os.path.dirname(path) or ".",
                exist_ok=True
            )

            with open(
                path,
                "w",
                encoding=DEFAULT_ENCODING
            ) as f:

                f.write(params["content"])

            return f"成功写入文件：{path}"

        # ==================================================
        # 编辑文件
        # ==================================================

        elif name == "edit_file":

            path = params["path"]

            with open(path, "r", encoding=DEFAULT_ENCODING) as f:

                content = f.read()

            if params["old_text"] not in content:

                return "没有找到需要替换的内容。"

            content = content.replace(
                params["old_text"],
                params["new_text"],
                1
            )

            with open(path, "w", encoding=DEFAULT_ENCODING) as f:

                f.write(content)

            return "文件修改成功。"

        # ==================================================
        # 执行命令
        # ==================================================

        elif name == "run_command":

            cmd = params["command"]

            if any(cmd.startswith(item) for item in DANGEROUS_COMMANDS):
                return "危险命令，拒绝执行。"

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=COMMAND_TIMEOUT,
            )

            output = result.stdout

            if result.stderr:
                output += "\n" + result.stderr

            return output or "命令执行完成。"

        # ==================================================
        # 查看目录
        # ==================================================

        elif name == "list_files":

            path = params.get("path", ".")

            result = []

            base_depth = path.rstrip(os.sep).count(os.sep)

            for root, dirs, files in os.walk(path):

                current_depth = root.count(os.sep) - base_depth
                # 限制最大遍历层数
                if current_depth >= MAX_DIRECTORY_DEPTH:
                    dirs.clear()

                dirs[:] = [
                    d
                    for d in dirs
                    if d not in IGNORED_DIRS
                ]

                for file in files:

                    result.append(
                        os.path.join(root, file)
                    )

            return "\n".join(
                result[:MAX_FILE_COUNT]
            )

        # ==================================================
        # 搜索代码
        # ==================================================

        elif name == "search_code":

            pattern = params["pattern"]

            path = params.get("path", ".")

            result = []

            for file in glob.glob(
                os.path.join(path, "**", "*"),
                recursive=True
            ):

                if not os.path.isfile(file):
                    continue

                try:

                    with open(
                        file,
                        "r",
                        encoding=DEFAULT_ENCODING,
                        errors="replace"
                    ) as f:

                        for line_number, line in enumerate(f, start=1):

                            if pattern.lower() in line.lower():

                                result.append(
                                    f"{file}:{line_number}: {line.strip()}"
                                )

                                if len(result) >= MAX_SEARCH_RESULT:
                                    return "\n".join(result)

                except Exception:
                    continue

            if result:
                return "\n".join(result)

            return "没有找到匹配内容。"

        # ==================================================

        return f"未知工具：{name}"

    except Exception as e:

        return f"执行失败：{e}"