try:
    from aivk.core import LKM, AivkRoot
except ImportError:
    raise ImportError(" import error : aivk etc.")

# 修改相对导入为绝对导入
try:
    from core.lifecycle import Lifecycle
except ImportError:
    # 如果直接导入失败，尝试其他路径
    try:
        from loader.core.lifecycle import Lifecycle
    except ImportError:
        import sys
        import os
        # 添加当前模块路径到sys.path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(current_dir)
        from core.lifecycle import Lifecycle

import logging

logger = logging.getLogger("aivk.loader")

__version__ = "0.1.0"
__author__ = "LIghtJUNction"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025 LIghtJUNction"
__description__ = "AIVK module Loader Module"
    
__github__ = "https://github.com/LIghtJUNction/AIVK_loader"

__LOGO__ = """
Description: {__description__}
 /$$                           /$$                    
| $$                          | $$                    
| $$  /$$$$$$   /$$$$$$   /$$$$$$$  /$$$$$$   /$$$$$$ 
| $$ /$$__  $$ |____  $$ /$$__  $$ /$$__  $$ /$$__  $$
| $$| $$  \ $$  /$$$$$$$| $$  | $$| $$$$$$$$| $$  \__/
| $$| $$  | $$ /$$__  $$| $$  | $$| $$_____/| $$      
| $$|  $$$$$$/|  $$$$$$$|  $$$$$$$|  $$$$$$$| $$      
|__/ \______/  \_______/ \_______/ \_______/|__/      

Author: {__author__}
Version: {__version__}
License: {__license__}
Copyright: {__copyright__}

GitHub: {__github__}
""".format(
    __description__=__description__,
    __author__=__author__,
    __version__=__version__,
    __license__=__license__,
    __copyright__=__copyright__,
    __github__=__github__
)

class Entry(LKM):
    """
    aivk core module : loader 

    This aivk module can load any aivk module. 
    """
    @staticmethod
    async def _onLoad(aivk : AivkRoot) -> None:
        logger.info(__LOGO__)
        try:
            # 调用loader模块的onLoad方法
            await Lifecycle.onLoad(aivk)
        except Exception as e:
            logger.error(f"Error during loader module onLoad: {e}")

    @staticmethod
    async def _onUnload(aivk: AivkRoot) -> None:
        try:
            # 调用loader模块的onUnload方法
            await Lifecycle.onUnload(aivk)
        except Exception as e:
            logger.error(f"Error during loader module onUnload: {e}")

    @staticmethod
    async def _onInstall(aivk: AivkRoot) -> None:
        try:
            await Lifecycle.onInstall(aivk)
        except Exception as e:
            logger.error(f"Error during loader module onInstall: {e}")
    
    @staticmethod
    async def _onUninstall(aivk: AivkRoot) -> None:
        try:
            await Lifecycle.onUninstall(aivk)
        except Exception as e:
            logger.error(f"Error during loader module onUninstall: {e}")
    @staticmethod
    async def _onUpdate(aivk: AivkRoot) -> None:
        try:
            await Lifecycle.onUpdate(aivk)
        except Exception as e:
            logger.error(f"Error during loader module onUpdate: {e}")

