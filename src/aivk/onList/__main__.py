# -*- coding: utf-8 -*-
import builtins 
import importlib
import logging
from typing import Any, Dict, List, Set, Optional # Import Optional
# Remove unused Path import: from pathlib import Path
import importlib.metadata
from ..logger import setup_logging

setup_logging(style="panel")
logger = logging.getLogger("aivk.onList")

def _extract_aivk_module_name(pkg_name: Optional[str]) -> Optional[str]:
    """从包名中提取 aivk 模块名"""
    if not pkg_name:
        return None
    pkg_name_lower = pkg_name.lower()
    if pkg_name_lower == "aivk":
        return "aivk"
    if pkg_name_lower.startswith("aivk-"):
        module_part = pkg_name[len("aivk-"):]
        if module_part:
            return module_part
    return None

async def list(
    **kwargs: Dict[str, Any]
) -> List[str]:
    """列出已安装的 aivk 相关模块
    # ... (docstring) ...
    """
    logger.info("Scanning for installed aivk modules...")
    aivk_module_set: Set[str] = set()
    try:
        distributions = importlib.metadata.distributions()
        # 使用生成器表达式和辅助函数提取并过滤模块名
        module_names = (
            _extract_aivk_module_name(dist.metadata.get('Name'))
            for dist in distributions
        )
        # 更新集合，自动过滤掉 None 值
        aivk_module_set.update(name for name in module_names if name)

        aivk_modules = sorted(builtins.list(aivk_module_set))

        if aivk_modules:
            logger.info(f"Found aivk modules: {', '.join(aivk_modules)}")
        else:
            logger.warning("No aivk modules found.")

    except Exception as e:
        logger.error(f"Error scanning modules: {e}", exc_info=True)
        return []

    return aivk_modules

if __name__ == "__main__":
    # 直接运行时，执行加载
    import asyncio
    # Call the renamed function
    found_modules = asyncio.run(list())
    print(f"Detected modules: {found_modules}")