
import abc
from pathlib import Path

import logging
logger = logging.getLogger("aivk.core")

class LKM(abc.ABC):
    """
    Base class for all LKM models.
    loadable aivk module.
    """

    def __init__(self, name: str):
        meta_file = Path(__file__).parent / "meta.toml"

    @abc.abstractmethod
    async def onLoad(self):
        """
        Called when the LKM is loaded.
        """
        pass

    @abc.abstractmethod
    async def onUnload(self):
        """
        Called when the LKM is unloaded.
        """
        pass

    @abc.abstractmethod
    async def onInstall(self):
        """
        Called when the LKM is installed.
        """
        pass

    @abc.abstractmethod
    async def onUninstall(self):
        """
        Called when the LKM is uninstalled.
        """
        pass

    @abc.abstractmethod
    async def onUpdate(self):
        """
        Called when the LKM is updated.
        """
        pass
