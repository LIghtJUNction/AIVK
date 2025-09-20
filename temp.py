from __future__ import annotations
from pathlib import Path
import threading
from typing import Callable, Any, Self, TypeVar, Type, Dict
from pydantic import BaseModel, PrivateAttr
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import json
from logging import getLogger
from watchdog.observers.api import BaseObserver
from contextlib import asynccontextmanager
logger = getLogger("aivk.config")

T = TypeVar('T', bound='AivkConfig')

# 全局共享配置类 - 优雅的单例模式
class GlobalConfig(BaseModel):
    """全局共享配置容器，所有模块配置都保存在这里"""
    modules: Dict[str, Dict[str, Any]] = {}  # 模块ID -> 模块配置
    
    # 类变量：单例实例
    _instance: 'GlobalConfig | None' = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls) -> 'GlobalConfig':
        """获取全局配置单例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def set_module_config(self, module_id: str, config_data: Dict[str, Any]) -> None:
        """设置模块配置"""
        self.modules[module_id] = config_data
    
    def get_module_config(self, module_id: str) -> Dict[str, Any]:
        """获取模块配置"""
        return self.modules.get(module_id, {})

# 监控系统 - 简化的全局状态
_shared_observer: BaseObserver | None = None
_shared_lock = threading.Lock()
_watched_configs: dict[str, 'AivkConfig'] = {}
_watched_files: set[str] = set()

class AivkConfig(BaseModel):
    """
    通用类型安全配置基类，支持 JSON 文件加载、保存、热重载。
    继承后自定义字段即可。
    
    支持两种模式：
    1. 私有配置模式：每个实例独立的配置文件
    2. 共享配置模式：多个模块共享同一个配置文件，通过模块ID进行区分
    """
    _fs: Any = PrivateAttr()
    _file_name: str = PrivateAttr()
    _module_id: str | None = PrivateAttr(default=None)  # 模块ID，用于共享配置模式
    
    # 类变量：全局共享配置实例
    _shared_config_instance: 'AivkConfig | None' = None

    def __init__(self, fs: Any, file_name: str, module_id: str | None = None, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._reload_callbacks: list[Callable[[Any], None]] = []
        # 确保文件名包含扩展名
        if not file_name.endswith('.json'):
            file_name += '.json'
        self._config_path: Path = fs.etc / file_name
        self._fs = fs
        self._file_name = file_name
        self._module_id = module_id

    @classmethod
    def load(cls: Type[T], fs: Any, file_name: str) -> T:
        """从JSON文件加载配置，返回模型实例"""
        # 确保文件名包含扩展名
        if not file_name.endswith('.json'):
            file_name += '.json'
        path: Path = fs.etc / file_name
        if path.exists():
            try:
                with path.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                return cls(fs, file_name, **data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON 文件解析错误 {path}: {e}")
                # 返回默认实例
                return cls(fs, file_name=file_name)
            except Exception as e:
                logger.error(f"加载配置文件失败 {path}: {e}")
                # 对于 Pydantic 验证错误，尝试部分加载有效字段
                try:
                    with path.open('r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 过滤出有效的字段
                    valid_data = {}
                    for key, value in data.items():
                        try:
                            # 直接使用 Pydantic 的字段验证
                            field = cls.model_fields.get(key)
                            if field:
                                # 简单验证类型
                                if key == 'age' and isinstance(value, str):
                                    continue  # 跳过字符串形式的 age
                                valid_data[key] = value
                        except Exception:
                            logger.warning(f"跳过无效字段 {key}={value}")
                    
                    # 使用有效数据创建实例
                    return cls(fs, file_name, **valid_data)
                except Exception:
                    return cls(fs, file_name=file_name)
        else:
            return cls(fs, file_name=file_name)

    def reload(self):
        """重新加载文件的实例方法，安全读取，防止触发watch（不改变mtime/不写入文件）"""
        # 只读模式，不会触发watchdog的on_modified
        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # 只更新模型字段，避免直接操作__dict__带来的副作用
            for k, v in data.items():
                if hasattr(self, k):
                    setattr(self, k, v)
        except Exception as e:
            logger.error(f"配置reload失败: {e}")

    def save(self,  path: Path | None = None) -> None:
        """保存配置到JSON文件"""
        path = path or self._config_path

        with path.open('w', encoding='utf-8') as f:
            json.dump(self.model_dump(), f, ensure_ascii=False, indent=2)

    def onReload(self, func: Callable[[Self], None]):
        """装饰器：注册热重载回调（支持多回调）"""
        self._reload_callbacks.append(func)

    def watch(self, path: Path | None = None) -> BaseObserver:
        """监控配置文件所在目录，使用共享Observer监控多个配置文件。"""
        global _shared_observer, _shared_lock, _watched_configs, _watched_files
        
        real_path: Path = path or self._config_path
        file_path = str(real_path)
        dir_path = str(real_path.parent)
        
        with _shared_lock:
            # 将当前实例注册到共享监控器
            _watched_configs[file_path] = self
            
            # 如果共享监控器不存在，创建它
            if _shared_observer is None:
                _shared_observer = Observer()
                _shared_observer.daemon = True
                _shared_observer.start()
                logger.info("启动共享配置文件监控器")
            
            # 监控文件所在的目录，而不是直接监控文件
            if dir_path not in _watched_files:
                _shared_observer.schedule(
                    AivkConfig._SharedReloader(), 
                    dir_path,  # 监控目录
                    recursive=False
                )
                _watched_files.add(dir_path)
                logger.debug(f"添加目录监控: {dir_path}")
        
        return _shared_observer

    def stop_watch(self) -> None:
        """停止监听当前配置文件，如果没有其他配置在监听则停止共享监控器"""
        global _shared_observer, _shared_lock, _watched_configs, _watched_files
        
        real_path = str(self._config_path)
        
        with _shared_lock:
            # 从共享监控器中移除当前实例
            if real_path in _watched_configs:
                del _watched_configs[real_path]
                logger.debug(f"停止监听配置文件: {real_path}")
            
            # 如果没有配置在监听了，停止共享监控器
            if not _watched_configs and _shared_observer:
                _shared_observer.stop()
                _shared_observer.join()
                _shared_observer = None
                _watched_files.clear()  # 清空已监控目录记录
                logger.info("停止共享配置文件监控器")

    class _SharedReloader(FileSystemEventHandler):
        """共享的文件系统事件处理器，为所有AivkConfig实例提供防抖热重载"""
        def __init__(self):
            self._timers: dict[str, threading.Timer] = {}  # 文件路径 -> 定时器
            self._lock = threading.Lock()
            self._delay = 0.5  # 500ms

        def on_modified(self, event: FileSystemEvent) -> None:
            global _watched_configs
            
            if event.is_directory:
                return
                
            file_path = str(event.src_path)
            
            # 检查是否是我们监控的配置文件
            config = _watched_configs.get(file_path)
            if not config:
                return
                
            with self._lock:
                # 取消之前的定时器
                if file_path in self._timers:
                    self._timers[file_path].cancel()
                
                def trigger():
                    try:
                        config.reload()  # 先 reload，确保内容为最新
                        if config._reload_callbacks:
                            for cb in config._reload_callbacks:
                                cb(config)
                        else:
                            logger.warning(f"配置文件 {file_path} 被修改，但没有注册热重载回调!")
                    except Exception as e:
                        logger.error(f"热重载回调异常: {e}")
                    finally:
                        # 清理完成的定时器
                        with self._lock:
                            if file_path in self._timers:
                                del self._timers[file_path]
                
                timer = threading.Timer(self._delay, trigger)
                timer.daemon = True
                self._timers[file_path] = timer
                timer.start()

    @asynccontextmanager
    async def open(self):
        """
        异步上下文管理器：进入时自动加载，退出时自动保存并清理资源。
        """
        try:
            # 可选：根据需要重新加载配置
            yield self
        finally:
            if hasattr(self, "save_async"):
                self.save()
            else:
                self.save()
            if hasattr(self, "stop_watch"):
                self.stop_watch()

    def __enter__(self):
        """同步上下文管理器，进入时返回自身"""
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any) -> None:
        """同步上下文管理器，退出时自动停止监听并保存"""
        self.stop_watch()
        self.save(self._config_path)
