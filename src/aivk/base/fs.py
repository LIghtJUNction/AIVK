"""
文件系统操作模块，包含 AIVK 文件系统初始化、挂载等功能
"""

import os
import shutil
import logging
import datetime
from pathlib import Path
from typing import Union
import toml

try:
    from ..__about__ import __version__, __github__
    from .utils import AivkExecuter
except ImportError:
    from aivk.__about__ import __version__, __github__
    from aivk.base.utils import AivkExecuter

logger = logging.getLogger("aivk.fs")

class AivkFS:
    """
    AIVK 文件系统操作类
    
    提供初始化、挂载 AIVK 根目录等文件系统操作
    """
    AIVK_ROOT: Path = Path(os.getenv("AIVK_ROOT", str(Path().home() / ".aivk")))

    @classmethod
    def dir(cls, dir: str , exist : bool) -> Path:
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
        

        :return: 指定文件路径
        """
        path = cls.AIVK_ROOT / file

        if not path.exists() and exist:
            path.touch(exist_ok=True)
        return path

    @classmethod
    def meta_file(cls, id: str , exist: bool = True) -> Path:
        """
        获取指定 ID 的元文件路径
        
        :param id: 文件 ID
        :param exist: 是否允许文件已存在，默认为 True
        :return: 指定 ID 的元文件路径
        """
        path = cls.file(f"etc/{id}/meta.toml", exist)

        return path
    

    @classmethod
    def config_file(cls, id: str , exist: bool = True) -> Path:
        """
        获取指定 ID 的配置文件路径
        
        :param id: 文件 ID
        :param exist: 是否允许文件已存在，默认为 True
        :return: 指定 ID 的配置文件路径
        """
        path = cls.file(f"etc/{id}/config.toml", exist)

        return path

    @classmethod
    async def initialize(cls, force: bool = False) -> Path:
        """
        初始化 AIVK 根目录
        
        :param force: 是否强制初始化，默认为 False
        :return: AIVK 根目录路径
        """
        try:
            # 记录开始初始化的日志
            logger.debug(f"开始初始化 AIVK 根目录: {cls.AIVK_ROOT}")
            
            dotaivk = cls.AIVK_ROOT / ".aivk"
            if dotaivk.exists() and not force:
                logger.warning(f"AIVK 根目录已初始化 ")
                return cls.AIVK_ROOT
            
            # 创建 AIVK 根目录
            try:
                cls.AIVK_ROOT.mkdir(parents=True, exist_ok=True)
                logger.debug(f"AIVK 根目录创建成功: {cls.AIVK_ROOT}")
            except Exception as e:
                logger.error(f"创建 AIVK 根目录失败: {e}")
                raise
            
            # 创建基本目录结构
            try:
                cls.dir("etc", True)
                cls.dir("cache", True)
                cls.dir("data", True)
                cls.dir("tmp", True)
                cls.dir("home", True)
                cls.dir("etc/aivk", True)
                logger.debug("基本目录结构创建成功")
            except Exception as e:
                logger.error(f"创建基本目录结构失败: {e}")
                raise
    
            # 创建配置文件
            try:
                config_path = cls.config_file("aivk", True)
                if not config_path.exists() or force:
                    aivk_config = {
                        "port": 10140,
                        "host": "localhost"
                    }
                    with open(config_path, 'w') as f:
                        toml.dump(aivk_config, f)
                    logger.debug(f"配置文件创建成功: {config_path}")
            except Exception as e:
                logger.error(f"创建配置文件失败: {e}")
                raise
    
            # 创建元文件
            try:
                meta_path = cls.meta_file("aivk", True)
                if not meta_path.exists() or force:
                    aivk_meta = {
                        "version": __version__,
                        "github": __github__,
                        "AIVK_ROOT": str(cls.AIVK_ROOT),
                        "created_at": datetime.datetime.now().isoformat(),
                        "updated_at": datetime.datetime.now().isoformat(),
                    }
                    with open(meta_path, 'w') as f:
                        toml.dump(aivk_meta, f)
                    logger.debug(f"元文件创建成功: {meta_path}")
            except Exception as e:
                logger.error(f"创建元文件失败: {e}")
                raise
    
            # 创建 dotaivk 文件
            try:
                dotaivk = cls.file(".aivk", True)
                dotaivk_dict = {
                    "version": __version__,
                    "github": __github__,
                    "AIVK_ROOT": str(cls.AIVK_ROOT),
                    "created_at": datetime.datetime.now().isoformat(),
                    "updated_at": datetime.datetime.now().isoformat(),
                }
                
                with open(dotaivk, 'w') as f:
                    toml.dump(dotaivk_dict, f)
                logger.debug(f".aivk 标记文件创建成功: {dotaivk}")
            except Exception as e:
                logger.error(f"创建 .aivk 标记文件失败: {e}")
                raise
            
            logger.info(f"AIVK 根目录初始化完成: {cls.AIVK_ROOT}")
            return cls.AIVK_ROOT
            
        except Exception as e:
            # 捕获所有异常，记录详细信息并重新抛出
            logger.error(f"初始化 AIVK 根目录失败: {e}")
            raise Exception(f"初始化 AIVK 根目录失败: {e}") from e
    
    @classmethod
    async def mount(cls) -> Path:
        """
        挂载 AIVK 根目录
        
        :return: AIVK 根目录路径
        """
        dotaivk = cls.AIVK_ROOT / ".aivk"
        if not cls.AIVK_ROOT.exists() :
            logger.warning("AIVK 根目录不存在，请先初始化 AIVK 根目录")
            raise FileNotFoundError("AIVK 根目录不存在，请先初始化 AIVK 根目录")
        
        if not dotaivk.exists():
            raise FileNotFoundError(f"AIVK 根目录未初始化，请先初始化 AIVK 根目录")
        
        # 更新 dotaivk 的更新时间
        dotaivk_dict = toml.load(dotaivk)
        dotaivk_dict["updated_at"] = datetime.datetime.now().isoformat()
        
        with open(dotaivk, 'w') as f:
            toml.dump(dotaivk_dict, f)

        return cls.AIVK_ROOT



