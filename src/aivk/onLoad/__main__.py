# -*- coding: utf-8 -*-
"""加载模块的主入口"""
import asyncio
import logging
from pathlib import Path
from ..logger import setup_logging
from ..base.cli import AivkCLI
from ..__about__ import __WELCOME__, __LOGO__

setup_logging(style="panel")
logger = logging.getLogger("aivk.onLoad")


async def load(**kwargs):
    """加载AIVK模块
    
    Args:
        id: 要加载的模块ID (通过 kwargs 传入)
        path: AIVK 根目录路径 (通过 kwargs 传入), 默认为 ~/.aivk
        **kwargs: 其他加载参数

    Returns:
        None

    支持加载整个系统或指定的模块。
    """
    # F841: Remove unused variable 'aivk_root'
    # aivk_root = kwargs.get("path", Path.home() / ".aivk")
    AivkCLI._validate_id(id)
    logger.info(__WELCOME__)
    logger.info(__LOGO__)
    
    logger.info("Loading AIVK modules...")
    # 启动load模块
    load = AivkCLI.on("load", "loader")

    await load(**kwargs)


    
if __name__ == "__main__":
    asyncio.run(load(path=Path.home() / ".aivk"))