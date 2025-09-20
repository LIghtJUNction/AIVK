from logging import getLogger
from typing import Any

from aivk.api import AivkMod
from aivk.base.config import AivkConfig
from aivk.base.fs import AivkFS
from ..__about__ import __BYE__, __LOGO__, __WELCOME__, __O_o__

logger = getLogger("aivk.aivkd")

class AivkDaemonConfig(AivkConfig):
    """AivkDaemon 配置类"""
    id: str = "aivkd"
    level: int = 0
    k: int = 1
    # 可以添加更多daemon特定的配置字段

class AivkDaemon(AivkMod):
    """AivkDaemon"""
    def __init__(self):
        super().__init__()
        # 获取文件系统实例
        self.fs = AivkFS.getFS("aivkd")
        # 加载配置
        self.config = AivkDaemonConfig.load(self.fs, "aivkd_load_config")

    async def onLoad(self, **kwargs: dict[str, Any]) -> None:
        """模块加载时调用"""
        logger.info(f"{__LOGO__}")

    async def onUnload(self, **kwargs: dict[str, Any]) -> None:
        """模块卸载时调用"""
        logger.info(f"{__BYE__}")

    async def onInit(self, **kwargs: dict[str, Any]) -> AivkDaemonConfig:
        """模块首次被安装时调用"""
        logger.info(__WELCOME__)
        # 保存初始配置
        self.config.save()
        return self.config

    async def onUninstall(self, **kwargs: dict[str, Any]) -> str:
        """模块被卸载时调用"""
        logger.info(f"{__O_o__}")
        return "bye"

    async def onHealthCheck(self, **kwargs: dict[str, Any]) -> bool:
        """模块健康检查"""
        return True
