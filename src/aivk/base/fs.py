"""
文件系统操作模块，包含 AIVK 文件系统初始化、挂载等功能
"""
import os
import logging
from pathlib import Path


try:
    from ..__about__ import __version__, __github__
    
except ImportError:
    from aivk.__about__ import __version__, __github__
        

logger = logging.getLogger("aivk.fs")

class AivkFS:
    """
    AIVK 文件系统操作类
    
    提供初始化、挂载 AIVK 根目录等文件系统操作
    """
    # 定义为普通类变量，而不是 pydantic 模型字段
    AIVK_ROOT: Path = Path(os.getenv("AIVK_ROOT", str(Path().home() / ".aivk")))

    @classmethod
    def dir(cls, dir: str, exist: bool) -> Path:
        """
        获取指定目录路径
        
        :return: 指定目录路径
        """
        path = cls.AIVK_ROOT / dir

        if not path.exists() and exist:
            # 创建目录
            path.mkdir(parents=True, exist_ok=exist)
        return path

    @classmethod
    def file(cls, file: str, exist: bool = True) -> Path:
        """
        获取指定文件路径
        
        :param file: 文件路径
        :param exist: 是否确保文件存在，默认为 True
        :return: 指定文件路径
        """
        path = cls.AIVK_ROOT / file

        if not path.exists() and exist:
            # 确保父目录存在
            parent_dir = path.parent
            parent_dir.mkdir(parents=True, exist_ok=True)
            # 创建文件
            path.touch(exist_ok=True)
        return path

    @classmethod
    def meta_file(cls, id: str, exist: bool = True) -> Path:
        """
        获取指定 ID 的元文件路径
        
        :param id: 文件 ID
        :param exist: 是否允许文件已存在，默认为 True
        :return: 指定 ID 的元文件路径
        """
        path = cls.file(f"etc/{id}/meta.toml", exist)

        return path
    

    @classmethod
    def config_file(cls, id: str, exist: bool = True) -> Path:
        """
        获取指定 ID 的配置文件路径
        
        :param id: 文件 ID
        :param exist: 是否允许文件已存在，默认为 True
        :return: 指定 ID 的配置文件路径
        """
        path = cls.file(f"etc/{id}/config.toml", exist)

        return path

