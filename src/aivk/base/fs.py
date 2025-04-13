"""
文件系统操作模块，包含 AIVK 文件系统初始化、挂载等功能
"""

import os
import shutil
import logging
import datetime
from pathlib import Path
import toml

try:
    from ..base.models import GlobalVar
    from ..__about__ import __version__, __github__
    from .utils import AivkExecuter
except ImportError:
    from aivk.base.models import GlobalVar
    from aivk.__about__ import __version__, __github__
    from aivk.base.utils import AivkExecuter

logger = logging.getLogger("aivk.fs")

class AivkFS:
    """
    AIVK 文件系统操作类
    
    提供初始化、挂载 AIVK 根目录等文件系统操作
    """
    
    @classmethod
    async def initialize(cls, path: Path = None, force: bool = False) -> Path:
        """
        初始化 AIVK 根目录
        
        Args:
            path: AIVK 根目录路径，如不提供则使用默认路径
            force: 是否强制覆盖现有目录
            
        Returns:
            Path: 初始化的 AIVK 根目录路径
            
        Raises:
            FileExistsError: 如果目录已存在且 force=False
            Exception: 初始化过程中的其他错误
        """
        # 使用 GlobalVar 获取默认根目录
        path = path if path else GlobalVar.get_aivk_root()
        logger.info(f"初始化 AIVK 根目录: {path} (force={force})")
        
        if path.exists() and not force:
            msg = f"路径 {path} 已存在。使用 --force / -f 覆盖。"
            logger.error(msg)
            raise FileExistsError(msg)
        
        if path.exists() and force:
            logger.warning(f"路径 {path} 已存在。正在覆盖...")
            
            # 在删除前先获取目录内容
            def list_dir_contents(dir_path, prefix=""):
                contents = []
                try:
                    for item in os.listdir(dir_path):
                        item_path = os.path.join(dir_path, item)
                        contents.append(f"{prefix}├── {item}")
                        if os.path.isdir(item_path):
                            sub_contents = list_dir_contents(item_path, prefix + "│   ")
                            contents.extend(sub_contents)
                except PermissionError:
                    contents.append(f"{prefix}├── <无法访问>")
                return contents
            
            # 获取要删除的目录内容
            contents = list_dir_contents(path)
            
            # 输出将被删除的内容
            if contents:
                logger.info("即将删除以下内容:")
                for item in contents:
                    logger.info(item)
            
            # 删除目录
            shutil.rmtree(path, ignore_errors=True)
        
        try:
            # 创建根目录
            path.mkdir(exist_ok=force, parents=True)
            
            # 创建必要的子目录
            (path / "cache").mkdir(exist_ok=True)
            (path / "tmp").mkdir(exist_ok=True)
            (path / "data").mkdir(exist_ok=True)
            (path / "etc").mkdir(exist_ok=True)
            (path / "home").mkdir(exist_ok=True)
            
            # 创建配置目录
            etc_aivk_dir = path / "etc" / "aivk"
            etc_aivk_dir.mkdir(exist_ok=True, parents=True)
            
            # 更新 GlobalVar 中的根目录设置
            GlobalVar.set_aivk_root(path)
            
            # 新建 .aivk 根标记文件
            await cls._create_dotaivk_file(path)
            
            # 创建 MCP 配置文件
            await cls._create_mcp_config(path)
            
            # 创建 AIVK 元数据配置文件
            await cls._create_aivk_meta(path)
            
            # 初始化为 uv 项目
            logger.info("正在初始化 uv 项目...")
            # 创建一个有效的项目名称 (不以点开头)
            uv_project_name = "aivk_root"
            
            try:
                # 首先尝试在目标目录中创建一个简单的 pyproject.toml 文件
                pyproject_file = path / "pyproject.toml"
                with open(pyproject_file, "w") as f:
                    f.write(f"""[project]
name = "{uv_project_name}"
version = "0.1.0"
description = "AIVK Environment"
requires-python = ">=3.10"
readme = "README.md"
authors = [
    {{name = "AIVK", email = "lightjunction.me@gmail.com"}}
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["."]

[tool.hatch.build]
exclude = [
    "/.git",
    "/.github",
    "/docs",
    "/tests",
    "/.gitignore",
]
""")
                
                readme_file = path / "README.md"
                with open(readme_file, "w") as f:
                    f.write(f"# {uv_project_name}\n\nAIVK Environment - Python Virtual Environment for AIVK")
                
                # 验证文件是否确实创建
                if not readme_file.exists():
                    logger.warning("无法创建 README.md 文件，尝试以不同的方式创建")
                    # 备用方式创建
                    with open(str(path / "README.md"), "w") as f:
                        f.write(f"# {uv_project_name}\n\nAIVK Environment")
                
                logger.info(f"已创建配置文件: {pyproject_file} 和 {readme_file}")
                
                # 然后尝试uv 刷新
                result = await AivkExecuter.aexec(
                    command=f"cd {str(path)} && uv sync",
                    shell=True,
                    stream_output=True,
                    logger=logger
                )
                
                logger.info(f"uv虚拟环境创建结果: {result}")
                
                
            except Exception as e:
                logger.warning(f"UV 初始化失败: {e}")
                logger.warning("继续初始化过程...")
            
            logger.info(f"AIVK 成功初始化于 {path}")
            return path
            
        except Exception as e:
            logger.error(f"AIVK 初始化失败: {e}")
            raise
    
    @classmethod
    async def _create_dotaivk_file(cls, path: Path) -> None:
        """创建 .aivk 配置文件"""
        dotaivk_file = path / ".aivk"
        dotaivk_file.touch(exist_ok=True)
        
        dotaivk = {}
        now = str(datetime.datetime.now())
        
        # 基本元数据
        dotaivk["metadata"] = {
            "aivk": __github__,
            "version": __version__,
            "created": now,
            "updated": now,
            "path": str(path)
        }
        
        # 系统信息
        import platform
        dotaivk["system"] = {
            "os": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python": platform.python_version()
        }
        
        with open(dotaivk_file, "w") as f:
            toml.dump(dotaivk, f)
        
        logger.debug(f"创建 .aivk 配置文件: {dotaivk_file}")
    
    @classmethod
    async def _create_mcp_config(cls, path: Path) -> None:
        """创建 MCP 配置文件"""
        mcp_file = path / "etc" / "mcp.toml"
        mcp_file.touch(exist_ok=True)
        
        mcp = {}
        mcp["metadata"] = {"updated": str(datetime.datetime.now())}
        mcp["config"] = {"mcpServers": {}}
        
        # 添加 AIVK MCP 服务器配置
        mcp["config"]["mcpServers"]["aivk"] = {
            "name": "AIVK MCP",
            "type": "stdio",
            "command": "aivk",
            "args": ["mcp", "--stdio"],
            "enabled": True
        }

        with open(mcp_file, "w") as f:
            toml.dump(mcp, f)
            
        logger.debug(f"创建 MCP 配置文件: {mcp_file}")
    
    @classmethod
    async def _create_aivk_meta(cls, path: Path) -> None:
        """创建 AIVK 元数据配置文件"""
        meta_file = path / "etc" / "aivk" / "meta.toml"
        meta_file.touch(exist_ok=True)
        
        aivk_meta = {}
        aivk_meta["metadata"] = {"updated": str(datetime.datetime.now())}
        
        # 模块配置
        aivk_meta["modules"] = {
            "fs": {
                "enabled": False,  
                "version": "latest",
                "pypi": "aivk-fs",
            },
            "ai": {
                "enabled": False,
                "version": "latest",
                "pypi": "aivk-ai",
            },
            "webui": {
                "enabled": False,
                "version": "latest",
                "pypi": "aivk-webui",
            },
        }
        
        with open(meta_file, "w") as f:
            toml.dump(aivk_meta, f)
            
        logger.debug(f"创建 AIVK 元数据配置文件: {meta_file}")
            
    @classmethod
    async def mount(cls, path: Path = None) -> bool:
        """
        挂载 AIVK 根目录
        
        Args:
            path: AIVK 根目录路径，如不提供则使用默认路径
            
        Returns:
            bool: 是否成功挂载
            
        Raises:
            FileNotFoundError: 如果目录不存在
            Exception: 挂载过程中的其他错误
        """
        # 使用 GlobalVar 获取默认根目录
        path = path if path else GlobalVar.get_aivk_root()
        logger.info(f"挂载 AIVK 根目录: {path}")
        
        if not path.exists():
            msg = f"路径 {path} 不存在。请先使用 'aivk init' 进行初始化。"
            logger.error(msg)
            raise FileNotFoundError(msg)
            
        try:
            # 检查 .aivk 标记文件是否存在
            dotaivk_file = path / ".aivk"
            if not dotaivk_file.exists():
                raise ValueError(f"无效的 AIVK 根目录: {path}，缺少 .aivk 标记文件")
            
            # 读取配置文件
            with open(dotaivk_file, "r") as f:
                config = toml.load(f)
                
            # 更新访问时间
            config["metadata"]["accessed"] = str(datetime.datetime.now())
            
            # 将更新写回配置文件
            with open(dotaivk_file, "w") as f:
                toml.dump(config, f)
            
            # 更新 GlobalVar 中的根目录设置
            GlobalVar.set_aivk_root(path)
            logger.info(f"AIVK 成功挂载于 {path}")
            
            return True
            
        except Exception as e:
            logger.error(f"AIVK 挂载失败: {e}")
            raise
    
    @classmethod
    def is_initialized(cls, path: Path = None) -> bool:
        """
        检查 AIVK 是否已初始化
        
        Args:
            path: AIVK 根目录路径，如不提供则使用默认路径
            
        Returns:
            bool: 是否已初始化
        """
        # 使用 GlobalVar 获取默认根目录
        path = path if path else GlobalVar.get_aivk_root()
        dotaivk_file = path / ".aivk"
        
        return path.exists() and dotaivk_file.exists()
    
    @classmethod
    def get_root_path(cls) -> Path:
        """
        获取 AIVK 根目录路径
        
        Returns:
            Path: AIVK 根目录路径
        """
        # 直接从 GlobalVar 获取根目录
        return GlobalVar.get_aivk_root()

# 简便的函数接口

async def initialize(path: Path = None, force: bool = False) -> Path:
    """初始化 AIVK 根目录"""
    return await AivkFS.initialize(path, force)

async def mount(path: Path = None) -> bool:
    """挂载 AIVK 根目录"""
    return await AivkFS.mount(path)

def is_initialized(path: Path = None) -> bool:
    """检查 AIVK 是否已初始化"""
    return AivkFS.is_initialized(path)

def get_root_path() -> Path:
    """获取 AIVK 根目录路径"""
    return AivkFS.get_root_path()