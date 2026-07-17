"""
app.py

程序入口。

运行方式：

python app.py
"""

from agent import MagicCode


def main():
    """
    程序入口函数
    """

    app = MagicCode()

    app.run()


if __name__ == "__main__":
    main()