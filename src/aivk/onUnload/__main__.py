import asyncio
import logging
from typing import Any, Dict
from aivk.logger import setup_logging

setup_logging(style="panel")  # 使用面板样式
logger = logging.getLogger("aivk.onUnload")

async def unload(**kwargs) -> bool:
    """
    入口点一：aivk unload
    """
    logger.info("Unloading ...")
    # 卸载核心模块...
    # 根据配置来卸载核心组件

    return True

def cli() -> None:
    """终端：aivk-unload
    入口点二
    """
    # TODO: 通过命令行参数获取并传递参数
    kwargs = {}
    logger.info(f"kwargs: {kwargs}")
    asyncio.run(unload(**kwargs))


if __name__ == "__main__":
    """python -m aivk.onUnload
    入口点三
    """
    cli()


