# 使用显式相对导入，避免在命令行执行时的循环导入问题
from .__main__ import cli

__all__ = [
    "cli",
]