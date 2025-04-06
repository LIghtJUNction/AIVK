import argparse
import asyncio
from enum import Enum
import logging
from pathlib import Path
from typing import Optional, Any, Type, Literal
from pydantic import BaseModel, Field

class CommandType(str, Enum):
    """基础命令类型枚举"""
    LOAD = "Load"
    UNLOAD = "Unload"
    INSTALL = "Install"
    UNINSTALL = "Uninstall"


class BaseCLI(BaseModel):
    """基础命令行接口类
    /cli/__main__.py 主cli继承该类
    
    """
    pass

class LoadCLI(BaseCLI):
    """加载命令行接口
    /onLoad/__main__.py 附cli程序 继承该类 作用：python -m aivk.onLoad --anything 传递参数调用时使用该cli

    """
    pass

class UnloadCLI(BaseCLI):
    """卸载命令行接口
    /onUnload/__main__.py 附cli程序 继承该类 作用：python -m aivk.onUnload --anything 传递参数调用时使用该cli

    """
    pass    

class InstallCLI(BaseCLI):
    """安装命令行接口
    /onInstall/__main__.py 附cli程序 继承该类 作用：python -m aivk.onInstall --anything 传递参数调用时使用该cli

    """
    pass

class UninstallCLI(BaseCLI):
    """卸载命令行接口
    /onUninstall/__main__.py 附cli程序 继承该类 作用：python -m aivk.onUninstall --anything 传递参数调用时使用该cli

    """
    pass



