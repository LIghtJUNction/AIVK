# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict, NoReturn, Optional
from pathlib import Path
from ..logger import setup_logging

setup_logging(style="panel")  # 使用面板样式
logger = logging.getLogger("aivk.onList")

async def list(
    aivk_root: Optional[str | Path] = None,
    **kwargs: Dict[str, Any]
) -> NoReturn:
    """列出模块
    ...

    """
    pass
    
    # 调用加载函数
   


if __name__ == "__main__":
    # 直接运行时，执行加载
    import asyncio
    asyncio.run(list())