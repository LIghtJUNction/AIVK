# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict, NoReturn, Optional
from pathlib import Path
import os
from ..logger import setup_logging
from ..base.utils import aivk_on

setup_logging(style="panel")  # 使用面板样式
logger = logging.getLogger("aivk.onUnload")

async def unload(
    aivk_root: Optional[str] = None,
    **kwargs: Dict[str, Any]
) -> NoReturn:
    """卸载模块入口点
    
    Args:
        aivk_root: AIVK 根目录路径，如果未指定则按以下顺序查找：
                  1. 环境变量 AIVK_ROOT
                  2. 默认路径 ~/.aivk
        **kwargs: 其他卸载参数
        
    Returns:
        NoReturn
    """
    logger.info("Unloading ...")
    
    # 处理路径优先级
    root_path = None
    if aivk_root:
        # 1. 使用传入的路径
        root_path = Path(aivk_root)
        logger.info(f"Using specified path: {root_path}")
    elif os.environ.get("AIVK_ROOT"):
        # 2. 使用环境变量
        root_path = Path(os.environ["AIVK_ROOT"])
        logger.info(f"Using AIVK_ROOT environment variable: {root_path}")
    else:
        # 3. 使用默认路径
        root_path = Path.home() / ".aivk"
        logger.info(f"Using default path: {root_path}")
    
    # 检查目录是否存在
    if not root_path.exists():
        logger.warning(f"AIVK root directory does not exist: {root_path}")
        return False
    
    id = kwargs.get("id", "loader")
    
    await aivk_on("unload", "loader" , aivk_root=str(root_path), **kwargs)


if __name__ == "__main__":
    # 直接运行时，执行卸载
    import asyncio
    asyncio.run(unload())