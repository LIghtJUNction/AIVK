# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict, NoReturn, Optional
from pathlib import Path
import os
from ..logger import setup_logging
from ..__about__ import __WELCOME__, __LOGO__
from ..base.utils import  aivk_on

setup_logging(style="panel")  # 使用面板样式
logger = logging.getLogger("aivk.onLoad")

async def load(
    **kwargs: Dict[str, Any]
) -> NoReturn:
    """加载模块入口点
    
    Args:
        aivk_root: AIVK 根目录路径，如果未指定则按以下顺序查找：
                  1. 环境变量 AIVK_ROOT
                  2. 默认路径 ~/.aivk
        **kwargs: 其他加载参数
        
    Returns:
        bool: 加载是否成功
    """
    logger.info("Loading ...")
    # 处理路径优先级
    aivk_root = kwargs.get("aivk_root" , os.getenv("AIVK_ROOT"))

    if isinstance(aivk_root, str):
        aivk_root = Path(aivk_root)

    if aivk_root.exists():
        logger.info(f"AIVK_ROOT: {aivk_root}")
    else:
        try:
            aivk_root.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建 AIVK_ROOT: {aivk_root}")
            logger.info("=" * 20)
            logger.info(__WELCOME__)
        except Exception as e:
            logger.error(f"创建 AIVK_ROOT 失败: {e}")

        logger.info(__LOGO__)

    await aivk_on("load", "loader", **kwargs)
    
    # 调用加载函数
   


if __name__ == "__main__":
    # 直接运行时，执行加载
    import asyncio
    asyncio.run(load())