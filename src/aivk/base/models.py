from typing import ClassVar, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from pathlib import Path
import os
import toml

class Config(BaseModel):
    """AIVK 配置类，管理所有配置项"""
    port: int = 10140
    host: str = "localhost"
    AIVK_ROOT: Path = Path(os.getenv("AIVK_ROOT", str(Path().home() / ".aivk")))
    
    @classmethod
    def load_from_file(cls, config_path: Optional[Path] = None) -> 'Config':
        """从配置文件加载配置"""
        if config_path is None:
            # 默认配置文件路径
            config_path = cls().AIVK_ROOT / "etc" / "aivk" / "meta.toml"
            
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    meta = toml.load(f)
                    config_data = meta.get("config", {})
                return cls(**config_data)
            except Exception as e:
                print(f"Warning: Failed to load config from {config_path}: {e}")
        
        # 如果无法加载配置文件，返回默认配置
        return cls()
    
    def save_to_file(self, config_path: Optional[Path] = None) -> None:
        """保存配置到文件"""
        if config_path is None:
            # 默认配置文件路径
            config_path = self.AIVK_ROOT / "etc" / "aivk" / "meta.toml"
            
        # 确保目录存在
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        meta = toml.load(config_path)

        meta["config"] = self.model_dump()
        with open(config_path, "w") as f:
            toml.dump(meta, f)


        print(f"Configuration saved to {config_path}")

class GlobalVar:
    """全局变量存储类"""
    # 私有存储
    _storage: Dict[str, Any] = {}
    
    # 默认配置实例
    _config = Config()
    
    @classmethod
    def get_config(cls) -> Config:
        """获取当前配置"""
        return cls._config
    
    @classmethod
    def load_config(cls, config_path: Optional[Path] = None) -> Config:
        """加载配置"""
        cls._config = Config.load_from_file(config_path)
        return cls._config
    
    @classmethod
    def save_config(cls, config_path: Optional[Path] = None) -> None:
        """保存当前配置"""
        cls._config.save_to_file(config_path)
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """获取全局变量"""
        # 优先从存储中获取
        if key in cls._storage:
            return cls._storage[key]
        
        # 其次尝试从配置中获取
        if hasattr(cls._config, key):
            return getattr(cls._config, key)
        
        # 最后尝试从环境变量获取
        env_key = f"AIVK_{key.upper()}"
        if env_key in os.environ:
            return os.environ[env_key]
        
        # 都不存在则返回默认值
        return default
    
    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """设置全局变量"""
        cls._storage[key] = value
        
        # 如果是配置类的属性，也更新配置
        if hasattr(cls._config, key):
            setattr(cls._config, key, value)
    
    # 便捷访问方法
    @classmethod
    def get_port(cls) -> int:
        """获取端口号"""
        return cls.get("port", 10140)
    
    @classmethod
    def get_host(cls) -> str:
        """获取主机名"""
        return cls.get("host", "localhost")
    
    @classmethod
    def get_aivk_root(cls) -> Path:
        """获取AIVK根目录"""
        root_path = cls.get("AIVK_ROOT", Path().home() / ".aivk")
        if isinstance(root_path, str):
            return Path(root_path)
        return root_path
    
    # 数据存储区
    data: Dict[str, Any] = {}