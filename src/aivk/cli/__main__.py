import asyncio
import logging

from aivk.base.cli import BaseCLI
from aivk.logger import setup_logging

setup_logging(style="card", level=logging.DEBUG)
logger = logging.getLogger("aivk.cli")

class AIVKCLI(BaseCLI):
    pass

async def _main() -> None:
    """AIVK CLI 异步入口点
    具体实现
    """
    pass

def main() -> None:
    """AIVK CLI 同步入口点
    供pyproject打包使用
    """
    asyncio.run(_main())

if __name__ == "__main__":
    asyncio.run(_main())