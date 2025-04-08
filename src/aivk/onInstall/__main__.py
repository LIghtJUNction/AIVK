# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict, NoReturn
from ..logger import setup_logging
from ..base.utils import AivkExecuter
setup_logging(style="panel")  # 使用面板样式
logger = logging.getLogger("aivk.onInstall")

async def install(
    **kwargs: Dict[str, Any]
) -> NoReturn:
    """安装模块入口点
    
    Args:
        **kwargs: id
        
    Returns:
        NoReturn
    """
    id = kwargs.get("id", "fs")
    if id.startswith("aivk-"):
        logger.error("模块 ID 不应包含 'aivk-' 前缀, 示例：aivk-fs 模块id 应为 fs ， aivk-fs 为pypi包名")

    logger.info("Installing ...")

    await AivkExecuter.aexec(command=f"uv pip install aivk-{id}")

    logger.info(f"Installation of aivk-{id} completed.")

if __name__ == "__main__":
    # 直接运行时，执行安装
    import asyncio
    asyncio.run(install())