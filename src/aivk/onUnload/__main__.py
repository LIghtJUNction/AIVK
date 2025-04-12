# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict, Optional # Change NoReturn to Optional or remove if always None
from pathlib import Path
import os
from ..logger import setup_logging

setup_logging(style="panel")  # 使用面板样式
logger = logging.getLogger("aivk.onUnload")

async def unload(
    **kwargs: Dict[str, Any]
) -> None: # Changed NoReturn to None
    """卸载模块入口点

    Args:
        path: AIVK 根目录路径 (通过 kwargs 传入), 如果未指定则按以下顺序查找：
                  1. 环境变量 AIVK_ROOT
                  2. 默认路径 ~/.aivk
        **kwargs: 其他卸载参数

    Returns:
        None
    """
    logger.info("Unloading ...")

    aivk_path_str: Optional[str] = kwargs.get("path") # Use 'path' consistent with CLI
    aivk_path: Optional[Path] = None # Initialize aivk_path

    # 处理路径优先级
    if aivk_path_str:
        # 1. 使用传入的路径
        aivk_path = Path(aivk_path_str).expanduser()
        logger.info(f"Using specified path: {aivk_path}")
    elif os.environ.get("AIVK_ROOT"):
        # 2. 使用环境变量
        aivk_path = Path(os.environ["AIVK_ROOT"]).expanduser()
        logger.info(f"Using AIVK_ROOT environment variable: {aivk_path}")
    else:
        # 3. 使用默认路径
        aivk_path = Path.home() / ".aivk"
        logger.info(f"Using default path: {aivk_path}")

    # 可以在这里使用 aivk_path 进行后续操作
    logger.info(f"Unloading with path context: {aivk_path}")
    # 实际的卸载逻辑...
    logger.info("Unload process completed.")


if __name__ == "__main__":
    # pass
    import asyncio
    asyncio.run(unload()) # Runs with default path logic