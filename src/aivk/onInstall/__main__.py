import asyncio
import logging
from typing import Any, Dict
from aivk.logger import setup_logging

setup_logging(style="panel")  # 使用面板样式
logger = logging.getLogger("aivk.onInstall")

async def install(**kwargs) -> bool:
    """
    入口点一：aivk install
    """
    logger.info("Installing ...")
    # 安装核心模块...
    # 根据配置来安装核心组件

    return True

def cli() -> None:
    """终端：aivk-install
    入口点二
    """
    # TODO: 通过命令行参数获取并传递参数
    kwargs = {}
    
    asyncio.run(install(**kwargs))


if __name__ == "__main__":
    """python -m aivk.onInstall
    入口点三
    """
    cli()
    