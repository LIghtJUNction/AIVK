from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager
import os
from pathlib import Path
import runpy
import subprocess
import sys
import threading

from logging import getLogger
logger = getLogger("aivk.fs")
class AivkFSMeta(type):
    @property
    def env(cls) -> dict[str, str]:
        """
        获取当前环境变量
        """
        return {k: v for k, v in os.environ.items() if k.startswith("AIVK_")}

class AivkFS(metaclass=AivkFSMeta):
    root = Path(os.getenv("AIVK_ROOT", Path().home() / ".aivk"))
    fs: dict[str, AivkFS] = {}
    _venv_activated = False

    def __init__(self, id: str):
        self.id = id
        self.fs[id] = self

    def __repr__(self) -> str:
        info = f"\n\
home: {self.home}\n\
data: {self.data}\n\
etc: {self.etc}\n\
cache: {self.cache}\n\
tmp: {self.tmp}\n\
venv: {self.venv}\n\
root: {self.root}\n\
cwd: {Path.cwd()}\n\
"
        return f"\nAivkFS({self.id}):\n\
{info}"

    @classmethod
    def getFS(cls, id: str) -> AivkFS:
        if id not in cls.fs:
            cls(id)
        return cls.fs[id]

    @property
    def home(self) -> Path:
        return self.root  if self.id == "aivk" else self.root / "home" / self.id
    
    @property
    def data(self) -> Path:
        return self.home / "data"

    @property
    def etc(self) -> Path:
        return self.home / "etc"

    @property
    def cache(self) -> Path:
        return self.home / "cache"

    @property
    def tmp(self) -> Path:
        return self.home / "tmp"

    @property
    def venv(self) -> Path:
        return self.home / ".venv"
    
    @classmethod
    @asynccontextmanager
    async def ctx(cls, clear: bool = False):
        """
        仅允许全局进入一次
        """
        async with asyncio.Lock():
            with threading.Lock():
                logger.info("aivk 文件系统初始化")
                id = "aivk"
                fs = cls.getFS(id)
                cwd = Path.cwd()
                old_sys_path = sys.path.copy()
                old_environ = os.environ.copy()
    
                os.chdir(fs.home)
                activate_this = fs.venv / ("Scripts" if os.name == "nt" else "bin") / "activate_this.py"
                
                if not fs.venv.exists():
                    try:
                        # 只允许第一个进入的线程/协程激活虚拟环境
                        python_exe = sys.executable
                        subprocess.run(
                            ["uv", "venv", "-p", python_exe, str(fs.venv)],
                            check=True
                        )
                    except Exception as e:
                        logger.error(f"激活虚拟环境失败: {e}")
                        subprocess.run(
                            ["python", "-m", "venv", str(fs.venv)],
                            check=True
                        )

                if not cls._venv_activated:
                    if activate_this.exists():
                        runpy.run_path(str(activate_this))
                    cls._venv_activated = True

                logger.info("aivk 文件系统已初始化")
                try:
                    yield fs
                finally:
                    os.chdir(cwd)
                    sys.path[:] = old_sys_path
                    os.environ.clear()
                    os.environ.update(old_environ)
                    cls._venv_activated = False
