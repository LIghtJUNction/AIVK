"""AIVK CLI 命令行模块"""

import logging
from typing import Optional, Any # Import Optional and Any

import click
from pydantic import BaseModel
from anytree import NodeMixin

logger = logging.getLogger("aivk.cli")

class AivkCLI(BaseModel, NodeMixin):
    """AIVK CLI 入口模块"""
    cli_parent : Optional["AivkCLI"] = None # 父节点 (重命名以避免冲突)
    nodes : dict[str, "AivkCLI"] = {} # 节点字典
    id: str  # 节点 ID
    cli: Optional[click.Group] = None  # 命令行对象 (恢复 Optional)

    class Config:
        arbitrary_types_allowed = True  # 允许任意类型的字段

    @classmethod  
    def _validate_id(cls, id: str) -> str:
        """验证节点ID是否符合规范"""
        if id.startswith("aivk-"):
            raise ValueError("ID不能以'aivk'开头")

    @classmethod
    def on(cls,action: str, id : str )-> callable:
        """装饰器，用于注册命令行操作
        动态导入
        返回函数
        """
        cls._validate_id(id)
        import importlib

        pypi_name = f"aivk-{id}" if id != "aivk" else "aivk"
        # from aivk-id.onAction import action
        module_name = f"{pypi_name}.on{action.capitalize()}" 
        try:
            module = importlib.import_module(module_name)
            return getattr(module, action) # 返回函数
        except ImportError as e:
            logger.error(f"导入模块失败: {module_name}，请检查模块是否存在")
            raise e
    

    class AivkGroup(click.Group):

        def list_commands(self, ctx):
            """列出所有命令"""
            cmds = super().list_commands(ctx) # 调用父类方法
            return sorted(cmds)
        
        def get_command(self, ctx, cmd_name):
            command = super().get_command(ctx, cmd_name)
            if command is None:
                # 如果命令不存在
                try :
                    command = AivkCLI.on(action= "cli" , id = cmd_name)
                    self.add_command(command) # 这是一个group 由其他模块提供
                except Exception as e:
                    logger.error(f"获取命令失败: {cmd_name}，请检查是否安装该命令")
                    logger.warning(f"使用aivk install {cmd_name}安装该aivk模块")
                    raise e
            return command  
            

    def __init__(self, id: str, **data: Any): # 保持 Pydantic V2 兼容性
        super().__init__(id=id, **data)  # 显式调用 BaseModel 的初始化
        NodeMixin.__init__(self)  # 调用 NodeMixin 的初始化
        self._validate_id(id)  # 验证 ID
        self.nodes[id] = self  # 将节点添加到字典中 (恢复)

        logger.debug(f"创建节点: {self.id}")

    def __repr__(self) -> str:
        return f"AivkCLI(id={self.id})"


