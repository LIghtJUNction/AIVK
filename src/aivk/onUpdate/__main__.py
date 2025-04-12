# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict

from ..logger import setup_logging
from ..base.utils import AivkExecuter

setup_logging(style="panel")  # 使用面板样式
logger = logging.getLogger("aivk.onUpdate")

async def update(
    **kwargs: Dict[str, Any]
) -> None:
    """更新模块入口点

    Args:
        id: 要更新的模块ID (通过 kwargs 传入)
        **kwargs: 其他更新参数

    Returns:
        None
    """
    id = kwargs.get("id")
    if not id:
        logger.error("Module ID ('id') is required for update.")
        return

    logger.info(f"Updating aivk-{id}...")

    try:
        result = await AivkExecuter.aexec(command=f"uv pip install --upgrade aivk-{id}")
        if result.success:
             logger.info(f"Successfully updated module: aivk-{id}")
        else:
            logger.error(f"Update of aivk-{id} failed.")
            logger.error(f"Stderr:\n{result.stderr}")
    except Exception as e:
        logger.error(f"An error occurred during update of aivk-{id}: {e}", exc_info=True)


if __name__ == "__main__":
    # 直接运行时，执行更新
    logger.warning("Running update directly requires specifying an 'id', e.g., asyncio.run(update(id='fs'))")
