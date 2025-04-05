import logging
import datetime
import os
from pathlib import Path
from typing import Any, Dict, Union, Optional
from enum import Enum

from pydantic import BaseModel, model_validator
import toml

try:
    from .. import __LOGO__, __WELCOME__
except ImportError:
    from aivk import __LOGO__, __WELCOME__

logger = logging.getLogger("aivk.core.aivk_root")


class ResourceType(Enum):
    """AIVK资源类型枚举"""
    MODULES = "modules"
    MODULES_BAK = "modules_bak"
    MODULES_UPDATE = "modules_update"
    CACHE = "cache"
    DATA = "data"
    LOGS = "logs"
    TMP = "tmp"
    
    def __str__(self) -> str:
        """返回资源类型的字符串表示"""
        return self.value


class AivkRoot(BaseModel):
    """
    AIVK root directory.
    """
    # 修复类型问题，确保aivk_root是Path对象
    aivk_root : Path = Path(os.environ.get("AIVK_ROOT", str(Path.home() / ".aivk")))
    
    # 在访问这些属性时确保它们被计算为Path对象
    @property
    def cache(self) -> Path:
        return self.aivk_root / "cache"
    
    @property
    def data(self) -> Path:
        return self.aivk_root / "data"
    
    @property
    def logs(self) -> Path:
        return self.aivk_root / "logs"
    
    @property
    def tmp(self) -> Path:
        return self.aivk_root / "tmp"
    
    @property
    def modules(self) -> Path:
        return self.aivk_root / "modules"
    
    @property
    def modules_bak(self) -> Path:
        return self.aivk_root / "modules_bak"
    
    @property
    def modules_update(self) -> Path:
        return self.aivk_root / "modules_update"

    # aivk 元文件
    @property
    def meta(self) -> Path:
        return self.aivk_root / "meta.toml"
    
    # 定义验证方法，确保aivk_root总是Path对象
    @model_validator(mode='before')
    @classmethod
    def set_paths(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        # 如果数据是字典形式
        if isinstance(data, dict):
            aivk_root = data.get('aivk_root')
            if isinstance(aivk_root, str):
                data['aivk_root'] = Path(aivk_root)
            elif aivk_root is None:
                # 使用默认路径
                data['aivk_root'] = Path(os.environ.get("AIVK_ROOT", str(Path.home() / ".aivk")))
        return data

    def _get_sha256(self, path: Path) -> str:
        """
        Get the SHA256 hash of a file or directory.
        """
        import hashlib

        if not path.exists():
            return ""

        if path.is_file():
            with open(path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        elif path.is_dir():
            combined_hash = hashlib.sha256()
            # 排序确保每次计算结果一致
            for file_path in sorted(path.iterdir()):
                # 添加文件名到哈希中
                combined_hash.update(file_path.name.encode())
                # 递归调用自身计算文件或子目录的哈希
                file_hash = self._get_sha256(file_path)
                combined_hash.update(file_hash.encode())
            
            return combined_hash.hexdigest()
        
        return ""

    def _check_integrity(self, path: Path , hash: str) -> bool:
        """
        Check if the SHA256 hash of a file or directory matches the given hash.
        """
        calculated_hash = self._get_sha256(path)

        """ 
        发生变化时，返回True
        """
        return not calculated_hash == hash

    def _update_meta_sha256(self, meta_data: dict , dir_name: str) -> bool:
        """
        Update the SHA256 hash of a file or directory in the meta data.
        """
        # 键名： <dir_name>_sha256 
        key_sha256 = f"{dir_name}_sha256"
        hash_value = self._get_sha256(getattr(self, dir_name))
        if key_sha256 not in meta_data:
            meta_data[key_sha256] = hash_value
            return True
        
        # 如果SHA256值发生变化，_check_integrity返回True
        if self._check_integrity(getattr(self, dir_name), hash_value):
            # 成功更新SHA256值
            logger.info(f"SHA256 hash for {key_sha256} has changed")
            logger.info(f"{meta_data[key_sha256]} -> {hash_value}")
            meta_data[key_sha256] = hash_value
            return True
        # 无变化 不更新 -> False
        return False
    
    
    # ###################################################################################
    """
    root directory structure:
    ├── aivk_root
    │   ├── cache
    │   │   ├── <module_id> -- 模块名称 仅限缓存数据 核心模块使用 作用：缓存数据，减少重复计算
    │   │   |  |——— meta.toml -- 元数据 自定义
    │   │   |
    │   │   |———meta.toml -- 元数据 来自根模块 aivk
    │   │   |——— anything -- 其他数据 aivk 视为根模块 因此放在根目录下 
    │   │   |
    │   │   |
    │   ├── data
    │   │   ├── <module_id> -- 模块名称
    │   │   |  |——— meta.toml -- 元数据 自定义
    │   │   |  |——— anything -- 其他数据 持久化存储
    │   │   |  
    │   │   |——meta.toml -- 元数据 来自根模块 aivk
    │   │   |—— anything -- 其他数据 aivk 视为根模块 因此放在根目录下
    │   │   |
    │   ├── logs
    │   │   ├── <module_id> -- 模块名称 仅限日志数据
    │   │   |  |——— meta.toml -- 元数据 自定义
    │   │   |  |——— <module_id>.log -- 模块日志文件
    │   │   |
    |   |   |———meta.toml -- 元数据 来自根模块 aivk  
    │   │   |——aivk.log -- AIVK日志文件 aivk 视为根模块 因此日志文件放在根目录下
    │   │   |
    │   ├── tmp
    │   │   ├── <module_id> -- 模块名称 仅限临时数据
    |   │   │   |——— meta.toml -- 元数据 自定义
    │   │   |   |——— anything -- 其他数据 临时数据
    |   │   │   
    │   │   |———meta.toml -- 元数据 来自根模块 aivk
    |   |   |——— anything -- 其他数据 临时数据 来自根模块 aivk 
    |   |   |
    │   ├── modules -- 模块目录
    │   │   ├── <module_id> -- 模块名称 请勿在本目录下放置任何数据文件！临时文件请放在tmp目录下！其他数据请放在data目录下！
    │   │   |  |——— meta.toml -- 模块元数据
    │   │   |  |——— module_id.py -- 模块入口文件
    │   │   |  |——— .disable -- 模块禁用标记
    │   │   |
    |   │   |———meta.toml -- 元数据 来自核心模块 aivk.loader
    │   │   |
    │   │   |
    │   ├── modules_bak -- 备份模块目录
    │   │   ├── <module_id> -- 模块名称 仅限备份数据
    │   │   |  |——— meta.toml -- 元数据 自定义
    │   │   |  |—— ...同上
    │   │   |
    │   ├── modules_update -- 借鉴至magisk模块设计 当模块更新时 先放在此目录下
    |   │   ├── <module_id> -- 新模块 用于更新，如果更新成功，则覆盖至modules目录下
    │   │   |  |—— ... 同上
    │   │   |  
    |   |   |———meta.toml -- 元数据 来自核心模块 aivk.loader
    │   └── meta.toml -- AIVK meta file 
    │
    └── README.MD -- AIVK root directory structure
    """
    def _create_dirs(self) -> bool:
        """
        Create a directory in the AIVK root directory.
        """
        try:
            logger.info(f"AIVK根目录: {self.aivk_root}")
            for dir in [self.cache, self.data, self.logs, self.tmp,
                        self.modules, self.modules_bak, self.modules_update]:
                rel_path = dir.relative_to(self.aivk_root)
                if not dir.exists():
                    logger.info(f"创建目录: {rel_path}")
                    dir.mkdir(parents=True, exist_ok=True)
                else:
                    logger.warning(f"目录已存在: {rel_path}")
            
        except Exception as e:
            logger.error(f"创建目录时出错: {e}")
            return False
        
        return True
    
    def _create_files(self) -> bool:
        """
        Create a file in the AIVK root directory.
        """
        try:
            # 创建根目录下的meta.toml
            meta_rel_path = self.meta.relative_to(self.aivk_root)
            if not self.meta.exists():
                logger.info(f"创建文件: {meta_rel_path}")
                with open(self.meta, "w") as f:
                    f.write("# AIVK Meta File\n")
            else:
                logger.warning(f"文件已存在: {meta_rel_path}")
            
            # 创建.aivk标记文件，用于标识目录已初始化
            aivk_mark_file = self.aivk_root / ".aivk"
            if not aivk_mark_file.exists():
                logger.info("创建AIVK标记文件: .aivk")
                with open(aivk_mark_file, "w") as f:
                    f.write("# AIVK Directory\n")
                    f.write(f"created = \"{datetime.datetime.now().isoformat()}\"\n")
            else:
                logger.warning("AIVK标记文件已存在: .aivk")
            
            # 为各个主要目录创建meta.toml文件
            for dir_path in [self.cache, self.data, self.logs, self.tmp, 
                           self.modules, self.modules_bak, self.modules_update]:
                meta_path = dir_path / "meta.toml"
                meta_rel_path = meta_path.relative_to(self.aivk_root)
                if not meta_path.exists():
                    logger.info(f"创建元数据文件: {meta_rel_path}")
                    with open(meta_path, "w") as f:
                        f.write(f"# {dir_path.name} Meta File\n")
                        f.write(f"created = \"{datetime.datetime.now().isoformat()}\"\n")
                        f.write(f"directory = \"{dir_path.name}\"\n")
                else:
                    logger.warning(f"元数据文件已存在: {meta_rel_path}")
            
        except Exception as e:
            logger.error(f"创建文件时出错: {e}")
            return False
        
        return True

    def create_module_meta(self, directory_type: str, module_id: str) -> Path:
        """
        Create a meta.toml file for a specific module in the specified directory.
        
        Args:
            directory_type: The type of directory (cache, data, logs, tmp)
            module_id: Module ID
            
        Returns:
            Path to the created meta.toml file
            
        Raises:
            ValueError: If directory_type is invalid
        """
        if directory_type not in ["cache", "data", "logs", "tmp"]:
            raise ValueError(f"Invalid directory type for module meta: {directory_type}")
        
        directory = getattr(self, directory_type)
        module_dir = directory / module_id
        
        # 确保模块目录存在
        if not module_dir.exists():
            module_rel_dir = module_dir.relative_to(self.aivk_root)
            logger.info(f"创建模块目录: {module_rel_dir}")
            module_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建模块特定的meta.toml
        meta_path = module_dir / "meta.toml"
        meta_rel_path = meta_path.relative_to(self.aivk_root)
        if not meta_path.exists():
            logger.info(f"创建模块元数据文件: {meta_rel_path}")
            with open(meta_path, "w") as f:
                f.write(f"# {module_id} Meta File in {directory_type}\n")
                f.write(f"created = \"{datetime.datetime.now().isoformat()}\"\n")
                f.write(f"module_id = \"{module_id}\"\n")
                f.write(f"directory = \"{directory_type}\"\n")
        else:
            logger.warning(f"模块元数据文件已存在: {meta_rel_path}")
            
        return meta_path

    @classmethod
    def init(cls, aivk_root: Path | str) -> "AivkRoot":
        """
        Initialize the AIVK root directory structure.
        """
        # Create the AIVK root directory if it doesn't exist
        if isinstance(aivk_root, str):
            aivk_root = Path(aivk_root)
        logger.info(f"开始初始化: {aivk_root}")
        
        # 创建实例
        instance = cls(aivk_root=aivk_root)
        
        if not instance._create_dirs():
            raise RuntimeError("Failed to create necessary directories.")
        if not instance._create_files():
            raise RuntimeError("Failed to create necessary files.")
     
        return instance
    
    # ################################################################################
    
    def _check_dir_exists(self) -> bool:
        """
        Check if a directory exists.
        """
        if not self.aivk_root.exists():
            logger.error(f"Directory does not exist: {self.aivk_root}")
            return False
        
        for dir_name in [self.cache, self.data, self.logs, self.tmp,
                         self.modules, self.modules_bak, self.modules_update]:
            if not dir_name.exists():
                logger.error(f"Directory does not exist: {dir_name}")
                return False
        return True


    def _check_critical_files(self) -> bool:
        """
        Check if critical files exist.
        """
        if not self.meta.exists():
            logger.error(f"Critical file does not exist: {self.meta}")
            return False
        
        # 检查.aivk标记文件是否存在
        aivk_mark_file = self.aivk_root / ".aivk"
        if not aivk_mark_file.exists():
            logger.error(f"AIVK标记文件不存在: {aivk_mark_file}")
            return False
        
        # Add more critical files checks as needed
        return True

    @classmethod
    def mount(cls, aivk_root: Path | str) -> "AivkRoot":
        """
        Mount aivk_root to the AIVK root directory.
        """
        if isinstance(aivk_root, str):
            aivk_root = Path(aivk_root)

        logger.info(f"Mounting aivk_root: {aivk_root}")

        # 创建实例
        instance = cls(aivk_root=aivk_root)

        if not instance._check_dir_exists():
            raise FileNotFoundError("Aivk root directory structure does not contain all required directories.")
        
        if not instance._check_critical_files():
            raise FileNotFoundError("Aivk root directory structure does not contain all required files.")
        
        # 分析meta.toml文件
        with open(instance.meta, "r") as f:
            meta_data = toml.load(f)
        
        # 计算时间间隔
        last_mount_time = meta_data.get("last_mount", 'N/A')
        logger.info(f"Last mount time: {last_mount_time}")
        if last_mount_time != 'N/A':
            logger.info(f"{__LOGO__}")
            last_mount_time = datetime.datetime.fromisoformat(last_mount_time)
            current_time = datetime.datetime.now()
            time_difference = current_time - last_mount_time
            logger.info(f"距离上次挂载：{time_difference}")
            meta_data["last_mount"] = current_time.isoformat()
        else:
            print(f"{__WELCOME__}")
            current_time = datetime.datetime.now()
            meta_data["last_mount"] = current_time.isoformat()
            
        with open(instance.meta, "w") as f:
            instance._update_meta_sha256(meta_data, "cache")
            instance._update_meta_sha256(meta_data, "data")
            instance._update_meta_sha256(meta_data, "modules")
            instance._update_meta_sha256(meta_data, "modules_bak")  
            instance._update_meta_sha256(meta_data, "modules_update")  
            instance._update_meta_sha256(meta_data, "tmp")
            instance._update_meta_sha256(meta_data, "logs")
            toml.dump(meta_data, f)
        
        return instance

    @staticmethod
    def rmtree(path: Path, ignore_errors: bool = False) -> bool:
        """
        递归删除目录及其内容，类似于shutil.rmtree
        
        Args:
            path: 要删除的目录路径
            ignore_errors: 是否忽略错误
            
        Returns:
            删除成功返回True，否则返回False
        """
        import shutil
        try:
            if path.exists():
                # 尝试获取相对路径，以提高日志可读性
                try:
                    # 尝试从父目录获取根目录的路径
                    if path.parent and path.parent.exists():
                        root_dir = path.parent
                        rel_path = path.relative_to(root_dir)
                        logger.info(f"删除目录树: {rel_path} (在 {root_dir})")
                    else:
                        logger.info(f"删除目录树: {path}")
                except (ValueError, AttributeError):
                    # 如果无法获取相对路径，则使用完整路径
                    logger.info(f"删除目录树: {path}")
                
                shutil.rmtree(path, ignore_errors=ignore_errors)
                return True
            return False
        except Exception as e:
            logger.error(f"删除目录树时出错: {e}")
            if ignore_errors:
                return False
            raise


    # #################################################################################
    # 重要方法：
    # 0. {module_id} = True/False -- 模块是否启用 / 或者是否使用 例如： data/{module_id}/meta.toml 存在，如果模块未使用data目录，则标记为False 意思是该模块不使用data目录
    # 1. 遍历modules目录 并更新 modules/meta.toml文件 内容： {module_id} = True/False
    # 2. 遍历modules_bak目录 并更新 modules_bak/meta.toml文件 内容： {module_id} = True/False
    # 3. 遍历modules_update目录 并更新 modules_update/meta.toml文件 内容： {module_id} = True/False
    # 4. 遍历cache目录 并更新 cache/meta.toml文件 内容： {module_id} = True/False
    # 5. 遍历data目录 并更新 data/meta.toml文件 内容： {module_id} = True/False
    # 6. 遍历logs目录 并更新 logs/meta.toml文件 内容： {module_id} = True/False
    # 7. 遍历tmp目录 并更新 tmp/meta.toml文件 内容： {module_id} = True/False
    
    # 8. 同样的，再来7个@property，计算时间戳，更新这一堆meta.toml文件里的时间戳
    # 9. 同样的，再来7个@property，分别更新 meta.toml文件里： [sha256] {module_id} = sha256值 对模块文件夹进行摘要计算

    # 10. 最后来一个@property 一次性更新上述所有的meta.toml文件！

    # #################################################################################
    def _get_meta_path(self, directory_type: str, module_id: str = None) -> Path:
        """
        Get the path to a meta.toml file.
        
        Args:
            directory_type: The type of directory (cache, data, logs, tmp, modules, modules_bak, modules_update)
            module_id: Optional module ID for module-specific meta.toml files
            
        Returns:
            Path to the meta.toml file
        
        Raises:
            ValueError: If directory_type is invalid
        """
        if directory_type not in ["cache", "data", "logs", "tmp", "modules", "modules_bak", "modules_update"]:
            raise ValueError(f"Invalid directory type: {directory_type}")
        
        directory = getattr(self, directory_type)
        
        if module_id:
            # 返回模块特定的meta.toml路径
            return directory / module_id / "meta.toml"
        else:
            # 返回目录根级的meta.toml路径
            return directory / "meta.toml"

    def _update_directory_meta_modules(self, directory_type: str) -> bool:
        """
        遍历指定目录，更新相应meta.toml文件中的模块状态
        
        Args:
            directory_type: 目录类型 (modules, modules_bak, modules_update, cache, data, logs, tmp)
            
        Returns:
            更新成功返回True，否则返回False
        """
        try:
            directory = getattr(self, directory_type)
            if not directory.exists():
                logger.error(f"目录不存在: {directory}")
                return False
                
            # 获取meta.toml文件路径
            meta_path = self._get_meta_path(directory_type)
            if not meta_path.exists():
                logger.warning(f"元数据文件不存在: {meta_path}, 尝试创建")
                with open(meta_path, "w") as f:
                    f.write(f"# {directory_type} Meta File\n")
                    f.write(f"created = \"{datetime.datetime.now().isoformat()}\"\n")
                    f.write(f"directory = \"{directory_type}\"\n")
                    f.write("[modules]\n")  # 添加模块节
            
            # 读取现有meta.toml文件
            meta_data = {}
            if meta_path.exists():
                with open(meta_path, "r") as f:
                    meta_data = toml.load(f)
            
            # 确保modules节存在
            if "modules" not in meta_data:
                meta_data["modules"] = {}
            
            # 遍历目录中的所有子目录，每个子目录视为一个模块
            module_found = False
            for item in directory.iterdir():
                if item.is_dir() and item.name != "__pycache__":
                    module_id = item.name
                    # 检查是否是模块目录 (具有meta.toml或特定入口文件)
                    is_module = False
                    
                    if directory_type in ["modules", "modules_update"]:
                        # 检查模块目录中是否有meta.toml或模块入口文件
                        module_meta = item / "meta.toml"
                        module_entry = item / f"{module_id}.py"
                        is_module = module_meta.exists() or module_entry.exists()
                    else:
                        # 对于其他目录，只要是子目录就认为是模块目录
                        is_module = True
                    
                    # 更新模块状态
                    if is_module:
                        module_found = True
                        # 检查模块是否已禁用
                        disable_marker = item / ".disable"
                        is_enabled = not disable_marker.exists()
                        
                        meta_data["modules"][module_id] = is_enabled
            
            # 如果没有找到模块，添加提示信息
            if not module_found:
                meta_data["modules"]["_info"] = f"No modules found in {directory_type}"
            
            # 更新修改时间
            meta_data["last_updated"] = datetime.datetime.now().isoformat()
            
            # 写入更新后的meta.toml文件
            with open(meta_path, "w") as f:
                toml.dump(meta_data, f)
            
            logger.info(f"成功更新 {directory_type} 元数据文件")
            return True
            
        except Exception as e:
            logger.error(f"更新 {directory_type} 元数据文件时出错: {e}")
            return False
    
    @property
    def update_modules_meta(self) -> bool:
        """更新modules目录的meta.toml文件内各模块的信息"""
        return self._update_directory_meta_modules("modules")
    
    @property
    def update_modules_bak_meta(self) -> bool:
        """更新modules_bak目录的meta.toml文件内各模块的信息"""
        return self._update_directory_meta_modules("modules_bak")
    
    @property
    def update_modules_update_meta(self) -> bool:
        """更新modules_update目录的meta.toml文件内各模块的信息"""
        return self._update_directory_meta_modules("modules_update")
    
    @property
    def update_cache_meta(self) -> bool:
        """更新cache目录的meta.toml文件内各模块的信息"""
        return self._update_directory_meta_modules("cache")
    
    @property
    def update_data_meta(self) -> bool:
        """更新data目录的meta.toml文件内各模块的信息"""
        return self._update_directory_meta_modules("data")
    
    @property
    def update_logs_meta(self) -> bool:
        """更新logs目录的meta.toml文件内各模块的信息"""
        return self._update_directory_meta_modules("logs")
    
    @property
    def update_tmp_meta(self) -> bool:
        """更新tmp目录的meta.toml文件内各模块的信息"""
        return self._update_directory_meta_modules("tmp")
    
    def _update_directory_meta_timestamp(self, directory_type: str) -> bool:
        """
        更新指定目录meta.toml文件中的时间戳
        
        Args:
            directory_type: 目录类型 (modules, modules_bak, modules_update, cache, data, logs, tmp)
            
        Returns:
            更新成功返回True，否则返回False
        """
        try:
            directory = getattr(self, directory_type)
            if not directory.exists():
                logger.error(f"目录不存在: {directory}")
                return False
                
            # 获取meta.toml文件路径
            meta_path = self._get_meta_path(directory_type)
            if not meta_path.exists():
                logger.warning(f"元数据文件不存在: {meta_path}, 尝试创建")
                with open(meta_path, "w") as f:
                    f.write(f"# {directory_type} Meta File\n")
                    f.write(f"created = \"{datetime.datetime.now().isoformat()}\"\n")
                    f.write(f"directory = \"{directory_type}\"\n")
                    f.write("[timestamps]\n")  # 添加时间戳节
            
            # 读取现有meta.toml文件
            meta_data = {}
            if meta_path.exists():
                with open(meta_path, "r") as f:
                    meta_data = toml.load(f)
            
            # 确保timestamps节存在
            if "timestamps" not in meta_data:
                meta_data["timestamps"] = {}
            
            # 更新目录的时间戳
            current_time = datetime.datetime.now().isoformat()
            meta_data["timestamps"]["last_updated"] = current_time
            
            # 遍历目录中的所有子目录，为每个模块更新时间戳
            for item in directory.iterdir():
                if item.is_dir() and item.name != "__pycache__":
                    module_id = item.name
                    # 更新模块的时间戳
                    meta_data["timestamps"][module_id] = current_time
            
            # 写入更新后的meta.toml文件
            with open(meta_path, "w") as f:
                toml.dump(meta_data, f)
            
            logger.info(f"成功更新 {directory_type} 时间戳")
            return True
            
        except Exception as e:
            logger.error(f"更新 {directory_type} 时间戳时出错: {e}")
            return False
    
    @property
    def update_modules_timestamp(self) -> bool:
        """更新modules目录的时间戳"""
        return self._update_directory_meta_timestamp("modules")
    
    @property
    def update_modules_bak_timestamp(self) -> bool:
        """更新modules_bak目录的时间戳"""
        return self._update_directory_meta_timestamp("modules_bak")
    
    @property
    def update_modules_update_timestamp(self) -> bool:
        """更新modules_update目录的时间戳"""
        return self._update_directory_meta_timestamp("modules_update")
    
    @property
    def update_cache_timestamp(self) -> bool:
        """更新cache目录的时间戳"""
        return self._update_directory_meta_timestamp("cache")
    
    @property
    def update_data_timestamp(self) -> bool:
        """更新data目录的时间戳"""
        return self._update_directory_meta_timestamp("data")
    
    @property
    def update_logs_timestamp(self) -> bool:
        """更新logs目录的时间戳"""
        return self._update_directory_meta_timestamp("logs")
    
    @property
    def update_tmp_timestamp(self) -> bool:
        """更新tmp目录的时间戳"""
        return self._update_directory_meta_timestamp("tmp")
    
    def _update_directory_meta_sha256(self, directory_type: str) -> bool:
        """
        更新指定目录meta.toml文件中的SHA256摘要值
        
        Args:
            directory_type: 目录类型 (modules, modules_bak, modules_update, cache, data, logs, tmp)
            
        Returns:
            更新成功返回True，否则返回False
        """
        try:
            directory = getattr(self, directory_type)
            if not directory.exists():
                logger.error(f"目录不存在: {directory}")
                return False
                
            # 获取meta.toml文件路径
            meta_path = self._get_meta_path(directory_type)
            if not meta_path.exists():
                logger.warning(f"元数据文件不存在: {meta_path}, 尝试创建")
                with open(meta_path, "w") as f:
                    f.write(f"# {directory_type} Meta File\n")
                    f.write(f"created = \"{datetime.datetime.now().isoformat()}\"\n")
                    f.write(f"directory = \"{directory_type}\"\n")
                    f.write("[sha256]\n")  # 添加SHA256节
            
            # 读取现有meta.toml文件
            meta_data = {}
            if meta_path.exists():
                with open(meta_path, "r") as f:
                    meta_data = toml.load(f)
            
            # 确保sha256节存在
            if "sha256" not in meta_data:
                meta_data["sha256"] = {}
            
            # 更新目录的整体SHA256值
            dir_hash = self._get_sha256(directory)
            meta_data["sha256"]["directory"] = dir_hash
            
            # 遍历目录中的所有子目录，为每个模块计算SHA256
            for item in directory.iterdir():
                if item.is_dir() and item.name != "__pycache__":
                    module_id = item.name
                    # 计算模块目录的SHA256值
                    module_hash = self._get_sha256(item)
                    meta_data["sha256"][module_id] = module_hash
            
            # 写入更新后的meta.toml文件
            with open(meta_path, "w") as f:
                toml.dump(meta_data, f)
            
            logger.info(f"成功更新 {directory_type} SHA256摘要")
            return True
            
        except Exception as e:
            logger.error(f"更新 {directory_type} SHA256摘要时出错: {e}")
            return False
    
    @property
    def update_modules_sha256(self) -> bool:
        """更新modules目录的SHA256摘要"""
        return self._update_directory_meta_sha256("modules")
    
    @property
    def update_modules_bak_sha256(self) -> bool:
        """更新modules_bak目录的SHA256摘要"""
        return self._update_directory_meta_sha256("modules_bak")
    
    @property
    def update_modules_update_sha256(self) -> bool:
        """更新modules_update目录的SHA256摘要"""
        return self._update_directory_meta_sha256("modules_update")
    
    @property
    def update_cache_sha256(self) -> bool:
        """更新cache目录的SHA256摘要"""
        return self._update_directory_meta_sha256("cache")
    
    @property
    def update_data_sha256(self) -> bool:
        """更新data目录的SHA256摘要"""
        return self._update_directory_meta_sha256("data")
    
    @property
    def update_logs_sha256(self) -> bool:
        """更新logs目录的SHA256摘要"""
        return self._update_directory_meta_sha256("logs")
    
    @property
    def update_tmp_sha256(self) -> bool:
        """更新tmp目录的SHA256摘要"""
        return self._update_directory_meta_sha256("tmp")
    
    @property
    def update_all_meta(self) -> bool:
        """
        一次性更新所有目录的meta.toml文件内各模块的信息，包括模块状态、时间戳和SHA256摘要
        
        Returns:
            全部更新成功返回True，任一更新失败返回False
        """
        # 保存每个更新操作的结果
        results = []
        
        # 更新模块状态
        results.append(self.update_modules_meta)
        results.append(self.update_modules_bak_meta)
        results.append(self.update_modules_update_meta)
        results.append(self.update_cache_meta)
        results.append(self.update_data_meta)
        results.append(self.update_logs_meta)
        results.append(self.update_tmp_meta)
        
        # 更新时间戳
        results.append(self.update_modules_timestamp)
        results.append(self.update_modules_bak_timestamp)
        results.append(self.update_modules_update_timestamp)
        results.append(self.update_cache_timestamp)
        results.append(self.update_data_timestamp)
        results.append(self.update_logs_timestamp)
        results.append(self.update_tmp_timestamp)
        
        # 更新SHA256摘要
        results.append(self.update_modules_sha256)
        results.append(self.update_modules_bak_sha256)
        results.append(self.update_modules_update_sha256)
        results.append(self.update_cache_sha256)
        results.append(self.update_data_sha256)
        results.append(self.update_logs_sha256)
        results.append(self.update_tmp_sha256)
        
        # 更新根目录的meta.toml文件
        with open(self.meta, "r") as f:
            root_meta_data = toml.load(f)
            
        # 更新根meta.toml的时间戳
        root_meta_data["last_updated"] = datetime.datetime.now().isoformat()
        
        # 写入更新后的根meta.toml文件
        with open(self.meta, "w") as f:
            toml.dump(root_meta_data, f)
        
        # 如果任一更新操作失败，返回False
        return all(results)
    
    # ##################################################################################
    # 资源路径获取的通用方法
    
    def get_resource_path(self, resource_type: Union[ResourceType, str], module_id: str, *path_parts: str) -> Path:
        """
        获取指定资源类型和模块的路径
        
        Args:
            resource_type: 资源类型(ResourceType枚举或字符串)
            module_id: 模块ID
            path_parts: 可选的附加路径部分
            
        Returns:
            资源路径
        """
        # 处理字符串类型的资源类型
        if isinstance(resource_type, str):
            try:
                resource_type = ResourceType(resource_type)
            except ValueError:
                raise ValueError(f"无效的资源类型: {resource_type}")
        
        # 获取基础目录
        base_dir = getattr(self, resource_type.value)
        
        # 确定模块目录路径
        module_dir = base_dir / module_id if module_id != "aivk" else base_dir
        
        # 如果有额外路径部分，拼接它们
        if path_parts:
            return module_dir.joinpath(*path_parts)
        return module_dir
    
    def get_resource_meta_path(self, resource_type: Union[ResourceType, str], module_id: Optional[str] = None) -> Path:
        """
        获取指定资源类型的meta.toml文件路径
        
        Args:
            resource_type: 资源类型(ResourceType枚举或字符串)
            module_id: 可选的模块ID，如果提供则返回模块特定的meta.toml路径
            
        Returns:
            meta.toml文件路径
        """
        # 处理字符串类型的资源类型
        if isinstance(resource_type, str):
            try:
                resource_type = ResourceType(resource_type)
            except ValueError:
                raise ValueError(f"无效的资源类型: {resource_type}")
        
        if module_id:
            # 返回模块特定的meta.toml路径
            return self.get_resource_path(resource_type, module_id, "meta.toml")
        else:
            # 返回资源根目录的meta.toml路径
            base_dir = getattr(self, resource_type.value)
            return base_dir / "meta.toml"
    
    # 兼容性方法 - 这些方法使用新的通用方法实现，但保持原有的接口
    
    def get_module_path(self, module_id: str) -> Path:
        """
        获取指定模块的路径
        
        Args:
            module_id: 模块ID
        
        Returns:
            模块路径
        """
        return self.get_resource_path(ResourceType.MODULES, module_id)
    
    def get_module_bak_path(self, module_id: str) -> Path:
        """
        获取指定模块备份的路径
        
        Args:
            module_id: 模块ID
        
        Returns:
            模块备份路径
        """
        return self.get_resource_path(ResourceType.MODULES_BAK, module_id)
    
    def get_module_update_path(self, module_id: str) -> Path:
        """
        获取指定模块更新的路径
        
        Args:
            module_id: 模块ID
        
        Returns:
            模块更新路径
        """
        return self.get_resource_path(ResourceType.MODULES_UPDATE, module_id)
    
    def get_module_cache_path(self, module_id: str) -> Path:
        """
        获取指定模块缓存的路径
        
        Args:
            module_id: 模块ID
        
        Returns:
            模块缓存路径
        """
        return self.get_resource_path(ResourceType.CACHE, module_id)
    
    def get_module_data_path(self, module_id: str) -> Path:
        """
        获取指定模块数据的路径
        
        Args:
            module_id: 模块ID
            
        Returns:
            模块数据路径
        """
        return self.get_resource_path(ResourceType.DATA, module_id)
    
    def get_module_logs_path(self, module_id: str) -> Path:
        """
        获取指定模块日志的路径
        
        Args:
            module_id: 模块ID
        
        Returns:
            模块日志路径
        """
        return self.get_resource_path(ResourceType.LOGS, module_id)

    def get_module_tmp_path(self, module_id: str) -> Path:
        """
        获取指定模块临时文件的路径
        
        Args:
            module_id: 模块ID
        
        Returns:
            模块临时文件路径
        """
        return self.get_resource_path(ResourceType.TMP, module_id)

    def get_module_meta_path(self, module_id: str) -> Path:
        """
        获取指定模块的meta.toml文件路径
        
        Args:
            module_id: 模块ID
        
        Returns:
            模块meta.toml文件路径
        """
        return self.get_resource_meta_path(ResourceType.MODULES, module_id)
    
    def get_module_bak_meta_path(self, module_id: str) -> Path:
        """
        获取指定模块备份的meta.toml文件路径
        
        Args:
            module_id: 模块ID
        
        Returns:
            模块备份meta.toml文件路径
        """
        return self.get_resource_meta_path(ResourceType.MODULES_BAK, module_id)
    
    def get_module_update_meta_path(self, module_id: str) -> Path:
        """
        获取指定模块更新的meta.toml文件路径
        
        Args:
            module_id: 模块ID
        
        Returns:
            模块更新meta.toml文件路径
        """
        return self.get_resource_meta_path(ResourceType.MODULES_UPDATE, module_id)
    
    def get_module_cache_meta_path(self, module_id: str) -> Path:
        """
        获取指定模块缓存的meta.toml文件路径
        
        Args:
            module_id: 模块ID
            
        Returns:
            模块缓存meta.toml文件路径
        """
        return self.get_resource_meta_path(ResourceType.CACHE, module_id)

    def get_module_data_meta_path(self, module_id: str) -> Path:
        """
        获取指定模块数据的meta.toml文件路径
        
        Args:
            module_id: 模块ID
            
        Returns:
            模块数据meta.toml文件路径
        """
        return self.get_resource_meta_path(ResourceType.DATA, module_id)
    
    # ##################################################################################
    # 便捷方法：获取模块的Entry类 
    # 1. /modules/{module_id}/module_id.py ： Entry类 

    def get_module_entry(self, module_id: str):
        """
        通过moduleId获取并返回模块的Entry类
        
        Args:
            module_id: 要加载的模块ID
            
        Returns:
            模块的Entry类实例，如果模块不存在或加载失败则返回None
            
        Raises:
            ImportError: 如果模块导入失败
            AttributeError: 如果模块中没有Entry类
        """
        try:
            # 检查模块是否可用
            if not self.check_module_status(module_id):
                logger.warning(f"模块 {module_id} 已禁用或不存在")
                return None
                
            # 获取模块路径
            module_path = self.get_module_path(module_id)
            
            # 将模块路径添加到sys.path以便能够导入
            import sys
            if str(module_path) not in sys.path:
                sys.path.insert(0, str(module_path))
                
            # 导入模块
            try:
                # 尝试直接导入
                module = __import__(module_id)
            except ImportError:
                # 如果直接导入失败，尝试相对导入
                module_rel_path = str(self.get_module_entry_path(module_id))
                
                import importlib.util
                spec = importlib.util.spec_from_file_location(module_id, module_rel_path)
                if spec is None:
                    raise ImportError(f"无法加载模块 {module_id} 的规范")
                    
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_id] = module
                spec.loader.exec_module(module)
                
            # 检查模块是否包含Entry类
            if not hasattr(module, 'Entry'):
                raise AttributeError(f"模块 {module_id} 中未找到Entry类")
                
            # 返回Entry类
            logger.info(f"成功加载模块 {module_id} 的Entry类")
            return module.Entry
            
        except Exception as e:
            logger.error(f"加载模块 {module_id} 的Entry类时出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def get_module_entry_path(self, module_id: str) -> Path:
        """
        获取指定模块的入口文件路径
        
        Args:
            module_id: 模块ID
        
        Returns:
            模块入口文件路径
        """
        return self.get_module_path(module_id) / f"{module_id}.py"
    
    def check_module_status(self, module_id: str) -> bool:
        """
        检查模块是否启用
        
        Args:
            module_id: 模块ID
        
        Returns:
            如果模块启用返回True，否则返回False
        """
        module_path = self.get_module_path(module_id)
        
        # 首先检查模块是否存在
        if not module_path.exists():
            logger.warning(f"模块不存在: {module_id}")
            return False
            
        # 检查是否有.disable标记文件
        disable_marker = module_path / ".disable"
        return not disable_marker.exists()
        
    def update_module_status(self, module_id: str, enabled: bool) -> bool:
        """
        更新模块状态（启用/禁用）
        
        Args:
            module_id: 模块ID
            enabled: 是否启用模块
            
        Returns:
            状态更新成功返回True，否则返回False
        """
        module_path = self.get_module_path(module_id)
        
        # 检查模块是否存在
        if not module_path.exists():
            logger.error(f"无法更新不存在的模块状态: {module_id}")
            return False
            
        disable_marker = module_path / ".disable"
        
        if enabled:
            # 启用模块 - 删除.disable标记文件
            if disable_marker.exists():
                disable_marker.unlink()
                logger.info(f"已启用模块: {module_id}")
                return True
            else:
                logger.info(f"模块已经处于启用状态: {module_id}")
                return False
        else:
            # 禁用模块 - 创建.disable标记文件
            if not disable_marker.exists():
                with open(disable_marker, "w") as f:
                    f.write(f"# Module {module_id} is disabled\n")
                    f.write(f"disabled_at = \"{datetime.datetime.now().isoformat()}\"\n")
                logger.info(f"已禁用模块: {module_id}")
                return True
            else:
                logger.info(f"模块已经处于禁用状态: {module_id}")
                return False


# ##################################################################################

# 使用示例
if __name__ == "__main__":
    import sys
    import argparse
    
    # 设置日志级别
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    parser = argparse.ArgumentParser(description='AIVK Root目录管理工具')
    parser.add_argument('action', choices=['init', 'mount', 'update', 'check'], 
                        help='执行的操作: init(初始化), mount(挂载), update(更新元数据), check(检查状态)')
    parser.add_argument('--path', type=str, default=str(Path.home() / ".aivk"), 
                        help='AIVK根目录路径，默认为~/.aivk')
    parser.add_argument('--module', type=str, help='操作的模块ID')
    parser.add_argument('--disable', action='store_true', help='禁用指定模块')
    parser.add_argument('--enable', action='store_true', help='启用指定模块')
    
    args = parser.parse_args()
    
    try:
        if args.action == 'init':
            # 初始化AIVK根目录
            aivk_root = AivkRoot.init(Path(args.path))
            print(f"AIVK根目录初始化成功: {aivk_root.aivk_root}")
            
            # 创建一些示例模块目录和文件
            example_module = "example_module"
            module_path = aivk_root.get_module_path(example_module)
            module_path.mkdir(parents=True, exist_ok=True)
            
            # 创建示例模块的meta.toml和入口文件
            with open(module_path / "meta.toml", "w") as f:
                f.write("# Example Module Meta\n")
                f.write(f"module_id = \"{example_module}\"\n")
                f.write(f"created = \"{datetime.datetime.now().isoformat()}\"\n")
            
            with open(module_path / f"{example_module}.py", "w") as f:
                f.write("# Example Module Entry Point\n")
                f.write("def init():\n")
                f.write("    print(\"Example module initialized\")\n")
                f.write("    return True\n")
            
            # 创建模块的数据和缓存目录
            aivk_root.create_module_meta("data", example_module)
            aivk_root.create_module_meta("cache", example_module)
            
            # 更新所有元数据
            print("更新所有元数据...")
            aivk_root.update_all_meta
            print("元数据更新完成")
            
        elif args.action == 'mount':
            # 挂载现有的AIVK根目录
            aivk_root = AivkRoot.mount(Path(args.path))
            print(f"AIVK根目录挂载成功: {aivk_root.aivk_root}")
            
            # 显示所有目录路径
            print(f"缓存目录: {aivk_root.cache}")
            print(f"数据目录: {aivk_root.data}")
            print(f"日志目录: {aivk_root.logs}")
            print(f"临时目录: {aivk_root.tmp}")
            print(f"模块目录: {aivk_root.modules}")
            print(f"模块备份目录: {aivk_root.modules_bak}")
            print(f"模块更新目录: {aivk_root.modules_update}")
            
        elif args.action == 'update':
            # 更新元数据
            aivk_root = AivkRoot.mount(Path(args.path))
            print(f"更新 {aivk_root.aivk_root} 的元数据...")
            if aivk_root.update_all_meta:
                print("所有元数据更新成功")
            else:
                print("部分元数据更新失败")
                
        elif args.action == 'check':
            # 检查模块状态
            aivk_root = AivkRoot.mount(Path(args.path))
            
            if args.module:
                # 检查特定模块
                module_id = args.module
                module_path = aivk_root.get_module_path(module_id)
                
                if not module_path.exists():
                    print(f"模块不存在: {module_id}")
                    sys.exit(1)
                
                # 更改模块状态
                if args.disable:
                    if aivk_root.update_module_status(module_id, False):
                        print(f"模块已禁用: {module_id}")
                    else:
                        print(f"模块已经处于禁用状态: {module_id}")
                elif args.enable:
                    if aivk_root.update_module_status(module_id, True):
                        print(f"模块已启用: {module_id}")
                    else:
                        print(f"模块已经处于启用状态: {module_id}")
                else:
                    # 只检查状态不修改
                    status = aivk_root.check_module_status(module_id)
                    print(f"模块 {module_id} 当前状态: {'启用' if status else '禁用'}")
                    
                    # 显示模块的各种资源路径
                    print(f"模块路径: {aivk_root.get_module_path(module_id)}")
                    print(f"模块缓存路径: {aivk_root.get_module_cache_path(module_id)}")
                    print(f"模块数据路径: {aivk_root.get_module_data_path(module_id)}")
                    print(f"模块日志路径: {aivk_root.get_module_logs_path(module_id)}")
                    print(f"模块临时路径: {aivk_root.get_module_tmp_path(module_id)}")
            else:
                # 如果没有指定模块，显示所有目录的状态
                aivk_root.update_all_meta
                print(f"AIVK根目录: {aivk_root.aivk_root}")
                
                # 显示模块目录的模块列表
                modules_meta = aivk_root.get_resource_meta_path(ResourceType.MODULES)
                if modules_meta.exists():
                    with open(modules_meta, "r") as f:
                        meta_data = toml.load(f)
                        if "modules" in meta_data:
                            print("\n已安装的模块:")
                            for module_id, status in meta_data["modules"].items():
                                if module_id != "_info":  # 跳过信息字段
                                    print(f"  - {module_id}: {'启用' if status else '禁用'}")
                
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
