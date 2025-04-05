import abc
from pathlib import Path
import logging
import asyncio
import inspect
import os
import sys
from enum import Enum
from typing import Dict, ClassVar, Optional, Any

logger = logging.getLogger("aivk.core.base.models")
logger.setLevel(logging.INFO)

class ModuleState(Enum):
    """模块状态枚举类"""
    UNLOADED = 0      # 未加载
    LOADING = 1       # 正在加载
    LOADED = 2        # 已加载
    UNLOADING = 3     # 正在卸载
    INSTALLING = 4    # 正在安装
    UNINSTALLING = 5  # 正在卸载
    UPDATING = 6      # 正在更新
    ERROR = 7         # 错误状态

class LKM(abc.ABC):
    """
    Base class for all LKM models.
    loadable aivk module.
    """
    # 类级变量，用于跟踪所有模块的状态
    _module_states: ClassVar[Dict[str, ModuleState]] = {}
    _module_locks: ClassVar[Dict[str, asyncio.Lock]] = {}
    
    # 缓存模块元数据和配置
    _meta_cache: ClassVar[Dict[str, Dict[str, Any]]] = {}
    _config_cache: ClassVar[Dict[str, Dict[str, Any]]] = {}
    
    @classmethod
    def get_module_id(cls) -> str:
        """
        获取模块ID
        
        模块ID优先从入口文件名获取，若失败则从同级目录下的meta.toml的id字段获取
        
        获取逻辑优先级：
        1. 从入口文件名获取（不含扩展名）
        2. 如果文件名是__init__，则使用目录名
        3. 尝试读取同级目录下的meta.toml中的id字段
        4. 最后才采用类名小写（最不推荐）
        """
        try:
            # 1. 尝试获取类定义所在的文件路径
            module_file = inspect.getfile(cls)
            # 提取文件名
            module_file_name = os.path.basename(module_file)
            # 去除扩展名
            module_id = os.path.splitext(module_file_name)[0]
            
            # 2. 如果文件名是 __init__，则使用目录名
            if module_id == "__init__":
                # 获取目录路径
                dir_path = os.path.dirname(module_file)
                # 提取目录名
                module_id = os.path.basename(dir_path)
            
            logger.debug(f"从文件名 {module_file_name} 获取模块ID: {module_id}")
            return module_id
            
        except (TypeError, ValueError) as e:
            logger.warning(f"无法从文件路径获取模块ID: {e}，尝试从meta.toml获取")
            
            try:
                # 3. 尝试读取meta.toml文件
                # 如果可以获取到文件路径
                if 'module_file' in locals():
                    # 获取模块所在目录
                    module_dir = os.path.dirname(module_file)
                    # meta.toml路径
                    meta_file = os.path.join(module_dir, "meta.toml")
                else:
                    # 如果没有文件路径，尝试获取当前工作目录
                    current_module = sys.modules.get(cls.__module__)
                    if current_module and hasattr(current_module, '__file__'):
                        module_dir = os.path.dirname(current_module.__file__)
                        meta_file = os.path.join(module_dir, "meta.toml")
                    else:
                        # 最后尝试当前工作目录
                        module_dir = os.getcwd()
                        meta_file = os.path.join(module_dir, "meta.toml")
                
                # 检查meta.toml文件是否存在
                if os.path.exists(meta_file):
                    # 读取meta.toml文件
                    try:
                        import toml
                        with open(meta_file, 'r', encoding='utf-8') as f:
                            meta_data = toml.load(f)
                            
                        # 从meta.toml中获取id字段
                        if 'id' in meta_data:
                            module_id = meta_data['id']
                            logger.info(f"从meta.toml文件获取模块ID: {module_id}")
                            return module_id
                        else:
                            logger.warning("meta.toml文件中未找到id字段")
                    except Exception as e:
                        logger.warning(f"读取meta.toml文件失败: {e}")
                else:
                    logger.warning(f"未找到meta.toml文件: {meta_file}")
            
            except Exception as e:
                logger.warning(f"尝试读取meta.toml失败: {e}")
            
            # 4. 最后才采用类名小写（最不推荐）
            fallback_id = cls.__name__.lower()
            logger.warning(f"无法获取模块ID，使用类名作为最后的备选: {fallback_id}")
            return fallback_id
    
    @classmethod
    def get_module_dir(cls) -> Optional[str]:
        """
        获取模块所在目录的路径
        
        返回:
            模块所在目录的绝对路径，如果无法获取则返回None
        """
        try:
            # 尝试获取类定义所在的文件路径
            module_file = inspect.getfile(cls)
            # 获取模块所在目录
            module_dir = os.path.dirname(os.path.abspath(module_file))
            return module_dir
        except (TypeError, ValueError) as e:
            logger.warning(f"无法获取模块所在目录: {e}")
            
            # 尝试从模块对象获取
            current_module = sys.modules.get(cls.__module__)
            if current_module and hasattr(current_module, '__file__'):
                module_dir = os.path.dirname(os.path.abspath(current_module.__file__))
                return module_dir
            
            logger.error("无法获取模块所在目录")
            return None

    @classmethod
    def get_meta_path(cls) -> Optional[Path]:
        """
        获取模块的meta.toml文件路径
        
        返回:
            meta.toml文件的Path对象，如果无法获取则返回None
        """
        module_dir = cls.get_module_dir()
        if (module_dir):
            return Path(module_dir) / "meta.toml"
        return None
    
    @classmethod
    def get_config_path(cls) -> Optional[Path]:
        """
        获取模块的config.toml文件路径
        
        返回:
            config.toml文件的Path对象，如果无法获取则返回None
        """
        module_dir = cls.get_module_dir()
        if (module_dir):
            return Path(module_dir) / "config.toml"
        return None
    
    @classmethod
    def get_meta(cls) -> Dict[str, Any]:
        """
        获取模块的meta.toml文件内容
        
        返回:
            meta.toml文件的内容，如果无法读取则返回空字典
        """
        module_id = cls.get_module_id()
        
        # 如果缓存中已有数据，直接返回
        if module_id in cls._meta_cache:
            return cls._meta_cache[module_id]
        
        meta_path = cls.get_meta_path()
        if meta_path and meta_path.exists():
            try:
                import toml
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta_data = toml.load(f)
                
                # 缓存数据
                cls._meta_cache[module_id] = meta_data
                return meta_data
            except Exception as e:
                logger.error(f"读取meta.toml文件失败: {e}")
        else:
            logger.warning(f"meta.toml文件不存在: {meta_path}")
        
        # 返回空字典
        cls._meta_cache[module_id] = {}
        return {}
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """
        获取模块的config.toml文件内容
        
        返回:
            config.toml文件的内容，如果无法读取则返回空字典
        """
        module_id = cls.get_module_id()
        
        # 如果缓存中已有数据，直接返回
        if module_id in cls._config_cache:
            return cls._config_cache[module_id]
        
        config_path = cls.get_config_path()
        if config_path and config_path.exists():
            try:
                import toml
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = toml.load(f)
                
                # 缓存数据
                cls._config_cache[module_id] = config_data
                return config_data
            except Exception as e:
                logger.error(f"读取config.toml文件失败: {e}")
        else:
            logger.warning(f"config.toml文件不存在: {config_path}")
        
        # 返回空字典
        cls._config_cache[module_id] = {}
        return {}
    
    # 为了兼容性，提供属性方式访问
    # 注意：这些属性只能在实例上使用，不能在类上使用
    @property
    def meta_path(self) -> Optional[Path]:
        """获取模块的meta.toml文件路径(实例方法)"""
        return self.__class__.get_meta_path()
    
    @property
    def config_path(self) -> Optional[Path]:
        """获取模块的config.toml文件路径(实例方法)"""
        return self.__class__.get_config_path()
    
    @property
    def meta(self) -> Dict[str, Any]:
        """获取模块的meta.toml文件内容(实例方法)"""
        return self.__class__.get_meta()
    
    @property
    def config(self) -> Dict[str, Any]:
        """获取模块的config.toml文件内容(实例方法)"""
        return self.__class__.get_config()
    
    @classmethod
    def reload_meta(cls) -> Dict[str, Any]:
        """
        重新加载模块的meta.toml文件内容
        
        返回:
            meta.toml文件的最新内容，如果无法读取则返回空字典
        """
        module_id = cls.get_module_id()
        
        # 清除缓存
        if module_id in cls._meta_cache:
            del cls._meta_cache[module_id]
        
        # 重新加载
        return cls.get_meta()
    
    @classmethod
    def reload_config(cls) -> Dict[str, Any]:
        """
        重新加载模块的config.toml文件内容
        
        返回:
            config.toml文件的最新内容，如果无法读取则返回空字典
        """
        module_id = cls.get_module_id()
        
        # 清除缓存
        if module_id in cls._config_cache:
            del cls._config_cache[module_id]
        
        # 重新加载
        return cls.get_config()
    
    @classmethod
    def save_config(cls, config_data: Dict[str, Any]) -> bool:
        """
        保存配置到config.toml文件
        
        参数:
            config_data: 要保存的配置数据
            
        返回:
            保存成功返回True，否则返回False
        """
        module_id = cls.get_module_id()
        config_path = cls.get_config_path()
        
        if not config_path:
            logger.error("无法获取config.toml文件路径")
            return False
        
        try:
            import toml
            with open(config_path, 'w', encoding='utf-8') as f:
                toml.dump(config_data, f)
            
            # 更新缓存
            cls._config_cache[module_id] = config_data
            logger.info(f"保存config.toml文件成功: {config_path}")
            return True
        except Exception as e:
            logger.error(f"保存config.toml文件失败: {e}")
            return False
    
    @classmethod
    async def onLoad(cls, *args, **kwargs):
        """
        加载模块，添加锁机制确保只能调用一次
        """
        module_id = cls.get_module_id()
        
        # 初始化模块锁和状态（如果不存在）
        if module_id not in cls._module_locks:
            cls._module_locks[module_id] = asyncio.Lock()
        
        if module_id not in cls._module_states:
            cls._module_states[module_id] = ModuleState.UNLOADED
        
        # 获取锁
        async with cls._module_locks[module_id]:
            # 检查当前状态
            current_state = cls._module_states.get(module_id)
            
            if current_state == ModuleState.LOADED:
                logger.warning(f"模块 {module_id} 已经加载，不能重复加载")
                return False
            
            if current_state == ModuleState.LOADING:
                logger.warning(f"模块 {module_id} 正在加载中")
                return False
                
            if current_state in [ModuleState.UNLOADING, ModuleState.INSTALLING, 
                               ModuleState.UNINSTALLING, ModuleState.UPDATING]:
                logger.warning(f"模块 {module_id} 正在执行 {current_state.name} 操作，不能加载")
                return False
            
            # 更新状态为加载中
            cls._module_states[module_id] = ModuleState.LOADING
            logger.info(f"模块 {module_id} 开始加载")
            
            try:
                # 调用实际的加载逻辑
                await cls._onLoad(*args, **kwargs)
                # 更新状态为已加载
                cls._module_states[module_id] = ModuleState.LOADED
                logger.info(f"模块 {module_id} 加载成功")
                return True
            except Exception as e:
                # 加载失败，设置为错误状态
                cls._module_states[module_id] = ModuleState.ERROR
                logger.error(f"模块 {module_id} 加载失败: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return False
    
    @classmethod
    async def onUnload(cls, *args, **kwargs):
        """
        卸载模块，添加锁机制确保状态转换正确
        """
        module_id = cls.get_module_id()
        
        # 初始化模块锁和状态（如果不存在）
        if module_id not in cls._module_locks:
            cls._module_locks[module_id] = asyncio.Lock()
        
        if module_id not in cls._module_states:
            cls._module_states[module_id] = ModuleState.UNLOADED
        
        # 获取锁
        async with cls._module_locks[module_id]:
            # 检查当前状态
            current_state = cls._module_states.get(module_id)
            
            if current_state == ModuleState.UNLOADED:
                logger.warning(f"模块 {module_id} 未加载，无需卸载")
                return False
            
            if current_state == ModuleState.UNLOADING:
                logger.warning(f"模块 {module_id} 正在卸载中")
                return False
                
            if current_state in [ModuleState.LOADING, ModuleState.INSTALLING, 
                               ModuleState.UNINSTALLING, ModuleState.UPDATING]:
                logger.warning(f"模块 {module_id} 正在执行 {current_state.name} 操作，不能卸载")
                return False
            
            # 更新状态为卸载中
            cls._module_states[module_id] = ModuleState.UNLOADING
            logger.info(f"模块 {module_id} 开始卸载")
            
            try:
                # 调用实际的卸载逻辑
                await cls._onUnload(*args, **kwargs)
                # 更新状态为未加载
                cls._module_states[module_id] = ModuleState.UNLOADED
                logger.info(f"模块 {module_id} 卸载成功")
                return True
            except Exception as e:
                # 卸载失败，设置为错误状态
                cls._module_states[module_id] = ModuleState.ERROR
                logger.error(f"模块 {module_id} 卸载失败: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return False
    
    @classmethod
    async def onInstall(cls, *args, **kwargs):
        """
        安装模块，添加锁机制确保状态转换正确
        """
        module_id = cls.get_module_id()
        
        # 初始化模块锁和状态（如果不存在）
        if module_id not in cls._module_locks:
            cls._module_locks[module_id] = asyncio.Lock()
        
        if module_id not in cls._module_states:
            cls._module_states[module_id] = ModuleState.UNLOADED
        
        # 获取锁
        async with cls._module_locks[module_id]:
            # 检查当前状态
            current_state = cls._module_states.get(module_id)
            
            if current_state != ModuleState.UNLOADED:
                logger.warning(f"模块 {module_id} 必须处于未加载状态才能安装，当前状态: {current_state.name}")
                return False
            
            # 更新状态为安装中
            cls._module_states[module_id] = ModuleState.INSTALLING
            logger.info(f"模块 {module_id} 开始安装")
            
            try:
                # 调用实际的安装逻辑
                await cls._onInstall(*args, **kwargs)
                # 安装完成后状态保持为未加载
                cls._module_states[module_id] = ModuleState.UNLOADED
                logger.info(f"模块 {module_id} 安装成功")
                return True
            except Exception as e:
                # 安装失败，设置为错误状态
                cls._module_states[module_id] = ModuleState.ERROR
                logger.error(f"模块 {module_id} 安装失败: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return False
    
    @classmethod
    async def onUninstall(cls, *args, **kwargs):
        """
        卸载安装模块，添加锁机制确保状态转换正确
        
        注意：本方法只在处理完成后返回布尔值表示成功或失败
        但不会将这个布尔值传递给内部方法_onUninstall
        """
        module_id = cls.get_module_id()
        
        # 初始化模块锁和状态（如果不存在）
        if module_id not in cls._module_locks:
            cls._module_locks[module_id] = asyncio.Lock()
        
        if module_id not in cls._module_states:
            cls._module_states[module_id] = ModuleState.UNLOADED
        
        # 获取锁
        async with cls._module_locks[module_id]:
            # 检查当前状态
            current_state = cls._module_states.get(module_id)
            
            if current_state == ModuleState.LOADED:
                logger.warning(f"模块 {module_id} 必须先卸载才能卸载安装")
                return False
            
            # 更新状态为卸载安装中
            cls._module_states[module_id] = ModuleState.UNINSTALLING
            logger.info(f"模块 {module_id} 开始卸载安装")
            
            try:
                # 保存原始参数，确保不传递布尔返回值
                original_args = args
                original_kwargs = kwargs.copy()
                
                # 调用实际的卸载安装逻辑，使用原始参数
                await cls._onUninstall(*original_args, **original_kwargs)
                
                # 卸载安装完成后状态保持为未加载
                cls._module_states[module_id] = ModuleState.UNLOADED
                logger.info(f"模块 {module_id} 卸载安装成功")
                return True
            except Exception as e:
                # 卸载安装失败，设置为错误状态
                cls._module_states[module_id] = ModuleState.ERROR
                logger.error(f"模块 {module_id} 卸载安装失败: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return False
    
    @classmethod
    async def onUpdate(cls, *args, **kwargs):
        """
        更新模块，添加锁机制确保状态转换正确
        """
        module_id = cls.get_module_id()
        
        # 初始化模块锁和状态（如果不存在）
        if module_id not in cls._module_locks:
            cls._module_locks[module_id] = asyncio.Lock()
        
        if module_id not in cls._module_states:
            cls._module_states[module_id] = ModuleState.UNLOADED
        
        # 获取锁
        async with cls._module_locks[module_id]:
            # 检查当前状态
            current_state = cls._module_states.get(module_id)
            
            if current_state == ModuleState.LOADED:
                logger.warning(f"模块 {module_id} 必须先卸载才能更新")
                return False
            
            # 更新状态为更新中
            cls._module_states[module_id] = ModuleState.UPDATING
            logger.info(f"模块 {module_id} 开始更新")
            
            try:
                # 调用实际的更新逻辑
                await cls._onUpdate(*args, **kwargs)
                # 更新完成后状态保持为未加载
                cls._module_states[module_id] = ModuleState.UNLOADED
                logger.info(f"模块 {module_id} 更新成功")
                return True
            except Exception as e:
                # 更新失败，设置为错误状态
                cls._module_states[module_id] = ModuleState.ERROR
                logger.error(f"模块 {module_id} 更新失败: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return False
    
    # 改名原始方法为内部方法，但保持抽象方法
    @classmethod
    @abc.abstractmethod
    async def _onLoad(cls, *args, **kwargs):
        """
        实际加载模块的逻辑（内部方法）
        """
        pass

    @classmethod
    @abc.abstractmethod
    async def _onUnload(cls, *args, **kwargs):
        """
        实际卸载模块的逻辑（内部方法）
        """
        pass

    @classmethod
    @abc.abstractmethod
    async def _onInstall(cls, *args, **kwargs):
        """
        实际安装模块的逻辑（内部方法）
        """
        pass

    @classmethod
    @abc.abstractmethod
    async def _onUninstall(cls, *args, **kwargs):
        """
        实际卸载安装模块的逻辑（内部方法）
        """
        pass
    
    @classmethod
    @abc.abstractmethod
    async def _onUpdate(cls, *args, **kwargs):
        """
        实际更新模块的逻辑（内部方法）
        """
        pass
