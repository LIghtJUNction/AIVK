import asyncio
from click import command
from ...api import AivkFS
from aivk.loader import AivkModLoader
from logging import getLogger
logger = getLogger("aivk.run")

@command()
def run() -> None:
    """
    启动Aivk
    """
    logger.info("初始化启动器...")
    loader = AivkModLoader()
    loader.aivk_pm.register(loader) # 自注册
    logger.debug("AivkModLoader 已注册到 AivkPM")

    async def main() -> None:
        logger.info("正在进入aivk 虚拟环境...")
        async with AivkFS.ctx() as fs:
            logger.info("Aivk 虚拟环境已进入")
            logger.info("尝试启动模块加载器...")
            logger.debug(fs.home)
            await asyncio.gather(*loader.aivk_pm.hook.onLoad(fs=fs))
        logger.info("已退出 Aivk 虚拟环境")
        await asyncio.gather(*reversed(loader.aivk_pm.hook.onUnload(fs=fs)))

    asyncio.run(main())