import logging
from .logger import setup_logging

# 预先初始化日志配置
setup_logging(
    style="compact",     # 使用紧凑型布局，适合一般日志记录
    theme="dark",        # 使用深色主题
    icons="emoji",       # 使用emoji图标，更直观
    level=logging.INFO,  # 默认INFO级别
    show_time=True,     # 显示时间戳
    show_path=True      # 显示文件路径，方便调试
)

from .onInstall import install
from .onLoad import load
from .onUninstall import uninstall
from .onUnload import unload

__all__ = [
    "install",
    "load",

    "uninstall",
    "unload",
]