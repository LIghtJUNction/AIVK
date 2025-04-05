from pydantic import BaseModel
from pathlib import Path
import logging

from aivk.core.aivkroot import AivkRoot
from aivk.core.exceptions import AivkLoaderError

logger = logging.getLogger("aivk.loader.manager")

class AivkModuleManager(BaseModel):
    aivk : AivkRoot
    
    # 通过当前路径反推根目录
    @classmethod
    def from_current_path(cls) -> "AivkModuleManager":
        aivk_root = Path(__file__).resolve().parent.parent.parent
        # 例如：/path/to/aivk_root/modules/loader/loader.py
        # 反推根目录：/path/to/aivk_root
        logger.info(f"通过当前路径反推根目录: {aivk_root}")
        
        return cls(aivk=AivkRoot.mount(aivk_root))
    
    @classmethod
    def from_aivk_root(cls, aivk_root: Path) -> "AivkModuleManager":
        logger.info("Creating AivkModuleManager from AivkRoot")
        return cls(aivk=AivkRoot.mount(aivk_root))
    
    # 向上递归查找根目录（具有.aivk文件标记的）
    @classmethod
    def find_aivk_root(cls, start_path: Path) -> Path:
        """
        向上递归查找根目录（具有.aivk文件标记的）
        """
        current_path = start_path.resolve()
        while current_path != current_path.parent:
            if (current_path / ".aivk").exists():
                return cls.from_aivk_root(current_path)
            current_path = current_path.parent
        raise AivkLoaderError("无法找到AIVK根目录")
    
    
    