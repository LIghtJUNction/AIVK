from logging import getLogger

from aivk.api import AivkMod , AivkConfig
from ..__about__ import __BYE__, __LOGO__, __WELCOME__, __O_o__

logger = getLogger("aivk.aivkd")

class AivkDaemon(AivkMod):
    """AivkDaemon"""
    config = AivkConfig(
        fs=None,
        file_name: str | None =None,
        meta=dict(
            id="aivkd",
            loadconf=dict(
                level=0,
                k=1
            )
        )
    )

    async def onLoad(self, **kwargs) -> None:
        """模块加载时调用"""
        logger.info(f"{__LOGO__}")

    async def onUnload(self, **kwargs) -> None:
        """模块卸载时调用"""
        logger.info(f"{__BYE__}")

    async def onInit(self, **kwargs) -> AivkConfig:
        """模块首次被安装时调用"""
        logger.info(__WELCOME__)
        return self.config

    async def onUninstall(self, **kwargs) -> str:
        """模块被卸载时调用"""
        logger.info(f"{__O_o__}")
        return "bye"

    async def onHealthCheck(self, **kwargs) -> bool:
        """模块健康检查"""
        return True
