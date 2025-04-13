from datetime import datetime
import os
import importlib
import sys
from pathlib import Path
from pydantic import BaseModel
import toml
from .fs import AivkFS


class AivkIO(BaseModel):
    """AIVK IO类"""
    AIVK_ROOT : Path = Path(os.getenv("AIVK_ROOT", str(Path().home() / ".aivk")))
    __registered_ids = set()  # 用于跟踪已注册的ID

    @classmethod
    def set_aivk_root(cls, root: Path) -> None:
        """设置AIVK_ROOT目录"""
        cls.AIVK_ROOT = root
        AivkFS.AIVK_ROOT = root
        os.environ["AIVK_ROOT"] = str(root)
        
    @classmethod
    def get_aivk_root(cls) -> Path:
        """获取AIVK_ROOT目录"""
        return cls.AIVK_ROOT
    
    @classmethod
    def is_aivk_root(cls) -> bool:
        """判断是否是AIVK_ROOT目录"""
        dotaivk_file = AivkFS.file(".aivk", exist=False)
        if not dotaivk_file.exists():
            return False
        return True

    @classmethod
    def get_path(cls, path: str) -> Path:
        """获取路径"""
        # 这里可以添加其他路径的处理逻辑
        return cls.AIVK_ROOT / path
    
    @classmethod
    async def fs_init(cls, force: bool = False) -> Path:
        """初始化AIVK_ROOT目录
        
        :param force: 是否强制初始化
        :return: 初始化后的 AIVK 根目录路径
        """
        return await AivkFS.initialize(force=force)

    @classmethod
    async def fs_mount(cls) -> Path:
        """挂载AIVK_ROOT目录
        
        :return: 挂载后的 AIVK 根目录路径
        """
        path = await AivkFS.mount()
        
        # 启动时读取已保存的模块ID
        module_ids = cls.get_module_ids()
        if module_ids:
            import logging
            logger = logging.getLogger("aivk.io")
            logger.info(f"已加载 {len(module_ids)} 个模块ID")
        
        # 将读取到的ID添加到已注册集合中，防止重复注册
        for module_id in module_ids:
            cls.__registered_ids.add(module_id)
            
        return path
    
    @classmethod
    def _check_and_register_caller(cls):
        """检查调用方并尝试注册其ID"""
        # 如果AIVK根目录未初始化，跳过注册过程
        if not cls.is_aivk_root():
            return
            
        import inspect
        import logging
        logger = logging.getLogger("aivk.io")
        
        # 获取调用栈
        stack = inspect.stack()
        
        # 跳过本方法和直接调用方法，从实际业务调用处开始查找
        for frame in stack[2:]:
            module = inspect.getmodule(frame[0])
            if module:
                module_name = module.__name__
                
                # 检查是否是 AIVK 模块（以 aivk_ 开头或等于 aivk 或aivk的子模块）
                parts = module_name.split('.')
                top_module = parts[0]
                
                if top_module == "aivk" or top_module.startswith("aivk_"):
                    # 已注册的模块跳过
                    if top_module in cls.__registered_ids:
                        return
                    
                    # 获取模块信息
                    try:
                        mod = sys.modules.get(top_module)
                        if mod:
                            module_info = {}
                            if hasattr(mod, "__id__"):
                                module_info["id"] = getattr(mod, "__id__")
                            if hasattr(mod, "__version__"):
                                module_info["version"] = getattr(mod, "__version__")
                            if hasattr(mod, "__github__"):
                                module_info["github"] = getattr(mod, "__github__")
                                
                            # 添加到模块ID列表
                            if cls.add_module_id(top_module, **module_info):
                                cls.__registered_ids.add(top_module)
                                logger.debug(f"自动注册模块ID: {top_module}")
                    except Exception as e:
                        logger.debug(f"尝试注册模块ID时出错 [{top_module}]: {e}")
                    
                    # 只处理找到的第一个AIVK模块
                    break

    @classmethod
    def get_config(cls, id : str) -> dict:
        """获取配置文件
        
        :param id: 配置ID
        :return: 配置字典，如果加载失败则返回空字典
        """
        # 检查并注册调用方
        cls._check_and_register_caller()
        
        config_path = AivkFS.config_file(id, exist=True)
        
        try:
            config = toml.load(config_path)
            return config
        except Exception as e:
            # 记录错误信息
            import logging
            logger = logging.getLogger("aivk.io")
            logger.warning(f"加载配置文件失败 [{id}]: {e}")
            # 如果加载失败，返回空字典
            return {}
        
    @classmethod
    def save_config(cls, id : str, config: dict) -> bool:
        """保存配置文件
        
        :param id: 配置ID
        :param config: 配置字典
        :return: 是否保存成功
        """
        # 检查并注册调用方
        cls._check_and_register_caller()
        
        try:
            config_path = AivkFS.config_file(id, exist=True)
            # 确保目录存在
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, "w") as f:
                toml.dump(config, f)

            aivk_meta = cls.get_meta("aivk")
            aivk_meta["updated_at"] = datetime.now().isoformat()
            cls.save_meta("aivk", aivk_meta)

            return True
        except Exception as e:
            # 记录错误信息
            import logging
            logger = logging.getLogger("aivk.io")
            logger.error(f"保存配置文件失败 [{id}]: {e}")
            return False

    @classmethod
    def get_meta(cls, id : str) -> dict:
        """获取元数据文件
        
        :param id: 元数据ID
        :return: 元数据字典，如果加载失败则返回空字典
        """
        # 检查并注册调用方
        cls._check_and_register_caller()
        
        meta_path = AivkFS.meta_file(id, exist=True)
        
        try:
            meta = toml.load(meta_path)
            return meta
        except Exception as e:
            # 记录错误信息
            import logging
            logger = logging.getLogger("aivk.io")
            logger.warning(f"加载元数据文件失败 [{id}]: {e}")
            # 如果加载失败，返回空字典
            return {}
        
    @classmethod
    def save_meta(cls, id : str, meta: dict) -> bool:
        """保存元数据文件
        
        :param id: 元数据ID
        :param meta: 元数据字典
        :return: 是否保存成功
        """
        # 检查并注册调用方
        cls._check_and_register_caller()
        
        try:
            meta_path = AivkFS.meta_file(id, exist=True)
            # 确保目录存在
            meta_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(meta_path, "w") as f:
                toml.dump(meta, f)
            return True
        except Exception as e:
            # 记录错误信息
            import logging
            logger = logging.getLogger("aivk.io")
            logger.error(f"保存元数据文件失败 [{id}]: {e}")
            return False

    @classmethod
    def add_module_id(cls, module_id: str, **kwargs) -> bool:
        """将模块 ID 添加到 .aivk 标记文件的 [modules] 部分
        
        :param module_id: 模块 ID
        :param kwargs: 附加信息，如版本、github等
        :return: 是否添加成功
        """
        try:
            # 获取 .aivk 文件路径
            dotaivk_file = AivkFS.file(".aivk", exist=False)
            if not dotaivk_file.exists():
                # 如果文件不存在，表示尚未初始化
                import logging
                logger = logging.getLogger("aivk.io")
                logger.error(f"AIVK 根目录未初始化，无法添加模块 ID")
                return False
                
            # 读取现有内容
            dotaivk_dict = toml.load(dotaivk_file)
            
            # 确保 modules 部分存在
            if "modules" not in dotaivk_dict:
                dotaivk_dict["modules"] = {}
                
            # 添加模块 ID 及其信息
            module_info = {
                "added_at": datetime.now().isoformat()
            }
            
            # 添加额外信息
            module_info.update(kwargs)
            
            # 如果模块已存在，更新信息而不是完全覆盖
            if module_id in dotaivk_dict["modules"]:
                existing_info = dotaivk_dict["modules"][module_id]
                # 保留原始添加时间
                if "added_at" in existing_info:
                    module_info["added_at"] = existing_info["added_at"]
                # 合并其他信息
                dotaivk_dict["modules"][module_id].update(module_info)
            else:
                # 新模块直接添加
                dotaivk_dict["modules"][module_id] = module_info
            
            # 更新 updated_at 字段
            dotaivk_dict["updated_at"] = datetime.now().isoformat()
            
            # 保存回文件
            with open(dotaivk_file, "w") as f:
                toml.dump(dotaivk_dict, f)
                
            return True
        except Exception as e:
            # 记录错误信息
            import logging
            logger = logging.getLogger("aivk.io")
            logger.error(f"添加模块 ID 失败: {e}")
            return False
    
    @classmethod
    def get_module_ids(cls) -> dict:
        """从 .aivk 标记文件读取所有模块 ID
        
        :return: 模块 ID 字典，如果加载失败则返回空字典
        """
        try:
            # 获取 .aivk 文件路径
            dotaivk_file = AivkFS.file(".aivk", exist=False)
            if not dotaivk_file.exists():
                # 如果文件不存在，返回空字典
                return {}
                
            # 读取文件内容
            dotaivk_dict = toml.load(dotaivk_file)
            
            # 返回 modules 部分，如果不存在则返回空字典
            return dotaivk_dict.get("modules", {})
        except Exception as e:
            # 记录错误信息
            import logging
            logger = logging.getLogger("aivk.io")
            logger.error(f"读取模块 ID 失败: {e}")
            return {}

