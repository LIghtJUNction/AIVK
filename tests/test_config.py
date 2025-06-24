import json
import threading
from pathlib import Path
from unittest.mock import MagicMock
import pytest
from src.aivk.base.config import AivkConfig
from typing import Type, Any, Optional

class MyConfig(AivkConfig):
    foo: int = 1
    bar: str = "baz"

def make_fs(tmp_path: Path) -> Any:
    fs = MagicMock()
    fs.etc = tmp_path
    return fs

def make_config(cls: Type[AivkConfig], fs: Any, file_name: str, **kwargs: Any) -> Any:
    obj = cls.__new__(cls)
    obj.__init__(fs, file_name, **kwargs)
    return obj

def test_config_load_and_save(tmp_path: Path):
    fs = make_fs(tmp_path)
    file_name = "test_config.json"
    cfg = make_config(MyConfig, fs, file_name, foo=42, bar="hello")
    cfg.save()
    file_path = tmp_path / file_name
    assert file_path.exists()
    with open(str(file_path), encoding="utf-8") as f:
        data = json.load(f)
    assert data["foo"] == 42
    assert data["bar"] == "hello"
    loaded = MyConfig.load(fs, file_name)
    assert loaded.foo == 42
    assert loaded.bar == "hello"

def test_config_on_reload_callback(tmp_path: Path):
    fs = make_fs(tmp_path)
    file_name = "test_reload.json"
    cfg = make_config(MyConfig, fs, file_name)
    called = threading.Event()
    @cfg.onReload
    def cb(conf: AivkConfig):
        called.set()
    for cb in cfg._reload_callbacks:
        cb(cfg)
    assert called.is_set()

def test_config_watch_and_stop(tmp_path: Path):
    fs = make_fs(tmp_path)
    file_name = "test_watch.json"
    cfg = make_config(MyConfig, fs, file_name)
    observer = cfg.watch()
    assert observer.is_alive()
    cfg.stop_watch()
    assert cfg._observer is None

def test_context_manager(tmp_path: Path):
    fs = make_fs(tmp_path)
    file_name = "test_ctx.json"
    cfg = make_config(MyConfig, fs, file_name, foo=99)
    with cfg as c:
        c.foo = 100
    with open(str(tmp_path / file_name), encoding="utf-8") as f:
        data = json.load(f)
    assert data["foo"] == 100

class AsyncAivkConfigWrapper:
    def __init__(self, cfg: Any):
        self.cfg = cfg
    async def __aenter__(self) -> Any:
        return self.cfg
    async def __aexit__(self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Any) -> None:
        await self.cfg.__aexit__(exc_type, exc_val, exc_tb)  # type: ignore

@pytest.mark.asyncio
async def test_async_context_manager(tmp_path: Path):
    fs = make_fs(tmp_path)
    file_name = "test_async_ctx.json"
    cfg = make_config(MyConfig, fs, file_name, foo=123)
    async with AsyncAivkConfigWrapper(cfg) as c:
        c.foo = 456
    with open(str(tmp_path / file_name), encoding="utf-8") as f:
        data = json.load(f)
    assert data["foo"] == 456
