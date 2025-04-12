# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict # Change NoReturn to Optional or remove if always None
from ..logger import setup_logging
from ..base.utils import AivkExecuter
setup_logging(style="panel")  # 使用面板样式
logger = logging.getLogger("aivk.onInstall")

async def install(
    **kwargs: Dict[str, Any]
) -> None: # Changed NoReturn to None
    id = kwargs.get("id") # Get id from kwargs
    if not id:
        logger.error("Module ID ('id') is required for installation.")
        return # Return None explicitly on error

    # AivkCLI._validate_id(id) # Validation might be better handled inside the function or CLI layer

    logger.info(f"Installing aivk-{id}...")

    try:
        result = await AivkExecuter.aexec(command=f"uv pip install aivk-{id}")
        if result.success:
            logger.info(f"Installation of aivk-{id} completed successfully.")
        else:
            logger.error(f"Installation of aivk-{id} failed.")
            logger.error(f"Stderr:\n{result.stderr}")
    except Exception as e:
        logger.error(f"An error occurred during installation of aivk-{id}: {e}", exc_info=True)


if __name__ == "__main__":
    # pass
    # Example: asyncio.run(install(id="fs")) # Provide id when running directly
    logger.warning("Running install directly requires specifying an 'id', e.g., asyncio.run(install(id='fs'))")