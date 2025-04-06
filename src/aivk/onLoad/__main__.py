import asyncio
import logging
from typing import Any, Dict
from aivk.logger import setup_logging

setup_logging(style="panel")  # 使用面板样式
logger = logging.getLogger("aivk.onLoad")

async def load(**kwargs) -> bool:
    """
    入口点一：aivk load
    """
    logger.info("Loading ...")
    # 加载核心模块...
    # 根据配置来加载核心组件

    return True

def main() -> None:
    """终端：aivk-load
    入口点二
    """
    # TODO: 通过命令行参数获取并传递参数
    kwargs = {}
    
    asyncio.run(load(**kwargs))


if __name__ == "__main__":
    """python -m aivk.onLoad
    入口点三
    """
    main()

