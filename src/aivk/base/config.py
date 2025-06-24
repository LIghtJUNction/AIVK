from __future__ import annotations
from pathlib import Path
import threading
from typing import Callable, Any, Self, TypeVar, Type
from pydantic import BaseModel, PrivateAttr
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import json
import os
from logging import getLogger
from watchdog.observers.api import BaseObserver
from contextlib import asynccontextmanager
logger = getLogger("aivk.config")

T = TypeVar('T', bound='AivkConfig')

class AivkConfig(BaseModel):
    """
    通用类型安全配置基类，支持 JSON 文件加载、保存、热重载。
    继承后自定义字段即可。
    """
    _lock: threading.Lock = PrivateAttr(default_factory=threading.Lock)
    _fs: Any = PrivateAttr()
    _file_name: str = PrivateAttr()

    def __init__(self, fs: Any, file_name: str, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._observer: BaseObserver | None = None
        self._reload_callbacks: list[Callable[[Any], None]] = []
        self._config_path: Path = fs.etc / file_name
        self._fs = fs
        self._file_name = file_name

    @classmethod
    def load(cls: Type[T], fs: Any, file_name: str) -> T:
        """从JSON文件加载配置，返回模型实例"""
        path: Path = fs.etc / file_name
        if path.exists():
            with path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            return cls(fs, file_name, **data)
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
        """监听配置文件变更，自动热重载，变更信号来时延迟0.5秒后reload，期间多次变更只触发一次（标准防抖写法）。"""
        import threading

        real_path: Path | str = path or self._config_path
        _config = self
        class _Reloader(FileSystemEventHandler):
            def __init__(self):
                self._timer = None
                self._lock = threading.Lock()
                self._delay = 0.5  # 500ms
            def on_modified(self, event: FileSystemEvent) -> None:
                if str(event.src_path).endswith(str(real_path)):
                    with self._lock:
                        if self._timer:
                            self._timer.cancel()
                        def trigger():
                            try:
                                _config.reload()  # 先 reload，确保内容为最新
                                if _config._reload_callbacks:
                                    for cb in _config._reload_callbacks:
                                        cb(_config)
                                else:
                                    logger.warning(f"配置文件 {real_path} 被修改，但没有注册热重载回调!")
                            except Exception as e:
                                logger.error(f"热重载回调异常: {e}")
                        self._timer = threading.Timer(self._delay, trigger)
                        self._timer.daemon = True
                        self._timer.start()
        observer: BaseObserver = Observer()
        observer.schedule(_Reloader(), os.path.dirname(real_path) or '.', recursive=False)
        observer.daemon = True
        observer.start()
        self._observer = observer
        return observer

    def stop_watch(self) -> None:
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None


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
