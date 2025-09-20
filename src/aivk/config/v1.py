from pathlib import Path
from typing import Any, Self
import toml
import json
import aiofiles

from .base import AivkConfigBase

from logging import getLogger
logger = getLogger("aivk.config.v1")

class AivkConfigV1(AivkConfigBase):
    """
    AIVK配置V1版本
    继承自AivkConfigBase
    用于存储AIVK的配置数据
    请继承这个类 喵
    """

    DEFAULT: dict[Any, Any] = {"警告": "缺少默认配置喵！"}
    
    @classmethod
    async def load(cls, path: Path, default: dict[Any, Any]) -> Self:
        """
        异步加载配置
        :param path: 配置文件路径
        """
        logger.debug(f"异步加载配置文件：{path}")
        # GET文件格式喵
        format = path.suffix.lstrip('.').lower()

        if not path.exists() or not path.is_file():
            # 新建并写入默认配置
            # 新建文件目录
            path.parent.mkdir(parents=True, exist_ok=True)

            # 异步写入默认配置
            match format:
                case 'json':
                    async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                        data: dict[Any , Any] = default
                        await f.write(json.dumps(data, ensure_ascii=False, indent=4))
                case 'toml':
                    async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                        data: dict[Any , Any] = default
                        await f.write(toml.dumps(data))
                case _:
                    raise ValueError(f"Unsupported file format: {format}. Supported formats are: json, toml.")
        
        # 异步读取配置文件（无论是新建的还是已存在的）
        match format:
            case 'json':
                async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    if not content.strip():  # 处理空文件情况
                        data: dict[Any , Any] = default
                    else:
                        data: dict[Any , Any] = json.loads(content)
            case 'toml':
                async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    if not content.strip():  # 处理空文件情况
                        data: dict[Any , Any] = default
                    else:
                        data: dict[Any , Any] = toml.loads(content)
            case _:
                raise ValueError(f"Unsupported file format: {format}. Supported formats are: json, toml.")

        # pydantic模型验证
        config =  cls.model_validate(data) 
        config._default = default
        config._format = format  # 保存格式信息
        config._path = path  # 设置配置文件路径

        return config
    
    async def save(self) -> None:
        """
        异步保存配置
        将内存值同步回文件
        """
        logger.debug(f"异步保存配置到文件：{self.path}")
        
        # 确保目录存在
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        # 获取文件格式
        format = self.format

        # 异步写入配置文件
        match format:
            case 'json':
                async with aiofiles.open(self.path, 'w', encoding='utf-8') as f:
                    data: dict[Any, Any] = self.model_dump()
                    await f.write(json.dumps(data, ensure_ascii=False, indent=4))
            case 'toml':
                async with aiofiles.open(self.path, 'w', encoding='utf-8') as f:
                    data: dict[Any, Any] = self.model_dump()
                    await f.write(toml.dumps(data))
            case _:
                raise ValueError(f"Unsupported file format: {format}. Supported formats are: json, toml.")
        
        logger.debug(f"配置已异步保存到：{self.path}")
            
    async def reload(self) -> None:
        """
        异步重新加载配置
        从文件中读取最新配置并更新内存
        """
        logger.debug(f"异步重新加载配置文件：{self.path}")
        
        # 重新加载配置
        reloaded_config = await self.load(self.path, self.default)
        
        # 更新当前实例的所有字段
        for field_name, field_value in reloaded_config.model_dump().items():
            setattr(self, field_name, field_value)
        
        # 更新内部属性
        self._default = getattr(reloaded_config, '_default', {})
        self._format = getattr(reloaded_config, '_format', 'json')  
        self._path = getattr(reloaded_config, '_path', self.path)
        
        logger.debug(f"配置已从文件异步重新加载：{self.path}")
    