"""
基础
"""
import os
import logging
from pathlib import Path
from typing import Self

logger = logging.getLogger("aivk.base.fs")

class AivkFsMeta(type):
    """
    AIVK 文件系统元类
    
    用于注册 AIVK 文件系统操作类
    """
    
    @property
    def aivk_root(cls) -> Path:
        """获取 AIVK 根目录"""
        return Path(os.getenv("AIVK_ROOT", str(Path().home() / ".aivk")))

    @property
    def aivk_data(cls) -> Path:
        """获取 AIVK 数据目录"""
        return cls.aivk_root / "data"
    
    @property
    def aivk_cache(cls) -> Path:
        """获取 AIVK 缓存目录"""
        return cls.aivk_root / "cache"
    
    @property
    def aivk_tmp(cls) -> Path:
        """获取 AIVK 临时目录"""
        return cls.aivk_root / "tmp"

    @property
    def aivk_etc(cls) -> Path:
        """获取 AIVK 配置目录"""
        return cls.aivk_root / "etc"

    @property
    def aivk_meta(cls) -> Path:
        """获取 AIVK 元数据目录"""
        return cls.aivk_etc / "meta.toml"

class AivkFS(metaclass=AivkFsMeta):
    _instances: dict[str, Self] = {}

    @classmethod
    def ensure_fs(cls) -> None:
        """确保 AIVK 文件系统目录存在"""
        cls.aivk_root.mkdir(parents=True, exist_ok=True)
        cls.aivk_meta.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"AIVK 文件系统已初始化: {cls.aivk_root}")

    def __init__(self, id: str = "aivk") -> None:
        """
        初始化 AIVK 文件系统
        
        请使用 AivkFS.getFS() 获取实例，不要直接实例化！
        
        :param id: AIVK ID
        :raises RuntimeError: 当直接实例化时抛出异常
        """

        self.id = id
        if id == "aivk":
            # on system boot
            self.ensure_fs()
        logger.info(f"AIVK 模块加载: {self.id}")

    @classmethod
    def getFS(cls, id: str = "aivk") -> Self:
        """
        获取 AIVK 文件系统实例
        
        :param id: AIVK ID
        :return: AIVK 文件系统实例
        """
        if id not in cls._instances:
            cls._instances[id] = cls(id)
        return cls._instances[id]
    
    @property
    def home(self) -> Path:
        """获取 AIVK 模块主目录"""
        return self.__class__.aivk_root / "home" / self.id if self.id != "aivk" else self.__class__.aivk_root
    
    @property
    def data(self) -> Path:
        """获取 AIVK 模块数据目录"""
        return self.home / "data"
    
    @property
    def cache(self) -> Path:
        """获取 AIVK 模块缓存目录"""
        return self.home / "cache"
    
    @property
    def tmp(self) -> Path:
        """获取 AIVK 模块临时目录"""
        return self.home / "tmp"
    
    @property
    def etc(self) -> Path:
        """获取 AIVK 模块配置目录"""
        return self.home / "etc"

    def __getattr__(self, item: str):
        """
        当访问不存在的属性时报错
        """
        available_paths = [name for name in dir(self) if not name.startswith('_') and isinstance(getattr(self.__class__, name, None), property)]
        raise AttributeError(f"{self.__class__.__name__} 禁止访问 '{item}'。可用路径：{available_paths}")
    

    def __dir__(self) -> list[str]:
        """
        返回 AIVK 文件系统可用路径列表
        """
        return list(self.__class__.__dict__.keys())
    
    def __repr__(self) -> str:
        """
        返回 AIVK 文件系统实例的字符串表示
        """
        return f"<AivkFS id={self.id} >"
    

