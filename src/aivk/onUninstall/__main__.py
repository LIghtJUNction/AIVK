import asyncio
import logging
from typing import Any, Dict
from aivk.logger import setup_logging

setup_logging(style="panel")  # 使用面板样式
logger = logging.getLogger("aivk.onUninstall")

async def uninstall(**kwargs) -> bool:
    """
    入口点一：aivk uninstall
    """
    logger.info("Uninstalling ...")
    # 卸载核心模块...
    # 根据配置来卸载核心组件

    return True

def cli() -> None:
    """终端：aivk-uninstall
    入口点二
    """
    # TODO: 通过命令行参数获取并传递参数
    kwargs = {}
    
    asyncio.run(uninstall(**kwargs))


if __name__ == "__main__":
    """python -m aivk.onUninstall
    入口点三
    """
    cli()

