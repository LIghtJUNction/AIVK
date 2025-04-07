from abc import ABC, abstractmethod
import asyncio
import click
import logging

logger = logging.getLogger(__name__)

class BaseCLI(ABC):
    """AIVK CLI 基类
    
    所有模块都应继承此类以获得标准的命令行结构。
    支持两种等效的调用方式:
    1. aivk-<module_id> xxx
    2. aivk <module_id> xxx
    """
    
    @abstractmethod
    def __init__(self):
        """初始化模块，子类必须指定 module_id"""
        self.module_id = None
        
    @abstractmethod
    async def on_load(self, **kwargs):
        """加载模块时的钩子"""
        pass
        
    @abstractmethod
    async def on_unload(self, **kwargs):
        """卸载模块时的钩子"""
        pass
    
    @abstractmethod
    async def on_install(self, **kwargs):
        """安装模块时的钩子"""
        pass
        
    @abstractmethod
    async def on_uninstall(self, **kwargs):
        """卸载模块时的钩子"""
        pass
        
    @abstractmethod
    async def on_update(self, **kwargs):
        """更新模块时的钩子"""
        pass