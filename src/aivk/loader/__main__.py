from importlib.metadata import EntryPoints ,entry_points
from typing import Any
from pluggy import PluginManager , HookimplMarker

from ..api import AivkFS, AivkMod
from logging import getLogger
logger = getLogger("aivk.loader")

class AivkModLoader(AivkMod):
    
    _aivk_impl = HookimplMarker("aivk")
    aivk_pm = PluginManager("aivk")
    aivk_pm.add_hookspecs(AivkMod)

    def sort(self, eps: EntryPoints) -> EntryPoints:
        """
        对模块进行排序
        """
        return eps
        
    @_aivk_impl
    async def onLoad(self, **kwargs: Any) -> None:
        """
        Aivk 模块加载器
        """

        fs: AivkFS = kwargs.get("fs", AivkFS.getFS("aivk"))

        logger.info("Aivk loader 加载成功...")
        logger.debug(f"Aivk loader fs: {fs}")
        logger.info("开始寻找模块...")
        eps: EntryPoints = entry_points(group="aivk.mods")
        logger.debug(f"找到 {len(eps)} 个模块")

        eps = self.sort(eps)
        
        

    @_aivk_impl
    async def onUnload(self, **kwargs: Any) -> None:
        """
        卸载加载器表示 加载完毕
        """
        pass

    @_aivk_impl
    async def onInit(self, **kwargs: Any) -> Any:
        """
        初始化 Aivk 模块加载器
        """
        pass

    @_aivk_impl
    async def onUninstall(self, **kwargs: Any) -> str:
        """
        卸载 Aivk 模块加载器
        """
        return "bye"

    @_aivk_impl
    async def onHealthCheck(self, **kwargs: Any) -> bool:
        """
        健康检查 Aivk 模块加载器
        """
        return True