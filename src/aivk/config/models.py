from __future__ import annotations

from pathlib import Path
import asyncio
from typing import Any, Literal, TypeVar, overload, Generic

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from logging import getLogger
from datetime import datetime

from ..base import AivkFS
from .base import AivkConfigBase

# 直接导入 AivkConfigV1 以改善类型推断
from .v1 import AivkConfigV1

T = TypeVar('T', bound=AivkConfigBase)

logger = getLogger("aivk.config.models")

class AivkConfigMeta(type):
    """
    Aivk配置元类
    用于在创建配置类时自动注册到AIVK配置系统。
    sqlite数据库有且只有一个喵
    """
    def __new__(mcs, name: str, bases: tuple[type,...], namespace: dict[str, Any]):
        cls = super().__new__(mcs, name, bases, namespace)
        
        # 初始化类级别的属性
        if not hasattr(cls, 'async_lock'):
            cls.async_lock = asyncio.Lock()
        if not hasattr(cls, 'engine'):
            cls.engine = None
        if not hasattr(cls, 'config_dict'):
            cls.config_dict = {}
        logger.debug(f"Creating AivkConfig class: {name}")
        return cls

    def __setattr__(cls, name: str, value: Any) -> None:
        return super().__setattr__(name, value)
    
    def __getattr__(cls, name: str) -> Any:
        return super().__getattribute__(name)

class AivkConfig(Generic[T], metaclass=AivkConfigMeta):
    """
    Aivk配置类
    用于管理AIVK的配置文件和模块配置。
    """
    async_lock: asyncio.Lock
    engine: AsyncEngine
    config_dict: dict[str, AivkConfigBase | AsyncEngine]

    def __delattr__(self, name: str) -> None:
        """
        删除配置属性
        """
        if hasattr(self, name):
            super().__delattr__(name)
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    @classmethod
    def _validate_tree(cls, tree: str) -> bool:
        """
        白名单模式
        验证配置树的格式
        :param tree: 配置树名称
        """
        if tree.count('.') >= 1:
            parts = tree.split('.')
            # 第一位是id位 不可包含_，且不能为空
            if not parts[0] or '_' in parts[0]:
                return False
            # 后面全部位置 文件夹名.文件名
            for part in parts[1:]:
                # 利用内置方法验证 满足 Python 标识符的规则即可，且不能为空
                if not part or not part.isidentifier():
                    return False
            return True
        # 其余情况一律不通过
        return False

    @classmethod
    @overload
    async def getConfig(cls, 
                        tree: str = "aivk.meta", 
                        default: dict[Any, Any] = {} , 
                        format: Literal["sqlite"] = "sqlite"
                        ) -> AsyncEngine: ...
    
    @classmethod
    @overload  
    async def getConfig(cls, 
                        tree: str = "aivk.meta", 
                        default: dict[Any, Any] = {} , 
                        format: Literal["json", "toml"] = "json", 
                        base: type[AivkConfigV1] = AivkConfigV1
                        ) -> AivkConfigV1: ...

    @classmethod
    async def getConfig(cls, 
                        tree: str = "aivk.meta", 
                        default: dict[Any, Any] = {} , 
                        format : Literal["json", "toml", "sqlite"] = "json", 
                        base: type[AivkConfigBase] | None = None
                        ) -> AivkConfigBase | AsyncEngine:
        """
        获取AIVK配置 (异步版本)
        配置树使用示例：
        example:
        >>> root_config = await AivkConfig.getConfig('aivk.meta') # /etc/meta.json
        >>> load_config = await AivkConfig.getConfig('load.meta') # /home/load/etc/meta.json    
        >>> any_config = await AivkConfig.getConfig('id.file_name') # /home/id/file_name.json
        
        """
        if not cls._validate_tree(tree):
            raise ValueError(f"Invalid tree format: {tree}")
        
        # 运行时导入默认配置类，避免循环依赖
        if base is None:
            base = AivkConfigV1
        
        # 确保 base 不为 None
        assert base is not None
        
        if not default:
            default["id"] = f"{tree}#{format}"
            default["created_at"] = datetime.now().isoformat()

        id , *_path = tree.split('.')

        # 生成配置文件路径
        fs: AivkFS = AivkFS.getFS(id)
        _path[-1] = f"{_path[-1]}.{format}"
        relative_path = '/'.join(_path) 
        cfg_path = fs.etc / relative_path

        if format == "json" or format == "toml":
            # 对于 JSON/TOML 格式，先检查缓存
            async with cls.async_lock:
                config_key = f"{tree}#{format}"
                if config_key in cls.config_dict:
                    return cls.config_dict[config_key]
                # 确保目录存在
                fs.etc.mkdir(parents=True, exist_ok=True)
                # 异步加载配置
                config = await base.load(path=cfg_path, default=default)
                cls.config_dict[config_key] = config
                return config
        elif format == "sqlite":
            # SQLite格式 (异步处理)
            db_path: Path = AivkFS.root / "aivk.db"
            # 确保目录存在
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with cls.async_lock:
                config_key = f"{tree}#{format}"
                if config_key in cls.config_dict:
                    return cls.config_dict[config_key]
                
                # 使用异步引擎
                engine: AsyncEngine = create_async_engine(f"sqlite+aiosqlite:///{db_path.as_posix()}")
                cls.config_dict[config_key] = engine
                return engine
        else:
            raise ValueError(f"Unsupported format: {format}")