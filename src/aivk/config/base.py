from abc import abstractmethod ,ABC
from pathlib import Path
from typing import Any, ClassVar, Self
from pydantic import BaseModel, ConfigDict

from logging import getLogger

from ..base import AivkFS

logger = getLogger("aivk.config.base")

class AivkConfigBase(BaseModel, ABC):
    """
    Base configuration model for AIVK.
    继承本类 创建双向同步配置T = TypeVar('T', bound='AivkConfigBase')
    不对外公开
    请使用 AivkConfig.getConfig() 方法获取配置类
    """
    _path : Path = AivkFS.root  # 默认配置文件路径
    _format: str = 'json'  # 默认文件格式
    model_config: ClassVar[ConfigDict] = ConfigDict(extra='allow' )  # 允许额外字段
    @property
    def default(self) -> dict[Any, Any]:
        """
        获取默认配置
        优先返回实例的 _default，回退到默认配置
        """
        return getattr(self, '_default', {"警告": "缺少默认配置！"})
    
    @default.setter
    def default(self, value: dict[Any, Any]) -> None:
        """
        设置默认配置
        :param value: 默认配置字典
        """
        self._default = value  # 设置实例变量
        logger.debug(f"设置实例默认配置，_default = {value}")

    @property
    def path(self) -> Path:
        """
        获取配置文件路径
        :return: 配置文件路径
        """
        return getattr(self, '_path' )

    @path.setter
    def path(self, value: Path) -> None:
        """
        设置配置文件路径
        :param value: 配置文件路径
        """
        self._path = value  # 设置实例变量
        logger.debug(f"设置实例配置文件路径，_path = {value}")
    
    @property
    def format(self) -> str:
        """
        获取配置文件格式
        :return: 配置文件格式
        """
        return getattr(self, '_format', 'json')
    
    @format.setter
    def format(self, value: str) -> None:
        """
        设置配置文件格式
        :param value: 配置文件格式
        """
        self._format = value  # 设置实例变量
        logger.debug(f"设置实例配置文件格式，_format = {value}")

    @classmethod
    @abstractmethod
    async def load(cls, path: Path, default: dict[Any, Any]) -> Self:
        """
        异步加载配置
        :param path: 配置文件路径
        :param default: 默认配置字典
        """
        ...

    @abstractmethod
    async def save(self) -> None:
        """
        异步保存配置
        将内存值同步回文件
        """
        ...

    @abstractmethod
    async def reload(self) -> None:
        """
        异步重新加载配置
        从文件中读取最新配置并更新内存
        """
        ...

    def __del__(self):
        """
        对象销毁时调用，保存配置
        """
        try:
            # 注意：析构函数中不能使用await，这里保持同步版本作为备份
            # 建议在主程序中手动调用async save()
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                # 检查事件循环是否正在运行且未关闭
                if loop and not loop.is_closed() and loop.is_running():
                    # 如果有运行中的事件循环，创建任务
                    loop.create_task(self.save())
                else:
                    logger.debug("析构时事件循环不可用，跳过异步保存")
            except RuntimeError:
                # 没有运行中的事件循环，跳过保存
                logger.debug("析构时无法异步保存配置，请确保在程序结束前手动调用save()")
            logger.debug("对象销毁时尝试自动保存配置")
        except Exception as e:
            logger.debug(f"析构时保存配置失败: {e}")
