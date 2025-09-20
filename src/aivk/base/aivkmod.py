from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING
from pluggy import HookspecMarker

if TYPE_CHECKING:
    from ..config.models import AivkConfig

class AivkMod(ABC):
    config: "AivkConfig"
    _aivk_spec = HookspecMarker("aivk")

    @property
    def priority(self) -> int:
        """
        获取模块的优先级
        """
        return self.config.meta.loadconf.level * self.config.meta.loadconf.k

    def enable(self):
        """
        确保模块启用
        """
        self.config.meta.loadconf.k = 1

    def disable(self):
        """
        确保模块禁用
        """
        self.config.meta.loadconf.k = 0

    @property
    def status(self) -> str:
        """
        获取模块的状态
        """
        return "enabled" if self.priority != 0 else "disabled"

    @abstractmethod
    @_aivk_spec
    async def onLoad(self, **kwargs: Any) -> None:
        """
        模块加载时调用
        """
        pass

    @abstractmethod
    @_aivk_spec
    async def onUnload(self, **kwargs: Any) -> None:
        """
        模块卸载时调用
        """
        pass

    @abstractmethod
    @_aivk_spec
    async def onInit(self, **kwargs: Any) -> AivkConfig:
        """
        模块首次被安装时调用
        """
        pass

    @abstractmethod
    @_aivk_spec
    async def onUninstall(self, **kwargs: Any) -> str:
        """
        模块被卸载时调用
        比如清理缓存文件
        返回一句遗言
        """
        pass

    @abstractmethod
    @_aivk_spec
    async def onHealthCheck(self, **kwargs: Any) -> bool:
        """
        模块健康检查
        """
        pass