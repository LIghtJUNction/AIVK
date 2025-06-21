# -*- coding: utf-8 -*-
"""
AIVK 虚拟环境上下文管理器
"""
import asyncio
import os
import sys
import subprocess
from contextlib import asynccontextmanager
from pathlib import Path
from types import TracebackType
from typing import Any
from .fs import AivkFS
from logging import getLogger

logger = getLogger("aivk.base.context")
class AsyncRLock:
    def __init__(self):
        self._lock = asyncio.Lock()
        self._owner = None
        self._count = 0

    async def acquire(self):
        current = asyncio.current_task()
        if self._owner == current:
            self._count += 1
            return True
        await self._lock.acquire()
        self._owner = current
        self._count = 1
        return True

    def release(self):
        current = asyncio.current_task()
        if self._owner != current:
            raise RuntimeError("Cannot release a lock that's not owned")
        self._count -= 1
        if self._count == 0:
            self._owner = None
            self._lock.release()

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self,
                        exc_type: type[BaseException] | None,
                        exc: BaseException | None,
                        tb: TracebackType | None):
        self.release()

# Aivk 虚拟环境上下文
class AivkContext:
    """
    AIVK 虚拟环境上下文
    """    
    def __init__(self):
        """初始化上下文"""
        self.current_fs = None
        self.active_venvs: dict[str, dict[str, Any]] = {}  # 跟踪激活的虚拟环境
        self._venv_lock = AsyncRLock()  # 新增锁 

    async def _create_venv(self, venv_path: Path, python_version: str | None = None, force: bool = False) -> bool:
        """创建虚拟环境（使用 uv）"""
        if venv_path.exists():
            if force:
                import shutil
                shutil.rmtree(venv_path)
                logger.info(f"已删除旧虚拟环境: {venv_path}")
            else:
                logger.info(f"虚拟环境已存在: {venv_path}")
                return True

        try:
            cmd = ["uv", "venv", str(venv_path)]
            if python_version:
                cmd.extend(["--python", python_version])

            subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"虚拟环境创建成功 (uv): {venv_path}")
            return True
        except FileNotFoundError as e:
            logger.error(f"未找到 uv 命令: {e}")
        except subprocess.CalledProcessError as e:
            logger.error(f"创建虚拟环境失败: {e}, 本项目依赖于uv管理虚拟环境（速度快且节约空间）")
        return False
    
    async def _activate_venv(self, venv_path: Path, env_id: str) -> dict[str, str | list[str]]:
        """激活虚拟环境，返回原始环境状态"""
        # 保存原始环境状态
        original_state = {
            'PATH': os.environ.get('PATH', ''),
            'PYTHONPATH': os.environ.get('PYTHONPATH', ''),
            'VIRTUAL_ENV': os.environ.get('VIRTUAL_ENV', ''),
            'sys_path': sys.path.copy()
        }        # 设置虚拟环境路径
        if os.name == 'nt':  # Windows
            scripts_path = venv_path / "Scripts"
            python_exe = scripts_path / "python.exe"
            pip_exe = scripts_path / "pip.exe"
            site_packages = venv_path / "Lib" / "site-packages"
        else:  # macOS/Linux
            scripts_path = venv_path / "bin"
            python_exe = scripts_path / "python"
            pip_exe = scripts_path / "pip"
            site_packages = venv_path / "lib" / "python3.*/site-packages"
        
        # 更新环境变量
        os.environ['PATH'] = str(scripts_path) + os.pathsep + os.environ['PATH']
        os.environ['VIRTUAL_ENV'] = str(venv_path)
        
        # 更新 sys.path (Windows 和 Linux 的 site-packages 路径不同)
        if os.name == 'nt':
            if site_packages.exists() and str(site_packages) not in sys.path:
                sys.path.insert(0, str(site_packages))
        else:
            # Linux/macOS 需要找到实际的 python 版本目录
            lib_path = venv_path / "lib"
            if lib_path.exists():
                for python_dir in lib_path.glob("python*"):
                    if python_dir.is_dir():
                        site_pkg_path = python_dir / "site-packages"
                        if site_pkg_path.exists() and str(site_pkg_path) not in sys.path:
                            sys.path.insert(0, str(site_pkg_path))
                            break        

        self.active_venvs[env_id] = {
            'path': venv_path,
            'python': python_exe,
            'pip': pip_exe,
            'original_state': original_state
        }
        
        logger.debug(f"进入虚拟环境: {venv_path}")
        return original_state
    
    async def _deactivate_venv(self, env_id: str):
        """停用虚拟环境"""
        if env_id not in self.active_venvs:
            return
            
        venv_info = self.active_venvs[env_id]
        original_state = venv_info['original_state']
        
        # 恢复环境变量
        os.environ['PATH'] = original_state['PATH']
        if original_state['PYTHONPATH']:
            os.environ['PYTHONPATH'] = original_state['PYTHONPATH']
        else:
            os.environ.pop('PYTHONPATH', None)
            
        if original_state['VIRTUAL_ENV']:
            os.environ['VIRTUAL_ENV'] = original_state['VIRTUAL_ENV']
        else:
            os.environ.pop('VIRTUAL_ENV', None)
        
        # 恢复 sys.path
        sys.path[:] = original_state['sys_path']
        
        del self.active_venvs[env_id]
        logger.debug(f"离开虚拟环境: {venv_info['path']}")    
    
    @asynccontextmanager
    async def env(self, id: str = "aivk", create_venv: bool = True, venv_name: str | None = None):
        async with self._venv_lock:
            # 1. 确保home目录结构正确
            fs = AivkFS.getFS(id)
            fs.home.mkdir(parents=True, exist_ok=True)
            fs.data.mkdir(parents=True, exist_ok=True)
            fs.cache.mkdir(parents=True, exist_ok=True)
            fs.tmp.mkdir(parents=True, exist_ok=True)
            fs.etc.mkdir(parents=True, exist_ok=True)

            # 2. 保存当前环境状态
            previous_fs = self.current_fs
            self.current_fs = fs
            venv_activated = False
            venv_name = venv_name or f"{id}_venv"
            venv_path = fs.home / venv_name
            previous_cwd = os.getcwd()

            # 3. 创建或激活虚拟环境
            if create_venv:
                venv_path.parent.mkdir(parents=True, exist_ok=True)
                if await self._create_venv(venv_path,"3.13"):
                    await self._activate_venv(venv_path, id)
                    venv_activated = True
            else:
                if venv_path.exists():
                    await self._activate_venv(venv_path, id)
                    venv_activated = True
                    logger.debug(f"激活已存在的虚拟环境: {venv_path}")
                else:
                    logger.warning(f"虚拟环境不存在: {venv_path}，将在不激活虚拟环境的情况下继续")

            try:
                # 4. 切换工作目录
                logger.debug(f"进入 AIVK 环境: {id}")
                os.chdir(str(fs.home))
                logger.debug(f"当前工作目录已更改为: {fs.home}")
                if venv_activated:
                    logger.debug(f"虚拟环境已激活: {venv_path}")
                fs.env = dict(os.environ)
                yield fs
            finally:
                # 5. 恢复环境
                logger.debug(f"退出 AIVK 环境: {id}")
                if venv_activated:
                    await self._deactivate_venv(id)
                os.chdir(previous_cwd)
                logger.debug(f"工作目录已恢复为: {previous_cwd}")
                self.current_fs = previous_fs
                
    @classmethod
    def getContext(cls):
        """
        获取 AIVK 上下文实例
        
        :return: AivkContext 实例
        """
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
            logger.info("AIVK 上下文已初始化")
        return cls._instance

__all__ = ["AivkContext"]