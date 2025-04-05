from pydantic import BaseModel
import logging
import sys
import os

from aivk.core import AivkRoot
from aivk.core import AivkModuleLoadError

# 添加当前模块路径到sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 使用绝对导入
try:
    from manager import AivkModuleManager
except ImportError:
    # 尝试通过完整路径导入
    sys.path.append(os.path.dirname(current_dir))
    from core.manager import AivkModuleManager

logger = logging.getLogger("aivk.loader.lifecycle")

class Lifecycle(BaseModel):
    """Lifecycle class
    """
    @staticmethod
    async def onLoad(aivk : AivkRoot) -> None:
        """onLoad method
        """
        # 检测模块目录其他模块
        # aivk实例方便获取各个路径

        if not aivk.check_module_status("loader"):
            # loader模块不存在或被禁用，退出循环 建议都这样写
            logger.info("Loader module disabled, exiting loop.")
            raise AivkModuleLoadError("loader", "Loader module disabled")

        loader = AivkModuleManager(aivk=aivk)

        loader.aivk.update_all_meta  # 作为属性访问，而不是方法调用


    @staticmethod
    async def onUnload(aivk: AivkRoot) -> None:
        """onUnload method
        """
        logger.info("aivk module loader unloaded!")
    @staticmethod
    async def onInstall(aivk: AivkRoot) -> None:
        """onInstall method
        """
        logger.info("aivk module installed!")
    @staticmethod
    async def onUninstall(aivk: AivkRoot) -> None:
        """onUninstall method
        """
        logger.info("aivk module loader unloaded!")
    @staticmethod
    async def onUpdate(aivk: AivkRoot) -> None:
        """onUpdate method
        """
        logger.info("loader updating ... ")
