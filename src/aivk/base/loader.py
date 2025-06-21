# -*- coding: utf-8 -*-
import importlib
import json
from logging import getLogger
from pathlib import Path
import re
import sys
from types import ModuleType
from .fs import AivkFS
from box import Box
logger = getLogger("aivk.base.loader")

class AivkLoader:
    """
    AIVK 加载器
    """
    if (AivkFS.aivk_cache / "aivk_box.toml").exists():
        aivk_box: Box = Box.from_toml(filename = AivkFS.aivk_cache / "aivk_box.toml")  # type: ignore
    else:
        aivk_box: Box = Box({"aivk": {"status": "running"}})
    @classmethod
    def getLoader(cls):
        """获取 AIVK 加载器全局单例"""
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    async def ls(self, fs: AivkFS) -> list[dict[str,str]]:
        """列出所有可用的 AIVK 模块"""
        stdout, _ = await fs.aexec("uv", "pip", "list", "--format", "json")
       
        try:
            pkgs_dict = json.loads(stdout.decode())
            pattern = re.compile(r"^aivk[-_]", re.IGNORECASE)
            aivk_modules = [
                pkg for pkg in pkgs_dict if pattern.match(pkg['name'])
            ]
            logger.debug(f"可用的 AIVK 模块: {aivk_modules}")
            return aivk_modules
        except json.JSONDecodeError as e:
            logger.error(f"解析 AIVK 模块列表时发生错误: {e}, stderr: {_}")
            return [{"name": "aivk"}]

    async def find(self, fs: AivkFS, id: str , aivk_modules : list[dict[str, str]]) -> list[ModuleType] | None:
        """查找指定的 AIVK 模块 导入后返回模块实例 """
        loaded_modules: list[ModuleType] = list()
        # 属性缓存 _id_list，避免重复计算
        if not hasattr(self, '_id_list_cache') or self._id_list_cache_src is not aivk_modules:
            self._id_list_cache = [mod["name"] for mod in aivk_modules]
            self._id_list_cache_src = aivk_modules
        _id_list = self._id_list_cache

        match id:
            case "aivk":
                import aivk
                loaded_modules.append(aivk)
                return loaded_modules
            case "*":
                # 匹配所有 AIVK 模块
                for mod in aivk_modules:
                    
                    try:
                        if "editable_project_location" in mod:
                            editable_path = mod["editable_project_location"]
                            if editable_path not in sys.path:
                                src_path = Path(editable_path) / "src"
                                if src_path.is_dir():
                                    path_to_add = str(src_path)
                                else:
                                    path_to_add = str(Path(editable_path))
                                if path_to_add not in sys.path:
                                    sys.path.insert(0, path_to_add)

                        result = importlib.import_module(mod["name"].replace("-", "_"))
                        loaded_modules.append(result)
                    except ImportError as e:
                        logger.error(f"导入模块 {mod} 时发生错误: {e}")
                return loaded_modules

            case _:
                if id in _id_list:
                    result = importlib.import_module(id.replace("-", "_"))
                    loaded_modules.append(result)
                    return loaded_modules
                # 使用正则表达式匹配 AIVK 模块
                pattern = re.compile(rf"^aivk[-_]{id}$", re.IGNORECASE)
                for mod in aivk_modules:
                    if pattern.match(mod["name"]):
                        result = importlib.import_module(mod["name"].replace("-", "_"))
                        loaded_modules.append(result)
                return loaded_modules if loaded_modules else None

    async def load(self, fs: AivkFS, id: str, aivk_modules: list[dict[str, str]]):
        """加载指定的 AIVK 模块"""
        loaded_module = await self.find(fs, id, aivk_modules)
        if not loaded_module:
            logger.warning(f"未找到 AIVK 模块: {id}")
            return

__all__ = ["AivkLoader"]