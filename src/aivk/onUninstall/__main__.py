# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict, NoReturn

from aivk.base.exceptions import AivkModuleError
from ..logger import setup_logging
from ..base.utils import AivkExecuter
from ..base.cli import AivkCLI
setup_logging(style="panel")  # 使用面板样式
logger = logging.getLogger("aivk.onUninstall")

async def uninstall(
    **kwargs: Dict[str, Any]
) -> NoReturn:
    """卸载模块入口点
    
    Args:
        id: 要卸载的模块ID
        **kwargs: 其他卸载参数
        
    Returns:
        NoReturn: 卸载是否成功
    """
    logger.info("Uninstalling ...")
    
    id = kwargs.get("id", "fs")

    AivkCLI._validate_id(id)

    if id.startswith("aivk-"):
        logger.error("模块 ID 不应包含 'aivk-' 前缀, 示例：aivk-fs 模块id 应为 fs ， aivk-fs 为pypi包名")
        raise AivkModuleError(id=id, operation="uninstall", message="模块 ID 不应包含 'aivk-' 前缀")
    
    await AivkExecuter.aexec(command=f"uv pip uninstall aivk-{id}")
    
    logger.info(f"Successfully uninstalled module: {id}")
    
if __name__ == "__main__":
    # 直接运行时，执行卸载
    import asyncio
    asyncio.run(uninstall())