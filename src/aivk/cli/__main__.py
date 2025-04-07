import asyncio
import logging

from aivk.base.cli import BaseCLI
from aivk.logger import setup_logging

setup_logging(style="error", theme="colorful", icons="blocks", level=logging.DEBUG)
logger = logging.getLogger("aivk.cli")

async def cli() -> None:
    """AIVK CLI 异步入口点
    具体实现
    """
    logger.info("AIVK CLI is running...")
    

def main() -> None:
    """AIVK CLI 同步入口点
    供pyproject打包使用
    """
    asyncio.run(cli())

if __name__ == "__main__":
    main()