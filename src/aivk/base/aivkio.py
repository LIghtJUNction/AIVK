from datetime import datetime
import os
from pathlib import Path
import shutil
import toml
from .fs import AivkFS
from ..__about__ import __version__, __github__ , __root__
from ..base.utils import AivkExecuter

class AivkIO:
    """AIVK IO类"""
    # 定义为普通类变量，不作为模型字段
    AIVK_ROOT: Path = Path(os.getenv("AIVK_ROOT", str(Path().home() / ".aivk")))
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
        
        :param force: 是否强制初始化，如果为True则覆盖现有目录
        :return: 初始化后的 AIVK 根目录路径
        """
        import logging
        logger = logging.getLogger("aivk.io")
        
        # 确保AivkFS.AIVK_ROOT与AivkIO.AIVK_ROOT同步
        AivkFS.AIVK_ROOT = cls.AIVK_ROOT
        logger.debug(f"尝试初始化AIVK根目录: {cls.AIVK_ROOT}, force={force}")

        # 检查目录是否已经初始化
        dotaivk = cls.AIVK_ROOT / ".aivk"
        if dotaivk.exists() and not force:
            logger.warning(f"AIVK 根目录已初始化，跳过初始化步骤: {cls.AIVK_ROOT}")
            return cls.AIVK_ROOT

        # 执行初始化
        if cls.AIVK_ROOT.exists() and force:
            # 检查是否为空
            if any(cls.AIVK_ROOT.iterdir()):
                shutil.rmtree(cls.AIVK_ROOT)
                logger.warning(f"强制初始化 AIVK 根目录: {cls.AIVK_ROOT} \n 已清空!")
            else:
                logger.info(f"当前 AIVK 根目录为空: {cls.AIVK_ROOT}")

        root_path = cls.AIVK_ROOT
        logger.debug(f"创建AIVK根目录: {root_path}")
        try:
            root_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"AIVK根目录创建成功: {root_path}")
        except Exception as e:
            logger.error(f"创建AIVK根目录失败: {e}")
            raise RuntimeError(f"创建AIVK根目录失败: {e}")
        
        # 创建基本目录结构
        logger.debug("开始创建基本目录结构...")
        # 修改 basic_dirs 列表，确保 aivk_agent 在 src 目录下创建
        basic_dirs = ["etc", "etc/aivk", "cache", "data", "tmp", "home" , "src" , "src/aivk_agent"]
        for dir_name in basic_dirs:
            dir_path = root_path / dir_name
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"目录创建成功: {dir_path}")
            except Exception as e:
                logger.error(f"创建目录 {dir_name} 失败: {e}")
                raise RuntimeError(f"创建基本目录结构失败: {e}")

        # 在 src/aivk_agent 目录下创建 __init__.py 文件
        init_py_path = root_path / "src" / "aivk_agent" / "__init__.py"
        py_typed_path = root_path / "src" / "aivk_agent" / "py.typed"
        try:
            init_py_path.touch(exist_ok=True)
            logger.debug(f"创建 __init__.py 文件成功: {init_py_path}")
            py_typed_path.touch(exist_ok=True)
            logger.debug(f"创建 py.typed 文件成功: {py_typed_path}")
        except Exception as e:
            logger.error(f"创建 __init__.py/py.typed 文件失败: {e}")
            # 虽然失败，但不一定是致命错误，继续执行
            # raise RuntimeError(f"创建 __init__.py 文件失败: {e}")

        # 创建基本的 .aivk 文件，确保结构与预期一致
        logger.debug(f"创建 .aivk 标记文件: {dotaivk}")
        try:
            import toml
            import datetime
            import platform
            
            current_time = datetime.datetime.now().isoformat()
            aivk_info = {
                "metadata": {
                    "aivk": __github__,
                    "version": __version__,  
                    "created": current_time,
                    "updated": current_time,
                    "path": str(root_path)
                },
                "system": {
                    "os": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                    "python": platform.python_version()
                },
                # 添加模块部分，用于记录已注册模块
                "modules": {}
            }
            
            # 以文本模式写入确保换行符处理正确
            with open(dotaivk, 'w', encoding='utf-8') as f:
                toml.dump(aivk_info, f)
            logger.info(f".aivk 标记文件创建成功: {dotaivk}")
        except Exception as e:
            logger.error(f"创建 .aivk 标记文件失败: {e}")
            raise RuntimeError(f"创建 .aivk 标记文件失败: {e}")
            
        # 创建基本配置文件
        config_path = root_path / "etc" / "aivk" / "config.toml"
        logger.debug(f"创建配置文件: {config_path}")
        try:
            import toml
            config = {
                "port": 10140,
                "host": "localhost",
                "created_at": current_time,
                "updated_at": current_time
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                toml.dump(config, f)
            logger.info(f"配置文件创建成功: {config_path}")
        except Exception as e:
            logger.error(f"创建配置文件失败: {e}")
            raise RuntimeError(f"创建配置文件失败: {e}")
            
        # 创建基本元数据文件    
        meta_path = root_path / "etc" / "aivk" / "meta.toml"
        logger.debug(f"创建元数据文件: {meta_path}")
        try:
            import toml
            meta = {
                "version": __version__,
                "github": __github__,
                "AIVK_ROOT": str(root_path),
                "created_at": current_time,
                "updated_at": current_time,
                "init_force": force
            }
            with open(meta_path, 'w', encoding='utf-8') as f:
                toml.dump(meta, f)
            logger.info(f"元数据文件创建成功: {meta_path}")
        except Exception as e:
            logger.error(f"创建元数据文件失败: {e}")
            raise RuntimeError(f"创建元数据文件失败: {e}")
        
        pyproject_path = root_path / "pyproject.toml"

        toml.dump(__root__, open(pyproject_path, 'w', encoding='utf-8'))
        logger.info(f"pyproject.toml 文件创建成功: {pyproject_path}")
        await AivkExecuter.aexec(cmd="uv sync", shell=True, cwd=root_path)

        logger.info(f"AIVK 根目录初始化完成: {root_path}")
        return root_path
    

    @classmethod
    async def fs_mount(cls) -> Path:
        """挂载AIVK_ROOT目录
        
        :return: 挂载后的 AIVK 根目录路径
        """
        import logging
        logger = logging.getLogger("aivk.io")
        
        # 确保AivkFS.AIVK_ROOT与AivkIO.AIVK_ROOT同步
        AivkFS.AIVK_ROOT = cls.AIVK_ROOT
        logger.debug(f"开始挂载AIVK根目录: {cls.AIVK_ROOT}")
        
        # 检查根目录是否存在
        if not cls.AIVK_ROOT.exists():
            logger.error(f"AIVK 根目录不存在: {cls.AIVK_ROOT}")
            raise FileNotFoundError(f"AIVK 根目录不存在: {cls.AIVK_ROOT}，请先初始化")
        
        # 检查.aivk文件是否存在
        dotaivk = cls.AIVK_ROOT / ".aivk"
        if not dotaivk.exists():
            logger.error(f"AIVK 根目录未初始化，.aivk 标记文件不存在: {dotaivk}")
            raise FileNotFoundError("AIVK 根目录未初始化，请先运行 'aivk init'")
        
        try:
            # 读取.aivk文件，验证格式
            import toml
            logger.debug(f"读取 .aivk 标记文件: {dotaivk}")
            dotaivk_content = toml.load(dotaivk)
            
            # 检查是否包含必要的字段
            if "metadata" not in dotaivk_content:
                logger.warning(".aivk 文件格式不正确，缺少 metadata 部分")
                # 尝试修复
                dotaivk_content["metadata"] = {
                    "aivk": "https://github.com/LIghtJUNction/AIVK",
                    "version": __version__,
                    "created": datetime.now().isoformat(),
                    "updated": datetime.now().isoformat(),
                    "path": str(cls.AIVK_ROOT)
                }
                logger.info("已自动添加缺失的 metadata 部分")
            
            # 更新访问时间
            dotaivk_content["metadata"]["accessed"] = datetime.now().isoformat()
            dotaivk_content["updated_at"] = datetime.now().isoformat()
            
            # 将修改保存回文件
            with open(dotaivk, 'w', encoding='utf-8') as f:
                toml.dump(dotaivk_content, f)
            logger.debug("已更新 .aivk 文件的访问时间")
            
            # 检查基本目录结构是否完整
            basic_dirs = ["etc", "etc/aivk", "cache", "data", "tmp", "home"]
            missing_dirs = []
            for dir_name in basic_dirs:
                dir_path = cls.AIVK_ROOT / dir_name
                if not dir_path.exists():
                    missing_dirs.append(dir_name)
                    logger.warning(f"缺少目录: {dir_path}")
                    dir_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"已创建缺失目录: {dir_path}")
            
            if missing_dirs:
                logger.warning(f"挂载过程中发现并修复了缺失的目录: {', '.join(missing_dirs)}")
            
            # 调用底层mount方法
            logger.debug("调用 AivkFS.mount()")
            path = await AivkFS.mount()
            logger.info(f"成功挂载AIVK根目录: {path}")
            
            # 启动时读取已保存的模块ID
            module_ids = cls.get_module_ids()
            logger.debug(f"读取模块ID列表: 找到 {len(module_ids)} 个")
            
            # 将读取到的ID添加到已注册集合中，防止重复注册
            for module_id in module_ids:
                cls.__registered_ids.add(module_id)
                logger.debug(f"已注册模块ID: {module_id}")
            
            if module_ids:
                logger.info(f"已加载 {len(module_ids)} 个模块ID")
            
            return path
            
        except FileNotFoundError as e:
            logger.error(f"挂载失败: 文件不存在: {e}")
            raise FileNotFoundError(f"挂载失败: {e}")
        except toml.TomlDecodeError as e:
            logger.error(f"挂载失败: .aivk 文件格式错误: {e}")
            raise ValueError(f"AIVK根目录损坏，.aivk 文件格式错误: {e}")
        except Exception as e:
            logger.error(f"挂载AIVK根目录失败: {e}")
            raise RuntimeError(f"挂载AIVK根目录失败: {e}")
    

    @classmethod
    def get_config(cls, id : str) -> dict:
        """获取配置文件
        
        :param id: 配置ID
        :return: 配置字典，如果加载失败则返回空字典
        """
        
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
                logger.error("AIVK 根目录未初始化，无法添加模块 ID")
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

