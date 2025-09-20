"""
灵活配置类 - 支持动态字段
"""
from pathlib import Path
from typing import Any, Self
import json
import toml
import aiofiles

from .base import AivkConfigBase
from logging import getLogger

logger = getLogger("aivk.config.flexible")

class AivkFlexibleConfig(AivkConfigBase):
    """
    灵活的AIVK配置类
    支持动态字段，适用于不确定结构的配置
    """
    
    model_config = {"extra": "allow"}  # 允许额外字段
    
    @classmethod
    async def load(cls, path: Path, default: dict[Any, Any]) -> Self:
        """
        异步加载配置
        支持动态字段的配置加载
        """
        logger.debug(f"异步加载灵活配置文件：{path}")
        format = path.suffix.lstrip('.').lower()

        if not path.exists() or not path.is_file():
            path.parent.mkdir(parents=True, exist_ok=True)
            
            match format:
                case 'json':
                    async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                        await f.write(json.dumps(default, ensure_ascii=False, indent=4))
                case 'toml':
                    async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                        await f.write(toml.dumps(default))
                case _:
                    raise ValueError(f"Unsupported file format: {format}")
        
        # 读取配置文件
        match format:
            case 'json':
                async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content) if content.strip() else default
            case 'toml':
                async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = toml.loads(content) if content.strip() else default
            case _:
                raise ValueError(f"Unsupported file format: {format}")

        # 创建配置实例 - 使用 **data 来设置动态字段
        config = cls(**data)
        config._default = default
        config._format = format
        config._path = path
        
        return config
    
    async def save(self) -> None:
        """
        异步保存配置
        保存所有动态字段
        """
        logger.debug(f"异步保存灵活配置到文件：{self.path}")
        
        self.path.parent.mkdir(parents=True, exist_ok=True)
        format = self.format

        match format:
            case 'json':
                async with aiofiles.open(self.path, 'w', encoding='utf-8') as f:
                    data = self.model_dump()
                    await f.write(json.dumps(data, ensure_ascii=False, indent=4))
            case 'toml':
                async with aiofiles.open(self.path, 'w', encoding='utf-8') as f:
                    data = self.model_dump()
                    await f.write(toml.dumps(data))
            case _:
                raise ValueError(f"Unsupported file format: {format}")
        
        logger.debug(f"灵活配置已异步保存到：{self.path}")
    
    async def reload(self) -> None:
        """
        异步重新加载配置
        """
        logger.debug(f"异步重新加载灵活配置文件：{self.path}")
        
        reloaded_config = await self.load(self.path, self.default)
        
        # 更新所有字段
        for field_name, field_value in reloaded_config.model_dump().items():
            setattr(self, field_name, field_value)
        
        # 更新内部属性
        self._default = getattr(reloaded_config, '_default', {})
        self._format = getattr(reloaded_config, '_format', 'json')  
        self._path = getattr(reloaded_config, '_path', self.path)
        
        logger.debug(f"灵活配置已从文件异步重新加载：{self.path}")
