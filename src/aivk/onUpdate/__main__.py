# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict, NoReturn

from ..logger import setup_logging
from ..base.utils import AivkExecuter

setup_logging(style="panel")  # 使用面板样式
logger = logging.getLogger("aivk.onUpdate")

async def update(
    id: str = "fs",
    **kwargs: Dict[str, Any]
) -> NoReturn:
    """更新模块入口点
    
    Args:
        id: 要更新的模块ID
        **kwargs: 其他更新参数
        
    Returns:
        NoReturn
    """

    logger.info("Updating ...")

    await AivkExecuter.aexec(command=f"uv pip install --upgrade aivk-{id}")

    logger.info(f"Successfully updated module: {id}")

if __name__ == "__main__":
    # 直接运行时，执行更新
    import asyncio
    asyncio.run(update())
